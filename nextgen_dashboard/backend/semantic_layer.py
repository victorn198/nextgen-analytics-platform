from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from .proposal_contracts import METRIC_FORMATS, TRACE_STYLES


class SemanticLayerError(RuntimeError):
    """Raised when the semantic layer configuration is invalid."""


class SemanticLayer:
    def __init__(self, semantic_root: Path | None = None, agent_data_root: Path | None = None) -> None:
        app_root = Path(__file__).resolve().parents[1]
        self.semantic_root = semantic_root or app_root / "semantic"
        self.agent_data_root = agent_data_root or app_root / "agent_data"
        self.page_overrides_path = self.agent_data_root / "page_overrides.json"
        self.metric_overrides_path = self.agent_data_root / "metric_overrides.json"
        self._cache: dict[str, Any] | None = None

    def load(self, force_refresh: bool = False) -> dict[str, Any]:
        if self._cache is not None and not force_refresh:
            return self._cache

        metrics = self._merge_metric_overrides(self._read_yaml("metrics.yml"))
        pages = self._merge_page_overrides(self._read_yaml("pages.yml"))
        payload = {"metrics": metrics, "pages": pages}
        self._validate(payload)
        self._cache = payload
        return payload

    def metric_definitions(self) -> dict[str, Any]:
        return self.load()["metrics"]["metrics"]

    def page_definitions(self) -> dict[str, Any]:
        return self.load()["pages"]["pages"]

    def refresh(self) -> dict[str, Any]:
        self._cache = None
        return self.load(force_refresh=True)

    def preview_page_override(self, page_key: str, override: dict[str, Any]) -> dict[str, Any]:
        metrics = self._merge_metric_overrides(self._read_yaml("metrics.yml"))
        pages = self._merge_page_overrides(self._read_yaml("pages.yml"), extra_overrides={page_key: override})
        payload = {"metrics": metrics, "pages": pages}
        self._validate(payload)
        return payload["pages"]["pages"][page_key]

    def preview_metric_override(self, metric_key: str, override: dict[str, Any]) -> dict[str, Any]:
        metrics = self._merge_metric_overrides(self._read_yaml("metrics.yml"), extra_overrides={metric_key: override})
        pages = self._merge_page_overrides(self._read_yaml("pages.yml"))
        payload = {"metrics": metrics, "pages": pages}
        self._validate(payload)
        return payload["metrics"]["metrics"][metric_key]

    def read_page_overrides(self) -> dict[str, Any]:
        return self._read_json_map(self.page_overrides_path, root_key="pages")

    def read_metric_overrides(self) -> dict[str, Any]:
        return self._read_json_map(self.metric_overrides_path, root_key="metrics")

    def _read_json_map(self, path: Path, root_key: str) -> dict[str, Any]:
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, dict):
            raise SemanticLayerError(f"Invalid override payload: {path}")
        root = payload.get(root_key, {})
        if not isinstance(root, dict):
            raise SemanticLayerError(f"{path.name} must contain a {root_key} map")
        return root

    def _merge_page_overrides(self, pages_payload: dict[str, Any], extra_overrides: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = {**pages_payload, "pages": {**pages_payload.get("pages", {})}}
        overrides = self.read_page_overrides()
        if extra_overrides:
            overrides = {**overrides, **extra_overrides}
        for page_key, override in overrides.items():
            if page_key not in payload["pages"]:
                continue
            if not isinstance(override, dict):
                raise SemanticLayerError(f"Override for page '{page_key}' must be a mapping")
            payload["pages"][page_key] = {**payload["pages"][page_key], **override}
        return payload

    def _merge_metric_overrides(self, metrics_payload: dict[str, Any], extra_overrides: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = {**metrics_payload, "metrics": {**metrics_payload.get("metrics", {})}}
        overrides = self.read_metric_overrides()
        if extra_overrides:
            overrides = {**overrides, **extra_overrides}
        for metric_key, override in overrides.items():
            if metric_key not in payload["metrics"]:
                continue
            if not isinstance(override, dict):
                raise SemanticLayerError(f"Override for metric '{metric_key}' must be a mapping")
            payload["metrics"][metric_key] = {**payload["metrics"][metric_key], **override}
        return payload

    def _read_yaml(self, name: str) -> dict[str, Any]:
        path = self.semantic_root / name
        if not path.exists():
            raise SemanticLayerError(f"Missing semantic layer file: {path}")
        with path.open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle) or {}
        if not isinstance(payload, dict):
            raise SemanticLayerError(f"Invalid YAML payload in {path}")
        return payload

    def _validate(self, payload: dict[str, Any]) -> None:
        metrics_payload = payload["metrics"]
        pages_payload = payload["pages"]

        if metrics_payload.get("version") != 1:
            raise SemanticLayerError("metrics.yml must declare version: 1")
        if pages_payload.get("version") != 1:
            raise SemanticLayerError("pages.yml must declare version: 1")

        metrics = metrics_payload.get("metrics")
        pages = pages_payload.get("pages")

        if not isinstance(metrics, dict) or not metrics:
            raise SemanticLayerError("metrics.yml must contain a non-empty metrics map")
        if not isinstance(pages, dict) or not pages:
            raise SemanticLayerError("pages.yml must contain a non-empty pages map")

        for metric_key, definition in metrics.items():
            if not isinstance(definition, dict):
                raise SemanticLayerError(f"Metric '{metric_key}' must be a mapping")
            for required_key in ("label", "description", "format", "aggregation"):
                if required_key not in definition:
                    raise SemanticLayerError(f"Metric '{metric_key}' is missing '{required_key}'")
            if definition.get("format") not in METRIC_FORMATS:
                raise SemanticLayerError(f"Metric '{metric_key}' has unsupported format '{definition.get('format')}'")
            for list_key in ("dimensions", "allowed_granularities", "allowed_comparisons"):
                values = definition.get(list_key, [])
                if not isinstance(values, list):
                    raise SemanticLayerError(f"Metric '{metric_key}' field '{list_key}' must be a list")

        for page_key, definition in pages.items():
            if not isinstance(definition, dict):
                raise SemanticLayerError(f"Page '{page_key}' must be a mapping")
            for required_key in ("label", "subtitle", "cards", "primary_trend_metric", "allowed_actions"):
                if required_key not in definition:
                    raise SemanticLayerError(f"Page '{page_key}' is missing '{required_key}'")
            if not isinstance(definition.get("cards"), list):
                raise SemanticLayerError(f"Page '{page_key}' field 'cards' must be a list")
            if not isinstance(definition.get("allowed_actions"), list):
                raise SemanticLayerError(f"Page '{page_key}' field 'allowed_actions' must be a list")
            if definition.get("current_trace_style") and definition.get("current_trace_style") not in TRACE_STYLES:
                raise SemanticLayerError(f"Page '{page_key}' has invalid current_trace_style")
            if definition.get("previous_trace_style") and definition.get("previous_trace_style") not in TRACE_STYLES:
                raise SemanticLayerError(f"Page '{page_key}' has invalid previous_trace_style")

            referenced_metrics = list(definition.get("cards", [])) + [definition["primary_trend_metric"]]
            for metric_key in referenced_metrics:
                if metric_key not in metrics:
                    raise SemanticLayerError(f"Page '{page_key}' references unknown metric '{metric_key}'")
