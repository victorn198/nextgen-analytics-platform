from __future__ import annotations

from typing import Any

import pandas as pd

from .analytics_helpers import fmt_number, fmt_pct
from .models import HeatmapPayload


def build_retention_snapshot(
    scoped_df: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    max_age: int = 6,
) -> dict[str, Any]:
    activity = scoped_df.dropna(subset=["customer_id", "order_day"])[["customer_id", "order_day"]].copy()
    if activity.empty:
        return _empty_snapshot(max_age)

    activity["order_month"] = activity["order_day"].dt.to_period("M").dt.to_timestamp()
    activity = activity.drop_duplicates(subset=["customer_id", "order_month"])
    cohort_map = activity.groupby("customer_id")["order_month"].min()
    activity["cohort_month"] = activity["customer_id"].map(cohort_map)

    cohort_start = _month_start(start_date)
    cohort_end = _month_start(end_date)
    activity = activity[
        (activity["cohort_month"] >= cohort_start)
        & (activity["cohort_month"] <= cohort_end)
        & (activity["order_month"] <= cohort_end)
    ].copy()
    if activity.empty:
        return _empty_snapshot_with_window(max_age, cohort_start, cohort_end)

    activity["cohort_age"] = (
        (activity["order_month"].dt.year - activity["cohort_month"].dt.year) * 12
        + (activity["order_month"].dt.month - activity["cohort_month"].dt.month)
    )
    activity = activity[(activity["cohort_age"] >= 0) & (activity["cohort_age"] <= max_age)]
    if activity.empty:
        return _empty_snapshot_with_window(max_age, cohort_start, cohort_end)

    cohort_sizes = (
        activity[activity["cohort_age"] == 0]
        .groupby("cohort_month")["customer_id"]
        .nunique()
        .sort_index()
        .astype(float)
    )
    if cohort_sizes.empty:
        return _empty_snapshot_with_window(max_age, cohort_start, cohort_end)

    counts = (
        activity.groupby(["cohort_month", "cohort_age"])["customer_id"]
        .nunique()
        .unstack(fill_value=0)
        .reindex(
            index=cohort_sizes.index,
            columns=list(range(max_age + 1)),
            fill_value=0,
        )
        .astype(float)
    )

    def weighted_retention(age: int) -> float:
        eligible = [
            cohort
            for cohort in cohort_sizes.index
            if cohort + pd.DateOffset(months=age) <= cohort_end
        ]
        if not eligible:
            return 0.0
        denominator = float(cohort_sizes.loc[eligible].sum())
        numerator = float(counts.loc[eligible, age].sum())
        return (numerator / denominator * 100.0) if denominator else 0.0

    curve = {
        age: (100.0 if age == 0 else weighted_retention(age))
        for age in range(max_age + 1)
    }
    retention = {
        age: weighted_retention(age) for age in range(1, min(max_age, 3) + 1)
    }
    latest_full_month = _last_closed_cohort_month(end_date)
    latest_full_size = (
        float(cohort_sizes.loc[latest_full_month])
        if latest_full_month is not None and latest_full_month in cohort_sizes.index
        else 0.0
    )

    detail_rows: list[dict[str, str]] = []
    y_labels: list[str] = []
    z_values: list[list[float | None]] = []
    for cohort in sorted(cohort_sizes.index.tolist(), reverse=True):
        cohort_size = float(cohort_sizes.loc[cohort])
        y_labels.append(pd.Timestamp(cohort).strftime("%b %Y"))
        row_values: list[float | None] = []
        for age in range(max_age + 1):
            if cohort + pd.DateOffset(months=age) > cohort_end:
                row_values.append(None)
                continue
            numerator = float(counts.loc[cohort, age])
            row_values.append((numerator / cohort_size * 100.0) if cohort_size else 0.0)
        z_values.append(row_values)
        detail_rows.append(
            {
                "cohort": pd.Timestamp(cohort).strftime("%b %Y"),
                "size": fmt_number(cohort_size),
                "m1": fmt_pct(row_values[1]) if row_values[1] is not None else "-",
                "m2": fmt_pct(row_values[2]) if row_values[2] is not None else "-",
                "m3": fmt_pct(row_values[3]) if row_values[3] is not None else "-",
            }
        )

    return {
        "heatmap": HeatmapPayload(
            title="Retention Cohort Heatmap",
            x_labels=[f"M{age}" for age in range(max_age + 1)],
            y_labels=y_labels,
            z_values=z_values,
            metric_format="percent",
        ),
        "cohort_sizes": cohort_sizes,
        "counts": counts,
        "latest_full_cohort_size": latest_full_size,
        "retention": retention,
        "curve": curve,
        "detail_rows": detail_rows[:6],
        "cohort_start": cohort_start,
        "cohort_end": cohort_end,
    }


def _empty_snapshot(max_age: int) -> dict[str, Any]:
    return {
        "heatmap": None,
        "cohort_sizes": pd.Series(dtype="float64"),
        "counts": pd.DataFrame(columns=list(range(max_age + 1))),
        "latest_full_cohort_size": 0.0,
        "retention": {age: 0.0 for age in range(1, min(max_age, 3) + 1)},
        "curve": {age: 0.0 for age in range(max_age + 1)},
        "detail_rows": [],
        "cohort_start": None,
        "cohort_end": None,
    }


def _empty_snapshot_with_window(
    max_age: int, cohort_start: pd.Timestamp, cohort_end: pd.Timestamp
) -> dict[str, Any]:
    snapshot = _empty_snapshot(max_age)
    snapshot["cohort_start"] = cohort_start
    snapshot["cohort_end"] = cohort_end
    return snapshot


def _month_start(value: pd.Timestamp) -> pd.Timestamp:
    return pd.Timestamp(value).to_period("M").to_timestamp()


def _last_closed_cohort_month(end_date: pd.Timestamp) -> pd.Timestamp:
    end_ts = pd.Timestamp(end_date).normalize()
    cohort_month = _month_start(end_ts)
    if end_ts < cohort_month + pd.offsets.MonthEnd(0):
        cohort_month -= pd.DateOffset(months=1)
    return pd.Timestamp(cohort_month).normalize()
