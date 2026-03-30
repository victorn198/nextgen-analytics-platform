from __future__ import annotations

PAGE_SCOPED_TARGETS = {"dashboard", "page"}
PAGE_OVERRIDE_FIELDS = {
    "label",
    "subtitle",
    "trend_title_template",
    "trend_x_title",
    "current_trace_style",
    "previous_trace_style",
    "cards",
    "allowed_actions",
    "insight_note",
    "interaction_hint",
}
METRIC_OVERRIDE_FIELDS = {
    "label",
    "description",
    "format",
    "aggregation",
    "source_column",
    "formula_hint",
    "dimensions",
    "allowed_granularities",
    "allowed_comparisons",
}
TRACE_STYLES = {"line", "bar"}
METRIC_FORMATS = {"currency", "number", "percent"}
