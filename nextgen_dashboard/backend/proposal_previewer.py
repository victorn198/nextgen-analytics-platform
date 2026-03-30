from __future__ import annotations

from .models import ProposalPreviewChange, ProposalPreviewPayload, ProposalRecord
from .proposal_contracts import METRIC_OVERRIDE_FIELDS, PAGE_OVERRIDE_FIELDS, PAGE_SCOPED_TARGETS
from .proposal_store import ProposalStore
from .semantic_layer import SemanticLayer


class ProposalPreviewError(RuntimeError):
    """Raised when a proposal preview cannot be generated."""


class ProposalPreviewer:
    def __init__(self, proposal_store: ProposalStore, semantic_layer: SemanticLayer) -> None:
        self.proposal_store = proposal_store
        self.semantic_layer = semantic_layer

    def preview(self, proposal_id: str) -> ProposalPreviewPayload:
        proposal = self.proposal_store.get_proposal(proposal_id)
        return self.preview_request(proposal)

    def preview_request(self, proposal: dict) -> ProposalPreviewPayload:
        target = proposal.get("target")
        after = proposal.get("after") or {}
        if not isinstance(after, dict):
            raise ProposalPreviewError("Proposal after payload must be an object")

        if target in PAGE_SCOPED_TARGETS:
            page = proposal.get("page")
            if not page:
                raise ProposalPreviewError("Page-scoped preview requires a page")
            current = self.semantic_layer.page_definitions().get(page)
            if current is None:
                raise ProposalPreviewError(f"Unknown page: {page}")
            override = {key: value for key, value in after.items() if key in PAGE_OVERRIDE_FIELDS}
            effective = self.semantic_layer.preview_page_override(page, override) if override else current
            scope_key = page
        elif target == "semantic_layer":
            metric_key = after.get("metric_key")
            if not isinstance(metric_key, str):
                raise ProposalPreviewError("Semantic-layer preview requires metric_key")
            current = self.semantic_layer.metric_definitions().get(metric_key)
            if current is None:
                raise ProposalPreviewError(f"Unknown metric: {metric_key}")
            override = {key: value for key, value in after.items() if key in METRIC_OVERRIDE_FIELDS}
            effective = self.semantic_layer.preview_metric_override(metric_key, override) if override else current
            scope_key = metric_key
        else:
            raise ProposalPreviewError(f"Unsupported proposal target: {target}")

        changes = [
            ProposalPreviewChange(field=field, before=current.get(field), after=effective.get(field))
            for field in override
            if current.get(field) != effective.get(field)
        ]

        preview_record = {
            **proposal,
            "proposal_id": proposal.get("proposal_id", "preview"),
            "created_at": proposal.get("created_at", "preview"),
            "status": proposal.get("status", "proposed"),
            "reviewer_note": proposal.get("reviewer_note"),
            "updated_at": proposal.get("updated_at"),
            "applied_to_draft_at": proposal.get("applied_to_draft_at"),
        }

        return ProposalPreviewPayload(
            proposal=ProposalRecord(**preview_record),
            scope_key=scope_key,
            current_config=current,
            proposed_override=override,
            effective_config=effective,
            changes=changes,
        )
