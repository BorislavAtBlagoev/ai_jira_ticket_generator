from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .models import GenerateRequest, GenerateResponse
from .services import generate_ticket, to_markdown


class GenerateEnvelope(BaseModel):
    ticket: GenerateResponse
    markdown: str


app = FastAPI(title="AI Jira Ticket Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/generate", response_model=GenerateEnvelope)
def generate(payload: GenerateRequest) -> GenerateEnvelope:
    try:
        ticket = generate_ticket(payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"AI generation failed: {exc}") from exc

    markdown = to_markdown(ticket)
    return GenerateEnvelope(ticket=ticket, markdown=markdown)
