# BMO - Task Runner Agent

A lightweight full-stack application that takes user prompts, selects the right tool (math evaluation, text transformation, weather info) using LLM function calling, and executes them with a recorded step trace.

---

## Dependencies & Prerequisites

- **Backend:** Python 3.10+
  - `fastapi`, `uvicorn`, `google-genai`, `pydantic`, `python-dotenv`, `pytest`
- **Frontend:** Node.js 18+
  - `react` (v18), `axios`, `vite`
- **Database:** SQLite (built-in with Python)

---

## Getting Started

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Optional: Add your Gemini API key (app falls back to heuristic routing if missing)
cp .env.example .env

python app.py
```
> Running at `http://localhost:8000`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```
> Running at `http://localhost:5173`.

### 3. Tests

```bash
cd backend
pytest tests/
```

---

## Assumptions & Tradeoffs

- **Fallback Routing:** If the Gemini API key isn't provided or the request fails, the backend falls back to a regex/keyword-based router so the app remains usable offline.
- **SQLite:** Used SQLite for simplicity and zero setup overhead, storing step traces directly as serialized JSON strings.
- **Synchronous Execution:** Kept request execution synchronous for simplicity rather than introducing background workers (Celery/Redis) within the project timeframe.
- **Mock Weather Tool:** The weather tool currently generates deterministic mock data instead of calling an external live provider to avoid requiring third-party weather API keys.
- **Single-step Intent:** Handled single-turn tool calls per request to keep the execution flow clean and predictable.

---

## Time Spent

**Total time:** ~6 hours

- **Backend & Tool Routing (~2h):** FastAPI setup, tool registry, Gemini function calling, and the fallback router.
- **Database & State (~1h):** SQLite models, JSON step serialization, and task history endpoints.
- **Frontend UI (~1.5h):** Task input form, real-time result viewing, execution step breakdown, and clean CSS styling.
- **Testing & Documentation (~1.5h):** Pytest test cases, edge case handling, and writeup.

---

## What I'd Improve with More Time

- **User Authentication:** Add user login / JWT authentication so task histories are personalized and securely isolated per user.
- **Live Weather API Integration:** Replace the mock weather tool with a real third-party service (e.g. OpenWeatherMap or WeatherAPI) for actual live meteorological data and forecasts.
- **Multi-step Agent Chaining:** Support multi-step execution loops where the output of one tool can feed into another (e.g. fetch live weather -> calculate average temp -> generate text summary).
