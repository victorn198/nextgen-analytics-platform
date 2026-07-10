from __future__ import annotations

import pandas as pd

from nextgen_dashboard.backend.dashboard_charts import build_breakdown_chart
from nextgen_dashboard.backend.retention_analytics import build_retention_snapshot


def test_build_breakdown_chart_compares_current_and_previous_groups() -> None:
    current = pd.DataFrame(
        {"city": ["London", "London", "Paris"], "sales_amount": [20.0, 10.0, 5.0]}
    )
    previous = pd.DataFrame(
        {"city": ["London", "Berlin"], "sales_amount": [15.0, 8.0]}
    )

    chart = build_breakdown_chart(
        title="Sales by city",
        x_title="City",
        y_title="Sales",
        current_df=current,
        previous_df=previous,
        group_col="city",
        metric_fn=lambda frame: float(frame["sales_amount"].sum()),
        metric_format="currency",
    )

    assert chart is not None
    assert [point.raw_label for point in chart.points] == ["London", "Paris", "Berlin"]
    assert chart.points[0].current_value == 30.0
    assert chart.points[0].previous_value == 15.0


def test_retention_snapshot_builds_only_mature_cells() -> None:
    dataframe = pd.DataFrame(
        {
            "customer_id": ["a", "a", "b", "b", "c"],
            "order_day": pd.to_datetime(
                ["2024-01-10", "2024-02-10", "2024-01-15", "2024-03-15", "2024-03-20"]
            ),
        }
    )

    snapshot = build_retention_snapshot(
        dataframe,
        pd.Timestamp("2024-01-01"),
        pd.Timestamp("2024-03-31"),
    )

    assert snapshot["latest_full_cohort_size"] == 1.0
    assert snapshot["retention"][1] == 50.0
    assert snapshot["heatmap"] is not None
    assert snapshot["heatmap"].z_values[0][1] is None
    assert snapshot["heatmap"].z_values[-1][1] == 50.0
