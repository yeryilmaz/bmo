# BMO - AI Agent Task Runner

A lightweight full-stack application that routes user tasks to specific tools (Calculator, Weather, Text Processor) using Gemini function calling with a fallback router, tracking execution steps and task history in SQLite.

---

## Quick Start

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # Add your GEMINI_API_KEY
python app.py
```
> Running at `http://localhost:8000`. (If no API key is provided, the heuristic fallback router takes over.)

### Frontend
```bash
cd frontend
npm install
npm run dev
```
> Running at `http://localhost:5173`.

### Run Tests
```bash
cd backend
pytest tests/
```

---

## Tech Stack

- **Backend:** FastAPI, Python 3.10+, Google GenAI SDK, SQLite, Pytest
- **Frontend:** React 18, Vite, CSS

---

## Key Notes

- **Routing:** Uses Gemini function calling (`mode="ANY"`), with a built-in heuristic fallback when offline or without an API key.
- **Storage:** SQLite with JSON-serialized step traces for task history.
- **Tools:** Math evaluator (restricted namespace), mock weather generator, and string manipulation utilities.
