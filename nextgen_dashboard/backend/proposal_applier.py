from __future__ import annotations

from .proposal_contracts import METRIC_OVERRIDE_FIELDS, PAGE_OVERRIDE_FIELDS, PAGE_SCOPED_TARGETS
from .proposal_store import ProposalStore
from .semantic_layer import SemanticLayer


class ProposalApplyError(RuntimeError):
    """Raised when an approved proposal cannot be materialized into a draft override."""


class ProposalApplier:
    def __init__(self, proposal_store: ProposalStore, semantic_layer: SemanticLayer) -> None:
        self.proposal_store = proposal_store
        self.semantic_layer = semantic_layer

    def apply_to_draft(self, proposal_id: str) -> dict:
        proposal = self.proposal_store.get_proposal(proposal_id)
        if proposal.get("status") != "approved":
            raise ProposalApplyError("Only approved proposals can be applied to draft")
        if proposal.get("applied_to_draft_at"):
            return proposal

        target = proposal.get("target")
        after = proposal.get("after") or {}
        if not isinstance(after, dict):
            raise ProposalApplyError("Proposal after payload must be an object")

        if target in PAGE_SCOPED_TARGETS:
            page = proposal.get("page")
            if not page:
                raise ProposalApplyError("Proposal must declare a page to apply a page/dashboard draft override")
            override = {key: value for key, value in after.items() if key in PAGE_OVERRIDE_FIELDS}
            if not override:
                raise ProposalApplyError("Proposal has no supported page override fields to apply")
            self.semantic_layer.preview_page_override(page, override)
            self.proposal_store.write_page_override(page, override)
            self.semantic_layer.refresh()
            return self.proposal_store.mark_proposal_applied(proposal_id)

        if target == "semantic_layer":
            metric_key = after.get("metric_key")
            if not isinstance(metric_key, str):
                raise ProposalApplyError("Semantic-layer proposals must declare 'metric_key'")
            override = {key: value for key, value in after.items() if key in METRIC_OVERRIDE_FIELDS}
            if not override:
                raise ProposalApplyError("Proposal has no supported metric override fields to apply")
            self.semantic_layer.preview_metric_override(metric_key, override)
            self.proposal_store.write_metric_override(metric_key, override)
            self.semantic_layer.refresh()
            return self.proposal_store.mark_proposal_applied(proposal_id)

        raise ProposalApplyError(f"Unsupported proposal target: {target}")
