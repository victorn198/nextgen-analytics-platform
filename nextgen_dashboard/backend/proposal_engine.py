from __future__ import annotations

import re
from typing import Iterable

from .models import PageName
from .semantic_layer import SemanticLayer


class ProposalEngine:
    def __init__(self, semantic_layer: SemanticLayer) -> None:
        self.semantic_layer = semantic_layer

    def suggestions_for_page(self, page: PageName) -> list[dict]:
        pages = self.semantic_layer.page_definitions()
        metrics = self.semantic_layer.metric_definitions()
        page_cfg = pages.get(page, {})
        cards = list(page_cfg.get("cards", []))
        primary_metric = page_cfg.get("primary_trend_metric")
        primary_label = metrics.get(primary_metric, {}).get(
            "label", primary_metric or "Primary metric"
        )
        page_label = page_cfg.get("label", page)

        suggestions: list[dict] = []

        if primary_metric:
            suggestions.append(
                {
                    "page": page,
                    "target": "semantic_layer",
                    "title": f"Clarify semantic definition for {primary_label}",
                    "rationale": f"The page centers on {primary_label}. Tightening the semantic description improves trust and makes future AI explanations more precise.",
                    "before": {
                        "metric_key": primary_metric,
                        "description": metrics.get(primary_metric, {}).get(
                            "description"
                        ),
                    },
                    "after": {
                        "metric_key": primary_metric,
                        "description": f"{primary_label} is the governed primary metric for {page_label}. Use it as the first read for current versus previous equivalent period movement.",
                    },
                }
            )
            suggestions.append(
                {
                    "page": page,
                    "target": "page",
                    "title": f"Add primary metric guidance for {page_label}",
                    "rationale": f"The page already centers on {primary_label}. Add a governed note so business users understand what the trend is optimized to explain.",
                    "before": {"insight_note": page_cfg.get("insight_note")},
                    "after": {
                        "insight_note": f"Primary metric is {primary_label}. Read it first to understand the main period-over-period movement before drilling into supporting KPIs."
                    },
                }
            )

        if "compare_previous_period" in page_cfg.get("allowed_actions", []):
            suggestions.append(
                {
                    "page": page,
                    "target": "page",
                    "title": "Add comparison reading note",
                    "rationale": "The dashboard already compares current versus previous equivalent period. Expose that rule directly in the page shell so users do not infer comparison logic incorrectly.",
                    "before": {"subtitle": page_cfg.get("subtitle")},
                    "after": {
                        "subtitle": f"{page_cfg.get('subtitle', '')} Current values are compared against the previous equivalent period, with partial edge periods aligned by day position.".strip()
                    },
                }
            )

        if page == "sales":
            suggestions.append(
                {
                    "page": page,
                    "target": "page",
                    "title": "Promote drilldown guidance on Sales Overview",
                    "rationale": "Sales already supports drilldown by clicked period. This is the strongest interaction in the app and should be explicit.",
                    "before": {"interaction_hint": page_cfg.get("interaction_hint")},
                    "after": {
                        "interaction_hint": "Click any aggregated Sales period in the chart to open the aligned day-by-day comparison for that selected window."
                    },
                }
            )
        elif page == "customers":
            suggestions.append(
                {
                    "page": page,
                    "target": "page",
                    "title": "Explain how new customers are defined",
                    "rationale": "Customer pages are often misread when new customers are defined only inside the filtered slice. Make the business definition explicit.",
                    "before": {"insight_note": page_cfg.get("insight_note")},
                    "after": {
                        "insight_note": "New Customers uses each customer's first-ever purchase date, while Repeat Purchase Rate uses only orders inside the selected window."
                    },
                }
            )
        elif page == "products":
            suggestions.append(
                {
                    "page": page,
                    "target": "page",
                    "title": "Add concentration risk note",
                    "rationale": "Product analysis becomes more actionable when concentration risk is explicitly called out instead of left only in KPI cards.",
                    "before": {"insight_note": page_cfg.get("insight_note")},
                    "after": {
                        "insight_note": "Watch Top Category Share and Top 5 Products Share together. If both rise, a small slice of the assortment is starting to dominate revenue."
                    },
                }
            )
        elif page == "operations":
            suggestions.append(
                {
                    "page": page,
                    "target": "page",
                    "title": "Surface operational reading order",
                    "rationale": "Operations is strongest when read as throughput first, then row intensity, then fulfillment quality.",
                    "before": {"insight_note": page_cfg.get("insight_note")},
                    "after": {
                        "insight_note": "Read Orders Count first, then Avg Lines / Order to assess processing complexity, and finally Non-Cancelled Rate to check quality under load."
                    },
                }
            )

        return suggestions

    def assist(self, page: PageName, request: str, limit: int = 4) -> list[dict]:
        normalized = self._normalize(request)
        if not normalized:
            return self.suggestions_for_page(page)[:limit]

        generated = self._request_specific_suggestions(page, normalized)
        library = self.suggestions_for_page(page)
        ranked = sorted(
            library,
            key=lambda item: self._score(item, normalized),
            reverse=True,
        )
        combined = self._dedupe(generated + ranked)
        if not combined:
            return library[:limit]
        return combined[:limit]

    def _request_specific_suggestions(
        self,
        page: PageName,
        normalized: str,
    ) -> list[dict]:
        pages = self.semantic_layer.page_definitions()
        metrics = self.semantic_layer.metric_definitions()
        page_cfg = pages.get(page, {})
        primary_metric = page_cfg.get("primary_trend_metric")
        primary_label = metrics.get(primary_metric, {}).get(
            "label", primary_metric or "Primary metric"
        )
        suggestions: list[dict] = []

        if primary_metric and any(
            token in normalized for token in ["rename", "call", "label", "name it"]
        ):
            new_label = self._extract_new_label(normalized)
            if new_label:
                suggestions.append(
                    {
                        "page": page,
                        "target": "semantic_layer",
                        "title": f"Rename {primary_label} to {new_label}",
                        "rationale": f"This updates the governed label for the primary metric on {page_cfg.get('label', page)}.",
                        "before": {"metric_key": primary_metric, "label": primary_label},
                        "after": {"metric_key": primary_metric, "label": new_label},
                    }
                )

        if "line" in normalized and "chart" in normalized:
            suggestions.append(
                {
                    "page": page,
                    "target": "page",
                    "title": "Use a line-led trend view",
                    "rationale": "A line-led current series makes trend continuity easier to read for this request.",
                    "before": {
                        "current_trace_style": page_cfg.get("current_trace_style"),
                        "previous_trace_style": page_cfg.get("previous_trace_style"),
                    },
                    "after": {
                        "current_trace_style": "line",
                        "previous_trace_style": "line",
                    },
                }
            )
        elif any(token in normalized for token in ["bar", "bars", "columns"]) and "chart" in normalized:
            suggestions.append(
                {
                    "page": page,
                    "target": "page",
                    "title": "Use a bar-led trend view",
                    "rationale": "A bar-led current series makes period comparison clearer for this request.",
                    "before": {
                        "current_trace_style": page_cfg.get("current_trace_style"),
                        "previous_trace_style": page_cfg.get("previous_trace_style"),
                    },
                    "after": {
                        "current_trace_style": "bar",
                        "previous_trace_style": "line",
                    },
                }
            )

        if any(
            token in normalized
            for token in ["explain", "clarify", "understand", "comparison", "compare"]
        ):
            suggestions.append(
                {
                    "page": page,
                    "target": "page",
                    "title": "Explain comparison logic on the page",
                    "rationale": "The request asks for clearer interpretation. Add a note that explains how current and previous periods are compared.",
                    "before": {"subtitle": page_cfg.get("subtitle")},
                    "after": {
                        "subtitle": f"{page_cfg.get('subtitle', '')} Current values are compared against the previous equivalent period, with partial edge periods aligned by day position.".strip()
                    },
                }
            )

        if page == "sales" and any(
            token in normalized for token in ["drilldown", "detail", "click"]
        ):
            suggestions.append(
                {
                    "page": page,
                    "target": "page",
                    "title": "Make drilldown interaction explicit",
                    "rationale": "The request mentions detail navigation. Expose the click-to-drill behavior directly on the page.",
                    "before": {"interaction_hint": page_cfg.get("interaction_hint")},
                    "after": {
                        "interaction_hint": "Click any aggregated Sales period in the chart to open the aligned day-by-day comparison for that selected window."
                    },
                }
            )

        if page == "customers" and any(
            token in normalized for token in ["retention", "repeat", "returning", "loyal"]
        ):
            suggestions.append(
                {
                    "page": page,
                    "target": "page",
                    "title": "Explain retention reading order",
                    "rationale": "The request points to retention. Add a guided note that tells users to read repeat rate before new-customer volume.",
                    "before": {"insight_note": page_cfg.get("insight_note")},
                    "after": {
                        "insight_note": "Read Repeat Purchase Rate first, then Returning Customers, and only then New Customers. This sequence separates retention quality from acquisition volume."
                    },
                }
            )

        if page == "products" and any(
            token in normalized for token in ["category", "concentration", "risk", "mix"]
        ):
            suggestions.append(
                {
                    "page": page,
                    "target": "page",
                    "title": "Highlight product concentration risk",
                    "rationale": "The request points to product mix or category risk. Add a note that explains how to use the concentration metrics.",
                    "before": {"insight_note": page_cfg.get("insight_note")},
                    "after": {
                        "insight_note": "Watch Top Category Share and Top 5 Products Share together. If both rise, a small part of the assortment is dominating revenue."
                    },
                }
            )

        return suggestions

    def _extract_new_label(self, normalized: str) -> str | None:
        match = re.search(r"(?:rename|call|label|name it) .*? to ([a-z0-9 /-]+)$", normalized)
        if not match:
            return None
        label = match.group(1).strip(" .,!?:;'")
        if not label:
            return None
        return " ".join(part.capitalize() for part in label.split())

    def _score(self, suggestion: dict, normalized_request: str) -> int:
        haystack = self._normalize(
            " ".join(
                [
                    suggestion.get("title", ""),
                    suggestion.get("rationale", ""),
                    str(suggestion.get("after", {})),
                ]
            )
        )
        score = 0
        for token in self._tokens(normalized_request):
            if token in haystack:
                score += 1
        return score

    def _dedupe(self, suggestions: Iterable[dict]) -> list[dict]:
        unique: list[dict] = []
        seen: set[tuple[str, str]] = set()
        for suggestion in suggestions:
            key = (suggestion.get("title", ""), suggestion.get("target", ""))
            if key in seen:
                continue
            seen.add(key)
            unique.append(suggestion)
        return unique

    def _tokens(self, text: str) -> list[str]:
        return [token for token in text.split() if len(token) > 2]

    def _normalize(self, text: str) -> str:
        return re.sub(r"\s+", " ", (text or "").strip().lower())
