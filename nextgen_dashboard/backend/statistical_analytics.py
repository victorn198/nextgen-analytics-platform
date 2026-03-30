from __future__ import annotations

from collections.abc import Callable, Iterable

import numpy as np
import pandas as pd

from .analytics_helpers import safe_pct
from .models import BreakdownPoint, TrendPoint

LabelTransform = Callable[[str], str]


def _scaled_quantile_scores(series: pd.Series, higher_is_better: bool, bins: int = 5) -> pd.Series:
    series = pd.to_numeric(series, errors="coerce").fillna(0.0)
    if series.empty:
        return pd.Series(dtype="int64")
    if series.nunique(dropna=True) <= 1:
        return pd.Series(3, index=series.index, dtype="int64")

    q = max(2, min(bins, int(series.nunique(dropna=True)), len(series)))
    ranked = series.rank(method="first", ascending=True)
    raw_scores = pd.qcut(ranked, q=q, labels=False, duplicates="drop").astype("float64") + 1.0

    if not higher_is_better:
        raw_scores = raw_scores.max() + 1.0 - raw_scores

    if q == 1:
        scaled = pd.Series(3.0, index=series.index)
    else:
        scaled = 1.0 + ((raw_scores - 1.0) * 4.0 / float(q - 1))

    return scaled.round().clip(lower=1, upper=5).astype("int64")


def abc_class(cumulative_pct: float) -> str:
    if cumulative_pct <= 80.0:
        return "A"
    if cumulative_pct <= 95.0:
        return "B"
    return "C"


def build_pareto_points(
    current_df: pd.DataFrame,
    previous_df: pd.DataFrame,
    group_col: str,
    value_col: str = "sales_amount",
    limit: int = 8,
    label_transform: LabelTransform | None = None,
) -> list[BreakdownPoint]:
    if current_df.empty or group_col not in current_df.columns or value_col not in current_df.columns:
        return []

    current_series = (
        current_df.dropna(subset=[group_col])
        .groupby(group_col)[value_col]
        .sum()
        .sort_values(ascending=False)
    )
    if current_series.empty:
        return []

    previous_series = (
        previous_df.dropna(subset=[group_col])
        .groupby(group_col)[value_col]
        .sum()
        if not previous_df.empty and group_col in previous_df.columns and value_col in previous_df.columns
        else pd.Series(dtype="float64")
    )

    ranked = current_series.head(limit)
    total_current = float(current_series.sum())
    running = 0.0
    points: list[BreakdownPoint] = []

    for raw_label, current_value in ranked.items():
        current_value = float(current_value)
        previous_value = float(previous_series.get(raw_label, 0.0))
        share_pct = (current_value / total_current * 100.0) if total_current else 0.0
        running += share_pct
        label = str(raw_label)
        points.append(
            BreakdownPoint(
                label=label_transform(label) if label_transform else label,
                raw_label=label,
                current_value=current_value,
                previous_value=previous_value,
                delta_pct=safe_pct(current_value, previous_value),
                share_pct=share_pct,
                cumulative_pct=running,
                segment_class=abc_class(running),
            )
        )

    return points


def build_rfm_customer_frame(current_df: pd.DataFrame, end_date: pd.Timestamp) -> pd.DataFrame:
    if current_df.empty:
        return pd.DataFrame(
            columns=[
                "customer_id",
                "customer_name",
                "city",
                "last_order_day",
                "orders",
                "revenue",
                "recency_days",
                "r_score",
                "f_score",
                "m_score",
                "segment",
            ]
        )

    working = current_df.dropna(subset=["customer_id", "order_day"])
    grouped = (
        working.groupby("customer_id", sort=False)
        .agg(
            customer_name=("customer_name", "first"),
            last_order_day=("order_day", "max"),
            orders=("order_id", "nunique"),
            revenue=("sales_amount", "sum"),
        )
        .reset_index()
    )
    if grouped.empty:
        return grouped

    city_counts = (
        working.dropna(subset=["city"])
        .groupby(["customer_id", "city"], sort=False)
        .size()
        .reset_index(name="city_count")
    )
    if city_counts.empty:
        grouped["city"] = "Unknown"
    else:
        dominant_city = (
            city_counts.sort_values(["customer_id", "city_count", "city"], ascending=[True, False, True])
            .drop_duplicates(subset=["customer_id"], keep="first")
            .set_index("customer_id")["city"]
        )
        grouped["city"] = grouped["customer_id"].map(dominant_city).fillna("Unknown")

    normalized_end = pd.Timestamp(end_date).normalize()
    grouped["recency_days"] = (normalized_end - pd.to_datetime(grouped["last_order_day"]).dt.normalize()).dt.days.astype(int)
    grouped["r_score"] = _scaled_quantile_scores(grouped["recency_days"], higher_is_better=False)
    grouped["f_score"] = _scaled_quantile_scores(grouped["orders"], higher_is_better=True)
    grouped["m_score"] = _scaled_quantile_scores(grouped["revenue"], higher_is_better=True)

    r_score = grouped["r_score"]
    f_score = grouped["f_score"]
    m_score = grouped["m_score"]
    grouped["segment"] = np.select(
        [
            (r_score >= 4) & (f_score >= 4) & (m_score >= 4),
            (r_score >= 3) & (f_score >= 3) & (m_score >= 3),
            (r_score >= 4) & ((f_score >= 2) | (m_score >= 2)),
            (r_score <= 2) & ((f_score >= 3) | (m_score >= 3)),
            (r_score <= 2) & (f_score <= 2) & (m_score <= 2),
        ],
        [
            "Champions",
            "Loyal",
            "Potential Loyalists",
            "At Risk",
            "Hibernating",
        ],
        default="Needs Attention",
    )
    return grouped


