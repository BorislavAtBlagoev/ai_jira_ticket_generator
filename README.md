# AI Jira Ticket Generator (Local Docker App)

AI Jira Ticket Generator is a small local-only web app that helps you draft Jira tickets using a fully local Ollama model.
It includes:

- **FastAPI backend** for validation, AI generation, and markdown rendering.
- **React + Vite frontend** for form input, preview, markdown/json tabs, and download/copy actions.
- **Ollama service** for local model inference (default: `phi3:mini`).
- **Docker Compose** setup so the app runs on a clean machine with only Docker installed.

## Features

- Generator page at `/` with required fields:
  - Ticket details (required, textarea)
  - Issue type: Bug / Task / Story
  - Priority: Low / Medium / High
  - Project key (optional)
  - Labels (optional, comma-separated)
  - Output format fixed to **Jira markdown**
- Buttons: **Generate**, **Clear**, **Regenerate**
- Result tabs: **Preview**, **Markdown**, **JSON**
- Result actions:
  - Copy Markdown
  - Copy JSON
  - Download `.md`
  - Download `.json`
- Help page at `/help` with field guidance, complete example input, output snippet, and **Use example** button.
- Backend API:
  - `GET /api/health` -> `{ "status": "ok" }`
  - `POST /api/generate`
- Local structured generation via Ollama JSON output mode.

## Requirements

- Docker
- Docker Compose (v2)

No Python or Node installation is required on your host machine.
No API keys are required.

## Project Structure

```
.
├── backend
│   ├── app
│   │   ├── main.py
│   │   ├── models.py
│   │   └── services.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend
│   ├── src
│   │   ├── components
│   │   │   ├── GeneratorPage.tsx
│   │   │   └── HelpPage.tsx
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── styles.css
│   │   └── types.ts
│   ├── Dockerfile
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── .env.example
├── docker-compose.yml
└── README.md
```

## Setup (100% Local)

1. Copy environment template:

   ```bash
   cp .env.example .env
   ```

2. (Optional) choose model in `.env`:

   ```dotenv
   OLLAMA_MODEL=phi3:mini
   ```

   Alternative supported model: `mistral`.

3. Start the app:

   ```bash
   docker compose up --build
   ```

   On startup, Docker Compose waits for Ollama to become healthy, then a one-shot `ollama-pull` service pulls the configured model and persists it in a Docker volume before the backend starts.

4. Open:
   - Frontend: `http://localhost:5173`
   - Backend health: `http://localhost:8000/api/health`

## How to Use

1. Open `http://localhost:5173`.
2. Fill in **Ticket details**.
3. Select **Issue type** and **Priority**.
4. (Optional) provide **Project key** and comma-separated **Labels**.
5. Click **Generate**.
6. Review output in:
   - **Preview** (human-readable)
   - **Markdown** (Jira-friendly markdown)
   - **JSON** (structured object)
7. Use copy/download buttons as needed.
8. Use **Regenerate** to run again with the same input.
9. Use **Clear** to reset the form and output.

## Help Page

Open `http://localhost:5173/help` for:

- Field descriptions and practical guidance.
- A complete example input.
- An output snippet preview.
- A **Use example** button that opens `/` and pre-fills the form.

## API Notes

### POST `/api/generate`

Request:

```json
{
  "ticket_details": "string",
  "issue_type": "Bug",
  "priority": "High",
  "project_key": "APP",
  "labels": "backend, validation"
}
```

Validation rules:

- `ticket_details` must be non-empty.
- `issue_type` must be one of `Bug | Task | Story`.
- `priority` must be one of `Low | Medium | High`.
- Labels are parsed from comma-separated text.
- User labels are always preserved in final label output (AI can add labels but cannot remove user-provided ones).

Response envelope:

```json
{
  "ticket": {
    "title": "...",
    "issue_type": "Bug",
    "priority": "High",
    "project_key": "APP",
    "description": {
      "problem": "...",
      "proposed_solution": "...",
      "notes": "..."
    },
    "acceptance_criteria": ["Given ... When ... Then ..."],
    "definition_of_done": ["..."],
    "labels": ["backend", "validation", "api"],
    "estimate": "M",
    "assumptions": ["..."]
  },
  "markdown": "# ..."
}
```

## Frontend-to-Backend Configuration

The frontend uses the environment variable:

- `VITE_API_BASE_URL=http://localhost:8000`

This is configured in `docker-compose.yml`.

## Error Handling

- Ollama connectivity/model failures are returned as API errors and shown in the UI.
- Validation errors are returned by FastAPI and shown in the UI.

## Important Notes

- This project is designed for **local use only**.
- No login/authentication.
- No database.
- No server-side persistence.
- English-only UI and generated app content.
