from __future__ import annotations

from typing import Any, Dict, List, Optional


from src.contracts import ResearchAdapterResult
from src.requirement_schema_v2 import DesignSpace, RequirementSchemaV2


class ResearchAdapterDisabledError(RuntimeError):
    """Raised when a disabled research adapter is asked to make a live call."""


class ResearchAdapterBase:
    adapter_name = "research_adapter"
    enabled = False

    def __init__(self, enabled: bool = False, config: Optional[Dict[str, Any]] = None) -> None:
        self.enabled = enabled
        self.config = config or {}

    def disabled_result(self, message: Optional[str] = None) -> ResearchAdapterResult:
        return {
            "adapter": self.adapter_name,
            "status": "disabled",
            "enabled": False,
            "message": message or f"{self.adapter_name} is disabled; no live calls were made.",
            "candidates": [],
            "evidence": [],
            "metadata": {},
        }

    def ensure_enabled(self) -> None:
        if not self.enabled:
            raise ResearchAdapterDisabledError(
                f"{self.adapter_name} is disabled by default; enable explicitly before use."
            )

    def generate_candidates(
        self,
        requirements: RequirementSchemaV2,
        design_space: Optional[DesignSpace] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ResearchAdapterResult:
        return self.disabled_result()

    def retrieve_evidence(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ResearchAdapterResult:
        return self.disabled_result()

    def rank_or_annotate(
        self,
        candidates: List[Dict[str, Any]],
        requirements: RequirementSchemaV2,
        context: Optional[Dict[str, Any]] = None,
    ) -> ResearchAdapterResult:
        return self.disabled_result()
