from __future__ import annotations

from .proposal_contracts import (
    METRIC_FORMATS,
    METRIC_OVERRIDE_FIELDS,
    PAGE_OVERRIDE_FIELDS,
    PAGE_SCOPED_TARGETS,
    TRACE_STYLES,
)
from .semantic_layer import SemanticLayer


class ProposalValidationError(ValueError):
    """Raised when a proposal violates semantic-layer constraints."""


class ProposalValidator:
    def __init__(self, semantic_layer: SemanticLayer) -> None:
        self.semantic_layer = semantic_layer

    def validate(self, proposal: dict) -> None:
        metrics = self.semantic_layer.metric_definitions()
        pages = self.semantic_layer.page_definitions()

        page = proposal.get("page")
        if page is not None and page not in pages:
            raise ProposalValidationError(f"Unknown page: {page}")

        target = proposal.get("target")
        after = proposal.get("after") or {}
        if not isinstance(after, dict):
            raise ProposalValidationError("Proposal 'after' payload must be an object")

        self._validate_metric_reference(after.get("metric"), metrics, field_name="metric")
        self._validate_metric_list(after.get("metrics"), metrics, field_name="metrics")

        if target in PAGE_SCOPED_TARGETS:
            if not page:
                raise ProposalValidationError("Page-scoped proposals must declare a page")
            self._validate_page_override(after, metrics)
            return

        if target == "semantic_layer":
            self._validate_metric_override(after, metrics)
            return

        raise ProposalValidationError(f"Unsupported proposal target: {target}")

    def _validate_page_override(self, after: dict, metrics: dict) -> None:
        unknown = set(after) - PAGE_OVERRIDE_FIELDS - {"metric", "metrics"}
        if unknown:
            raise ProposalValidationError(f"Unsupported page override fields: {', '.join(sorted(unknown))}")

        self._validate_metric_list(after.get("cards"), metrics, field_name="cards")
        self._validate_string_list(after.get("allowed_actions"), field_name="allowed_actions")
        self._validate_optional_string(after.get("label"), field_name="label")
        self._validate_optional_string(after.get("subtitle"), field_name="subtitle")
        self._validate_optional_string(after.get("trend_title_template"), field_name="trend_title_template")
        self._validate_optional_string(after.get("trend_x_title"), field_name="trend_x_title")
        self._validate_optional_string(after.get("insight_note"), field_name="insight_note")
        self._validate_optional_string(after.get("interaction_hint"), field_name="interaction_hint")
        self._validate_trace_style(after.get("current_trace_style"), field_name="current_trace_style")
        self._validate_trace_style(after.get("previous_trace_style"), field_name="previous_trace_style")

    def _validate_metric_override(self, after: dict, metrics: dict) -> None:
        metric_key = after.get("metric_key")
        self._validate_metric_reference(metric_key, metrics, field_name="metric_key")

        unknown = set(after) - METRIC_OVERRIDE_FIELDS - {"metric_key"}
        if unknown:
            raise ProposalValidationError(f"Unsupported metric override fields: {', '.join(sorted(unknown))}")

        self._validate_optional_string(after.get("label"), field_name="label")
        self._validate_optional_string(after.get("description"), field_name="description")
        self._validate_optional_string(after.get("aggregation"), field_name="aggregation")
        self._validate_optional_string(after.get("source_column"), field_name="source_column")
        self._validate_optional_string(after.get("formula_hint"), field_name="formula_hint")
        self._validate_string_list(after.get("dimensions"), field_name="dimensions")
        self._validate_string_list(after.get("allowed_granularities"), field_name="allowed_granularities")
        self._validate_string_list(after.get("allowed_comparisons"), field_name="allowed_comparisons")

        metric_format = after.get("format")
        if metric_format is not None and metric_format not in METRIC_FORMATS:
            raise ProposalValidationError(f"Unsupported metric format: {metric_format}")

    def _validate_metric_reference(self, metric_key: object, metrics: dict, field_name: str) -> None:
        if metric_key is None:
            return
        if not isinstance(metric_key, str):
            raise ProposalValidationError(f"Proposal '{field_name}' must be a string")
        if metric_key not in metrics:
            raise ProposalValidationError(f"Unknown metric in proposal '{field_name}': {metric_key}")

    def _validate_metric_list(self, metric_keys: object, metrics: dict, field_name: str) -> None:
        if metric_keys is None:
            return
        if not isinstance(metric_keys, list):
            raise ProposalValidationError(f"Proposal '{field_name}' must be a list")
        for metric_key in metric_keys:
            if not isinstance(metric_key, str):
                raise ProposalValidationError(f"Proposal '{field_name}' entries must be strings")
            if metric_key not in metrics:
                raise ProposalValidationError(f"Unknown metric in proposal '{field_name}': {metric_key}")

    def _validate_string_list(self, values: object, field_name: str) -> None:
        if values is None:
            return
        if not isinstance(values, list):
            raise ProposalValidationError(f"Proposal '{field_name}' must be a list")
        if not all(isinstance(value, str) for value in values):
            raise ProposalValidationError(f"Proposal '{field_name}' entries must be strings")

    def _validate_optional_string(self, value: object, field_name: str) -> None:
        if value is None:
            return
        if not isinstance(value, str):
            raise ProposalValidationError(f"Proposal '{field_name}' must be a string")

    def _validate_trace_style(self, value: object, field_name: str) -> None:
        if value is None:
            return
        if not isinstance(value, str) or value not in TRACE_STYLES:
            raise ProposalValidationError(
                f"Proposal '{field_name}' must be one of: {', '.join(sorted(TRACE_STYLES))}"
            )
