import { useState, useEffect, useCallback } from "react";
import TaskInput from "./components/TaskInput";
import ResultPanel from "./components/ResultPanel";
import HistoryList from "./components/HistoryList";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [activeTask, setActiveTask] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadHistory = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/tasks`);
      if (!res.ok) return;
      const data = await res.json();
      setHistory(data);
    } catch {
      // ignore network errors if backend is starting up
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleRun = async (text) => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/api/task`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: text }),
      });

      if (!res.ok) {
        const payload = await res.json().catch(() => ({}));
        throw new Error(payload.detail || `Request failed (${res.status})`);
      }

      const task = await res.json();
      setActiveTask(task);
      loadHistory();
    } catch (err) {
      setError(err.message || "Failed to process task");
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = async (id) => {
    try {
      const res = await fetch(`${API_BASE}/api/tasks/${id}`);
      if (!res.ok) throw new Error("Task not found");
      const task = await res.json();
      setActiveTask(task);
      setError(null);
    } catch {
      setError("Failed to load task details");
    }
  };

  const handleDelete = async (id) => {
    try {
      const res = await fetch(`${API_BASE}/api/tasks/${id}`, { method: "DELETE" });
      if (res.ok) {
        setHistory((prev) => prev.filter((item) => item.id !== id));
        if (activeTask?.id === id) setActiveTask(null);
      }
    } catch {
      setError("Failed to delete task");
    }
  };

  const handleClear = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/tasks`, { method: "DELETE" });
      if (res.ok) {
        setHistory([]);
        setActiveTask(null);
      }
    } catch {
      setError("Failed to clear history");
    }
  };

  return (
    <div className="app-layout">
      <aside className="app-sidebar">
        <div className="sidebar-header">
          <h2>BMO Agent</h2>
          <span>Task Controller</span>
        </div>

        <div className="sidebar-section">
          <div className="section-title-row">
            <h3>History</h3>
            <span className="count-badge">{history.length}</span>
          </div>
          <HistoryList
            tasks={history}
            activeId={activeTask?.id}
            onSelect={handleSelect}
            onDelete={handleDelete}
            onClearAll={handleClear}
          />
        </div>
      </aside>

      <main className="app-main">
        <div className="main-container">
          <header className="workspace-header">
            <h1>Agent Task Runner</h1>
            <p>Run natural language prompts routed through specialized agent tools.</p>
          </header>

          <TaskInput onSubmit={handleRun} loading={loading} />

          {error && (
            <div className="alert-banner" role="alert">
              <span>{error}</span>
              <button
                type="button"
                className="alert-close"
                onClick={() => setError(null)}
                aria-label="Dismiss error"
              >
                &times;
              </button>
            </div>
          )}

          {loading && (
            <div className="execution-loader">
              Executing task through agent controller...
            </div>
          )}

          {!loading && activeTask && (
            <div className="task-view-grid">
              <ResultPanel task={activeTask} />
            </div>
          )}

          {!loading && !activeTask && !error && (
            <div className="empty-workspace">
              <h3>No active task</h3>
              <p>Type a task prompt above or pick a previous run from the history.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