def build_rfm_segment_summary(current_df: pd.DataFrame, end_date: pd.Timestamp) -> pd.DataFrame:
    grouped = build_rfm_customer_frame(current_df, end_date)
    if grouped.empty:
        return pd.DataFrame(
            columns=[
                "segment",
                "customers",
                "orders",
                "revenue",
                "avg_orders_per_customer",
                "avg_revenue_per_customer",
                "share_pct",
                "median_recency_days",
            ]
        )

    total_revenue = float(grouped["revenue"].sum())
    summary = (
        grouped.groupby("segment")
        .agg(
            customers=("customer_id", "nunique"),
            orders=("orders", "sum"),
            revenue=("revenue", "sum"),
            avg_orders_per_customer=("orders", "mean"),
            avg_revenue_per_customer=("revenue", "mean"),
            median_recency_days=("recency_days", "median"),
        )
        .reset_index()
    )
    summary["share_pct"] = np.where(total_revenue > 0, summary["revenue"] / total_revenue * 100.0, 0.0)

    segment_order = {
        "Champions": 0,
        "Loyal": 1,
        "Potential Loyalists": 2,
        "Needs Attention": 3,
        "At Risk": 4,
        "Hibernating": 5,
    }
    summary["segment_order"] = summary["segment"].map(segment_order).fillna(999)
    summary = summary.sort_values(["segment_order", "revenue"], ascending=[True, False]).drop(columns=["segment_order"])
    return summary


def annotate_trend_anomalies(
    trend: Iterable[TrendPoint],
    lookback: int = 5,
    threshold: float = 3.0,
) -> list[TrendPoint]:
    trend_points = list(trend)
    if len(trend_points) < lookback + 1:
        return trend_points

    values = pd.Series([float(point.current_value) for point in trend_points], dtype="float64")
    for idx, point in enumerate(trend_points):
        point.is_anomaly = False
        point.anomaly_score = None
        point.baseline_value = None
        if idx < lookback:
            continue

        history = values.iloc[max(0, idx - lookback):idx]
        if history.empty:
            continue

        baseline = float(history.median())
        mad = float(np.median(np.abs(history - baseline)))

        if mad > 0:
            score = 0.6745 * (values.iloc[idx] - baseline) / mad
        else:
            std = float(history.std(ddof=0))
            if std <= 0:
                continue
            score = (values.iloc[idx] - baseline) / std

        point.baseline_value = baseline
        point.anomaly_score = float(score)
        point.is_anomaly = bool(abs(score) >= threshold)

    return trend_points


def detect_structural_shifts(
    trend: Iterable[TrendPoint],
    window: int = 3,
    threshold: float = 1.75,
) -> list[dict[str, float | str]]:
    trend_points = [point for point in trend if not point.is_projection]
    if len(trend_points) < (window * 2) + 1:
        return []

    values = np.array([float(point.current_value) for point in trend_points], dtype=float)
    signals: list[dict[str, float | str]] = []
    last_kept_idx = -window

    for idx in range(window, len(values) - window + 1):
        before = values[idx - window:idx]
        after = values[idx:idx + window]
        if len(after) < window:
            continue
        pooled = np.concatenate([before, after])
        pooled_std = float(np.std(pooled, ddof=0))
        if pooled_std <= 0:
            continue
        before_mean = float(np.mean(before))
        after_mean = float(np.mean(after))
        score = abs(after_mean - before_mean) / pooled_std
        if score < threshold:
            continue
        if idx - last_kept_idx < window:
            if signals and score > float(signals[-1]["score"]):
                signals.pop()
            else:
                continue
        direction = "Upward shift" if after_mean > before_mean else "Downward shift"
        pivot_point = trend_points[idx]
        signals.append(
            {
                "period_label": pivot_point.period_label,
                "period_key": pivot_point.period_key,
                "before_mean": before_mean,
                "after_mean": after_mean,
                "score": float(score),
                "direction": direction,
            }
        )
        last_kept_idx = idx

    return signals
