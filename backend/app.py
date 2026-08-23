import json
import os
import sqlite3
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agents import AgentController

load_dotenv(override=True)

DB_PATH = os.path.join(os.path.dirname(__file__), "tasks.db")
agent_controller = AgentController()


def db_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def setup_database():
    with db_conn() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input TEXT NOT NULL,
                result TEXT NOT NULL,
                tool_used TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                duration_ms REAL NOT NULL,
                steps TEXT
            )
        """)
        cols = {row["name"] for row in db.execute("PRAGMA table_info(tasks)").fetchall()}
        if "steps" not in cols:
            db.execute("ALTER TABLE tasks ADD COLUMN steps TEXT")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_database()
    yield


app = FastAPI(title="BMO Agent API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskRequest(BaseModel):
    input: str = Field(..., min_length=1)


class TaskResponse(BaseModel):
    id: int
    input: str
    result: str
    tool_used: str
    timestamp: str
    status: str
    duration_ms: float
    steps: list[str] = []


def serialize_task(row: sqlite3.Row) -> dict:
    data = dict(row)
    raw = data.get("steps")
    if raw:
        try:
            data["steps"] = json.loads(raw)
        except Exception:
            data["steps"] = [str(raw)]
    else:
        data["steps"] = []
    return data


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/task", response_model=TaskResponse, status_code=201)
def create_task(req: TaskRequest):
    prompt = req.input.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Input cannot be empty")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    start = time.perf_counter()

    try:
        res = agent_controller.execute(prompt)
        status = "success"
        output_text = res["result"]
        tool_name = res["tool_used"]
        elapsed = res["duration_ms"]
        steps = res["steps"]
    except Exception as err:
        status = "error"
        output_text = str(err)
        tool_name = "error"
        elapsed = round((time.perf_counter() - start) * 1000, 1)
        steps = [
            f'Step 1: Received input "{prompt}"',
            f"Step 2: Error running agent: {err}",
            "Step 3: Returning error to user",
        ]

    with db_conn() as db:
        cur = db.execute(
            """
            INSERT INTO tasks (input, result, tool_used, timestamp, status, duration_ms, steps)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (prompt, output_text, tool_name, now, status, elapsed, json.dumps(steps)),
        )
        task_id = cur.lastrowid

    return TaskResponse(
        id=task_id,
        input=prompt,
        result=output_text,
        tool_used=tool_name,
        timestamp=now,
        status=status,
        duration_ms=elapsed,
        steps=steps,
    )


@app.get("/api/tasks", response_model=list[TaskResponse])
def get_task_history(limit: int = Query(default=50, ge=1, le=200)):
    with db_conn() as db:
        rows = db.execute(
            "SELECT id, input, result, tool_used, timestamp, status, duration_ms, steps FROM tasks ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [serialize_task(r) for r in rows]


@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
def get_task_by_id(task_id: int):
    with db_conn() as db:
        row = db.execute(
            "SELECT id, input, result, tool_used, timestamp, status, duration_ms, steps FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Task not found")

    return serialize_task(row)


@app.delete("/api/tasks/{task_id}")
def remove_task(task_id: int):
    with db_conn() as db:
        cur = db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"deleted": True}


@app.delete("/api/tasks")
def clear_all_tasks():
    with db_conn() as db:
        db.execute("DELETE FROM tasks")
    return {"cleared": True}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)

