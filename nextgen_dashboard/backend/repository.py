from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd

from .data_source import (
    DashboardDataSource,
    DashboardSettings,
    DataSourceError,
)


@dataclass(slots=True)
class RepositoryHealth:
    status: str
    message: str


class SalesRepository:
    def __init__(self) -> None:
        self.settings = DashboardSettings.from_env()
        self.data_source = DashboardDataSource(self.settings)
        self._sales_cache: pd.DataFrame | None = None
        self._filter_metadata_cache: dict[str, object] | None = None
        self._first_purchase_cache: pd.Series | None = None

    def health(self) -> RepositoryHealth:
        try:
            return RepositoryHealth(
                status="ok", message=self.data_source.health_check()
            )
        except Exception as exc:  # pragma: no cover - defensive runtime guard
            return RepositoryHealth(status="error", message=str(exc))

    def load_sales_model(self, force_refresh: bool = False) -> pd.DataFrame:
        if self._sales_cache is not None and not force_refresh:
            return self._sales_cache

        sales_df = self.data_source.load_sales_model()
        sales_df.columns = [col.lower() for col in sales_df.columns]
        sales_df["order_date"] = pd.to_datetime(sales_df["order_date"], errors="coerce")
        sales_df = sales_df.dropna(subset=["order_date"]).copy()
        sales_df["order_date"] = sales_df["order_date"].dt.tz_localize(None)
        sales_df["order_day"] = sales_df["order_date"].dt.normalize()

        for numeric_col in ("sales_amount", "quantity", "unit_price"):
            if numeric_col in sales_df.columns:
                sales_df[numeric_col] = pd.to_numeric(
                    sales_df[numeric_col], errors="coerce"
                ).fillna(0.0)

        self._sales_cache = sales_df
        self._filter_metadata_cache = None
        self._first_purchase_cache = None
        return self._sales_cache

    def filter_frame_by_date(
        self,
        frame: pd.DataFrame,
        start_date: pd.Timestamp | None,
        end_date: pd.Timestamp | None,
    ) -> pd.DataFrame:
        scoped = frame
        if start_date is not None:
            scoped = scoped[
                scoped["order_day"] >= pd.Timestamp(start_date).normalize()
            ]
        if end_date is not None:
            scoped = scoped[
                scoped["order_day"] <= pd.Timestamp(end_date).normalize()
            ]
        return scoped

    def filter_sales(
        self,
        start_date: pd.Timestamp | None,
        end_date: pd.Timestamp | None,
        categories: list[str] | None,
        cities: list[str] | None,
    ) -> pd.DataFrame:
        scoped = self.load_sales_model()

        if categories:
            scoped = scoped[scoped["category"].isin(categories)]
        if cities:
            scoped = scoped[scoped["city"].isin(cities)]

        return self.filter_frame_by_date(scoped, start_date, end_date)

    def customer_first_purchase(self) -> pd.Series:
        if self._first_purchase_cache is not None:
            return self._first_purchase_cache

        sales_df = self.load_sales_model()
        self._first_purchase_cache = sales_df.groupby("customer_id")["order_day"].min()
        return self._first_purchase_cache

    def filter_metadata(self) -> dict[str, object]:
        if self._filter_metadata_cache is not None:
            return dict(self._filter_metadata_cache)

        sales_df = self.load_sales_model()
        min_ts = sales_df["order_day"].min()
        max_ts = sales_df["order_day"].max()
        max_date = max_ts.date()

        default_start = (max_ts - pd.Timedelta(days=365)).date()
        if default_start < min_ts.date():
            default_start = min_ts.date()

        categories = (
            sorted(sales_df["category"].dropna().astype(str).unique().tolist())
            if "category" in sales_df.columns
            else []
        )
        cities = (
            sorted(sales_df["city"].dropna().astype(str).unique().tolist())
            if "city" in sales_df.columns
            else []
        )

        self._filter_metadata_cache = {
            "min_date": min_ts.date().isoformat(),
            "max_date": max_date.isoformat(),
            "default_start_date": default_start.isoformat(),
            "default_end_date": max_date.isoformat(),
            "categories": categories,
            "cities": cities,
        }
        return dict(self._filter_metadata_cache)

    def validate_date_range(
        self, start: date | None, end: date | None
    ) -> tuple[pd.Timestamp, pd.Timestamp]:
        meta = self.filter_metadata()
        min_date = pd.Timestamp(meta["min_date"])
        max_date = pd.Timestamp(meta["max_date"])
        start_ts = pd.Timestamp(start) if start is not None else min_date
        end_ts = pd.Timestamp(end) if end is not None else max_date

        if start_ts < min_date:
            start_ts = min_date
        if end_ts > max_date:
            end_ts = max_date
        if start_ts > end_ts:
            raise DataSourceError("start_date must be less than or equal to end_date.")

        return start_ts.normalize(), end_ts.normalize()
