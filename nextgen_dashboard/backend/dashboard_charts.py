from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from .analytics_helpers import safe_pct
from .models import BreakdownChartPayload, BreakdownPoint
from .statistical_analytics import build_pareto_points


MetricFn = Callable[[pd.DataFrame], float]


def group_metric_map(
    dataframe: pd.DataFrame, group_col: str, metric_fn: MetricFn
) -> dict[str, float]:
    if dataframe.empty or group_col not in dataframe.columns:
        return {}
    scoped = dataframe.dropna(subset=[group_col])
    return {
        str(raw_label): float(metric_fn(frame))
        for raw_label, frame in scoped.groupby(group_col, sort=False)
    }


def build_breakdown_chart(
    title: str,
    x_title: str,
    y_title: str,
    current_df: pd.DataFrame,
    previous_df: pd.DataFrame,
    group_col: str,
    metric_fn: MetricFn,
    metric_format: str,
    limit: int = 6,
    current_trace_style: str = "bar",
    previous_trace_style: str = "bar",
    label_transform: Callable[[str], str] | None = None,
    filter_key: str | None = None,
) -> BreakdownChartPayload | None:
    current_map = group_metric_map(current_df, group_col, metric_fn)
    previous_map = group_metric_map(previous_df, group_col, metric_fn)
    labels = sorted(
        set(current_map) | set(previous_map),
        key=lambda label: (current_map.get(label, 0.0), previous_map.get(label, 0.0)),
        reverse=True,
    )[:limit]
    if not labels:
        return None
    return BreakdownChartPayload(
        title=title,
        x_title=x_title,
        y_title=y_title,
        metric_format=metric_format,
        current_trace_style=current_trace_style,
        previous_trace_style=previous_trace_style,
        filter_key=filter_key if filter_key in {"category", "city"} else None,
        points=[
            BreakdownPoint(
                label=label_transform(label) if label_transform else label,
                raw_label=label,
                current_value=float(current_map.get(label, 0.0)),
                previous_value=float(previous_map.get(label, 0.0)),
                delta_pct=safe_pct(
                    current_map.get(label, 0.0), previous_map.get(label, 0.0)
                ),
            )
            for label in labels
        ],
    )


def build_pareto_breakdown_chart(
    title: str,
    x_title: str,
    y_title: str,
    current_df: pd.DataFrame,
    previous_df: pd.DataFrame,
    group_col: str,
    metric_format: str,
    limit: int = 8,
    label_transform: Callable[[str], str] | None = None,
    filter_key: str | None = None,
    interaction_type: str | None = None,
    interaction_key: str | None = None,
    interaction_label: str | None = None,
) -> BreakdownChartPayload | None:
    points = build_pareto_points(
        current_df=current_df,
        previous_df=previous_df,
        group_col=group_col,
        limit=limit,
        label_transform=label_transform,
    )
    if not points:
        return None
    return BreakdownChartPayload(
        title=title,
        x_title=x_title,
        y_title=y_title,
        metric_format=metric_format,
        analysis_mode="pareto",
        current_series_name="Current Net Sales",
        cumulative_series_name="Cumulative Share",
        cumulative_y_title="Cumulative Share",
        current_trace_style="bar",
        filter_key=filter_key if filter_key in {"category", "city"} else None,
        interaction_type=interaction_type,
        interaction_key=interaction_key,
        interaction_label=interaction_label,
        points=points,
    )
