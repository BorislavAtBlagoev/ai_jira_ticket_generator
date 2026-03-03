from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx

from .models import GenerateRequest, GenerateResponse


SYSTEM_PROMPT = (
    "You are a Senior Jira/Agile Business Analyst. "
    "Create concise, clear Jira ticket drafts in English only. "
    "Use sentence case for the title. "
    "Write acceptance criteria as testable Given/When/Then statements. "
    "Do not invent unknown facts; if details are missing, add them under assumptions. "
    "Return valid JSON matching the provided schema exactly."
)


def parse_labels(raw_labels: str | None) -> list[str]:
    if not raw_labels:
        return []
    labels = [item.strip().lower() for item in raw_labels.split(",")]
    return [label for label in labels if label]


def merge_labels(user_labels: list[str], ai_labels: list[str]) -> list[str]:
    merged: list[str] = []
    for label in [*user_labels, *ai_labels]:
        normalized = label.strip().lower()
        if normalized and normalized not in merged:
            merged.append(normalized)
    return merged


def _response_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "title": {"type": "string"},
            "issue_type": {"type": "string", "enum": ["Bug", "Task", "Story"]},
            "priority": {"type": "string", "enum": ["Low", "Medium", "High"]},
            "project_key": {"type": ["string", "null"]},
            "description": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "problem": {"type": "string"},
                    "proposed_solution": {"type": "string"},
                    "notes": {"type": "string"},
                },
                "required": ["problem", "proposed_solution", "notes"],
            },
            "acceptance_criteria": {"type": "array", "items": {"type": "string"}},
            "definition_of_done": {"type": "array", "items": {"type": "string"}},
            "labels": {"type": "array", "items": {"type": "string"}},
            "estimate": {"type": "string", "enum": ["S", "M", "L"]},
            "assumptions": {"type": "array", "items": {"type": "string"}},
        },
        "required": [
            "title",
            "issue_type",
            "priority",
            "project_key",
            "description",
            "acceptance_criteria",
            "definition_of_done",
            "labels",
            "estimate",
            "assumptions",
        ],
    }


def _build_prompt(payload: GenerateRequest, user_labels: list[str]) -> str:
    labels_text = ", ".join(user_labels) if user_labels else "(none provided)"
    return (
        f"{SYSTEM_PROMPT}\n\n"
        "Return only JSON, with no markdown, no code fences, and no extra text.\n"
        "Use concrete values for every field (never return schema fragments, type definitions, or placeholders).\n\n"
        "Ticket details:\n"
        f"{payload.ticket_details}\n\n"
        f"Issue type: {payload.issue_type.value}\n"
        f"Priority: {payload.priority.value}\n"
        f"Project key: {payload.project_key or '(not provided)'}\n"
        f"User labels (must be preserved in final labels list): {labels_text}\n"
    )


def generate_ticket(payload: GenerateRequest) -> GenerateResponse:
    ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3")

    user_labels = parse_labels(payload.labels)

    request_payload = {
        "model": ollama_model,
        "prompt": _build_prompt(payload, user_labels),
        "format": _response_schema(),
        "stream": False,
    }

    try:
        with httpx.Client(timeout=90) as client:
            response = client.post(f"{ollama_url}/api/generate", json=request_payload)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Ollama request failed: {exc}") from exc

    content = response.json().get("response", "")
    if not content:
        raise RuntimeError("Ollama returned an empty response")

    parsed = _parse_ollama_response(content)

    parsed["labels"] = merge_labels(user_labels, parsed.get("labels", []))
    parsed["project_key"] = payload.project_key or None
    parsed["issue_type"] = payload.issue_type.value
    parsed["priority"] = payload.priority.value

    return GenerateResponse.model_validate(parsed)


def _parse_ollama_response(content: str) -> dict[str, Any]:
    cleaned = content.strip()

    # Ollama occasionally wraps JSON in markdown fences despite prompt instructions.
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, count=1, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    decoder = json.JSONDecoder()

    # Handle responses with trailing non-JSON text by decoding the first object only.
    try:
        parsed, _ = decoder.raw_decode(cleaned)
    except json.JSONDecodeError:
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Failed to parse JSON from Ollama response: {exc}") from exc

    if not isinstance(parsed, dict):
        raise RuntimeError("Ollama response JSON must be an object")

    return parsed


def to_markdown(ticket: GenerateResponse) -> str:
    lines = [f"# {ticket.title}", "", f"- **Issue type:** {ticket.issue_type.value}", f"- **Priority:** {ticket.priority.value}"]
    if ticket.project_key:
        lines.append(f"- **Project key:** {ticket.project_key}")

    lines.extend(
        [
            "",
            "## Description",
            f"- **Problem:** {ticket.description.problem}",
            f"- **Proposed solution:** {ticket.description.proposed_solution}",
            f"- **Notes:** {ticket.description.notes}",
            "",
            "## Acceptance criteria",
            *[f"- {item}" for item in ticket.acceptance_criteria],
            "",
            "## Definition of done",
            *[f"- {item}" for item in ticket.definition_of_done],
            "",
            f"**Labels:** {', '.join(ticket.labels)}",
            "",
            f"**Estimate:** {ticket.estimate.value}",
            "",
            "## Assumptions",
            *[f"- {item}" for item in ticket.assumptions],
        ]
    )

    return "\n".join(lines)
