from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class GuardrailIssue:
    category: str
    message: str
    severity: str = "warning"

    def __getitem__(self, item: str) -> str:
        return getattr(self, item)

    def to_dict(self) -> dict[str, str]:
        return {
            "category": self.category,
            "message": self.message,
            "severity": self.severity,
        }


@dataclass
class GuardrailReport:
    blocked: bool
    issues: list[GuardrailIssue] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "blocked": self.blocked,
            "issues": [issue.to_dict() for issue in self.issues],
            "summary": self.summary,
        }


_BIAS_PATTERNS = [
    r"\b(only|exclusively|target|for)\b.*\b(white|black|asian|hispanic|male|female|men|women|old|young|rich|poor|christian|muslim|jewish|gay|straight|disabled)\b",
    r"\b(white|black|asian|hispanic|male|female|men|women|old|young|rich|poor|christian|muslim|jewish|gay|straight|disabled)\b.*\b(only|exclusively|target|for)\b",
]


def _contains_bias(text: str) -> bool:
    if not text:
        return False
    lower = text.lower()
    return any(re.search(pattern, lower) for pattern in _BIAS_PATTERNS)


def evaluate_brief_guardrails(brief: dict[str, Any]) -> GuardrailReport:
    """Run lightweight policy checks over a proposed BrandBrief.

    The checks are intentionally simple and deterministic so they can run fast
    before any expensive media generation is triggered.
    """
    issues: list[GuardrailIssue] = []
    text_fields = [
        brief.get("business_name", ""),
        brief.get("one_liner", ""),
        brief.get("target_audience", ""),
        brief.get("core_message", ""),
        brief.get("call_to_action", ""),
        brief.get("voiceover_script", ""),
    ]

    if any(_contains_bias(field) for field in text_fields):
        issues.append(
            GuardrailIssue(
                category="bias",
                message="The brief contains exclusionary or discriminatory targeting language.",
                severity="error",
            )
        )

    if not brief.get("core_message"):
        issues.append(
            GuardrailIssue(
                category="missing_content",
                message="The brief is missing a clear core message.",
                severity="warning",
            )
        )

    if not brief.get("call_to_action"):
        issues.append(
            GuardrailIssue(
                category="missing_content",
                message="The brief is missing a clear call to action.",
                severity="warning",
            )
        )

    blocked = any(issue.severity == "error" for issue in issues)
    summary = (
        "Blocked" if blocked else "Approved"
    ) + f" with {len(issues)} issue(s)"

    return GuardrailReport(blocked=blocked, issues=issues, summary=summary)
