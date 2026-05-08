from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class InsuranceExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    insurer: str | None = None
    policy_type: str | None = None
    sum_insured: float | None = None
    waiting_periods: list[str] = Field(default_factory=list)
    exclusions: list[str] = Field(default_factory=list)


class MutualFundExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mutual_fund_names: list[str] = Field(default_factory=list)
    folios: list[str] = Field(default_factory=list)
    portfolio_value: float | None = None


class FinancialDocumentExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    insurance: InsuranceExtraction = Field(default_factory=InsuranceExtraction)
    mutual_funds: MutualFundExtraction = Field(default_factory=MutualFundExtraction)


class FinancialExtractionEngine:
    """Structured financial extractor with retry + strict validation."""

    def __init__(self, max_retries: int = 3) -> None:
        self.max_retries = max_retries

    def extract(self, raw_text: str, document_hints: list[str] | None = None) -> dict[str, Any]:
        prompt = self._build_prompt(raw_text=raw_text, hints=document_hints or [])

        last_error: str | None = None
        for attempt in range(1, self.max_retries + 1):
            llm_json = self._call_llm_structured(prompt=prompt, attempt=attempt)
            try:
                parsed = FinancialDocumentExtraction.model_validate_json(llm_json)
                return {
                    "attempts": attempt,
                    "validated": True,
                    "data": parsed.model_dump(mode="json"),
                    "schema": "FinancialDocumentExtraction",
                }
            except ValidationError as exc:
                last_error = str(exc)
                prompt = self._build_retry_prompt(prompt, llm_json, last_error)

        return {
            "attempts": self.max_retries,
            "validated": False,
            "data": FinancialDocumentExtraction().model_dump(mode="json"),
            "schema": "FinancialDocumentExtraction",
            "error": last_error,
        }

    def _call_llm_structured(self, prompt: str, attempt: int) -> str:
        """
        LLM call placeholder.

        This is intentionally implemented as a deterministic JSON response so this
        backend remains runnable without external model credentials. Replace this
        method with your model provider call that returns a strict JSON object.
        """
        _ = prompt
        _ = attempt
        return json.dumps(
            {
                "insurance": {
                    "insurer": None,
                    "policy_type": None,
                    "sum_insured": None,
                    "waiting_periods": [],
                    "exclusions": [],
                },
                "mutual_funds": {
                    "mutual_fund_names": [],
                    "folios": [],
                    "portfolio_value": None,
                },
            }
        )

    def _build_prompt(self, raw_text: str, hints: list[str]) -> str:
        return (
            "Extract finance data into strict JSON. "
            f"Document hints: {hints}. "
            "Only output JSON with keys: insurance and mutual_funds. "
            f"Text: {raw_text[:12000]}"
        )

    def _build_retry_prompt(self, base_prompt: str, previous_output: str, error: str) -> str:
        return (
            f"{base_prompt}\n"
            "Your previous JSON failed validation. "
            f"Validation error: {error}. "
            f"Previous output: {previous_output}. "
            "Return corrected strict JSON only."
        )
