from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from .models import Granularity, KpiCard, TrendPoint

Aggregator = Callable[[pd.DataFrame], float]


def safe_pct(current: float, previous: float) -> float:
    if previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100.0


def fmt_currency(value: float) -> str:
    return f"{value:,.2f}"


def fmt_number(value: float) -> str:
    return f"{value:,.0f}"


def fmt_decimal(value: float) -> str:
    return f"{value:,.2f}"


def fmt_pct(value: float) -> str:
    return f"{value:.2f}%"


def make_card(
    key: str,
    title: str,
    value: float,
    previous_value: float,
    formatter: Callable[[float], str],
) -> KpiCard:
    delta = safe_pct(value, previous_value)
    sign = "+" if delta > 0 else ""
    return KpiCard(
        key=key,
        title=title,
        value=float(value),
        previous_value=float(previous_value),
        delta_pct=float(delta),
        formatted_value=formatter(float(value)),
        formatted_previous_value=formatter(float(previous_value)),
        delta_label=f"{sign}{delta:.2f}%",
    )


def period_freq(granularity: Granularity) -> str:
    return {"Day": "D", "Month": "M", "Quarter": "Q", "Year": "Y"}[granularity]


def date_series(df: pd.DataFrame) -> pd.Series:
    if "order_day" in df.columns:
        return pd.to_datetime(df["order_day"], errors="coerce").dt.normalize()
    return pd.to_datetime(df["order_date"], errors="coerce").dt.normalize()


def window_df(df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    if df.empty:
        return df.iloc[0:0].copy()
    start = pd.Timestamp(start).normalize()
    end = pd.Timestamp(end).normalize()
    dates = date_series(df)
    return df[(dates >= start) & (dates <= end)].copy()


def range_with_previous(
    scoped_df: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Timestamp, pd.Timestamp]:
    current_df = window_df(scoped_df, start_date, end_date)
    days = int((end_date - start_date).days) + 1
    previous_end = start_date - pd.Timedelta(days=1)
    previous_start = previous_end - pd.Timedelta(days=max(days - 1, 0))
    previous_df = window_df(scoped_df, previous_start, previous_end)
    return current_df, previous_df, previous_start, previous_end


def format_period_label(period: pd.Period, granularity: Granularity) -> str:
    dt = period.start_time
    if granularity == "Day":
        return dt.strftime("%d %b %Y")
    if granularity == "Month":
        return dt.strftime("%b %Y")
    if granularity == "Quarter":
        quarter = ((dt.month - 1) // 3) + 1
        return f"{dt.year}Q{quarter}"
    return str(dt.year)


def period_bounds_from_key(
    period_key: str,
    granularity: Granularity,
) -> tuple[pd.Timestamp, pd.Timestamp, str]:
    period = pd.Period(period_key, freq=period_freq(granularity))
    start = period.start_time.normalize()
    end = period.end_time.normalize()
    return start, end, format_period_label(period, granularity)


def aligned_previous_window(
    period: pd.Period,
    current_start: pd.Timestamp,
    current_end: pd.Timestamp,
) -> tuple[pd.Timestamp, pd.Timestamp]:
    period_start = period.start_time.normalize()
    period_end = period.end_time.normalize()
    previous_period = period - 1
    previous_start = previous_period.start_time.normalize()
    previous_end = previous_period.end_time.normalize()

    if current_start == period_start and current_end == period_end:
        return previous_start, previous_end

    start_offset = int((current_start - period_start).days)
    end_offset = int((current_end - period_start).days)
    aligned_start = previous_start + pd.Timedelta(days=start_offset)
    aligned_end = min(previous_start + pd.Timedelta(days=end_offset), previous_end)
    return aligned_start, aligned_end


def _range_sum_from_daily_cumsum(
    daily_cumsum: pd.Series,
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> float:
    if daily_cumsum.empty:
        return 0.0
    start_ts = pd.Timestamp(start).normalize()
    end_ts = pd.Timestamp(end).normalize()
    if end_ts < start_ts:
        return 0.0
    end_total = float(daily_cumsum.loc[end_ts]) if end_ts in daily_cumsum.index else 0.0
    previous_day = start_ts - pd.Timedelta(days=1)
    previous_total = float(daily_cumsum.loc[previous_day]) if previous_day in daily_cumsum.index else 0.0
    return end_total - previous_total


def build_aligned_trend(
    scoped_df: pd.DataFrame,
    current_df: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    granularity: Granularity,
    aggregator: Aggregator,
    optimized_sum_col: str | None = None,
) -> list[TrendPoint]:
    if current_df.empty:
        return []

    daily_cumsum = None
    if optimized_sum_col and optimized_sum_col in scoped_df.columns:
        daily_values = (
            scoped_df.assign(day=date_series(scoped_df))
            .groupby("day")[optimized_sum_col]
            .sum()
            .sort_index()
            .astype(float)
        )
        if not daily_values.empty:
            full_index = pd.date_range(daily_values.index.min(), daily_values.index.max(), freq="D")
            daily_cumsum = daily_values.reindex(full_index, fill_value=0.0).cumsum()

    periods = pd.PeriodIndex(date_series(current_df).dt.to_period(period_freq(granularity)).unique()).sort_values()
    trend: list[TrendPoint] = []
    for period in periods:
        period_start = max(period.start_time.normalize(), start_date)
        period_end = min(period.end_time.normalize(), end_date)
        previous_start, previous_end = aligned_previous_window(period, period_start, period_end)

        if daily_cumsum is not None:
            current_value = _range_sum_from_daily_cumsum(daily_cumsum, period_start, period_end)
            previous_value = _range_sum_from_daily_cumsum(daily_cumsum, previous_start, previous_end)
        else:
            current_value = float(aggregator(window_df(scoped_df, period_start, period_end)))
            previous_value = float(aggregator(window_df(scoped_df, previous_start, previous_end)))
        trend.append(
            TrendPoint(
                period_key=str(period),
                period_label=format_period_label(period, granularity),
                current_value=current_value,
                previous_value=previous_value,
                delta_pct=safe_pct(current_value, previous_value),
            )
        )
    return trend


def build_daily_trend_for_period_comparison(
    scoped_df: pd.DataFrame,
    current_start: pd.Timestamp,
    current_end: pd.Timestamp,
    previous_start: pd.Timestamp,
) -> list[TrendPoint]:
    if scoped_df.empty:
        return []

    by_day = (
        scoped_df.assign(day=date_series(scoped_df))
        .groupby("day")["sales_amount"]
        .sum()
    )

    days = int((current_end - current_start).days) + 1
    trend: list[TrendPoint] = []
    for offset in range(days):
        current_day = current_start + pd.Timedelta(days=offset)
        previous_day = previous_start + pd.Timedelta(days=offset)
        current_value = float(by_day.get(current_day, 0.0))
        previous_value = float(by_day.get(previous_day, 0.0))
        trend.append(
            TrendPoint(
                period_key=current_day.date().isoformat(),
                period_label=current_day.strftime("%d %b"),
                current_value=current_value,
                previous_value=previous_value,
                delta_pct=safe_pct(current_value, previous_value),
            )
        )
    return trend
