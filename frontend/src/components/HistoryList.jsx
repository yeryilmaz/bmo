import { useState } from "react";

function formatTime(str) {
  if (!str) return "";
  try {
    const d = new Date(str);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } catch {
    return str;
  }
}

export default function HistoryList({
  tasks = [],
  activeId,
  onSelect,
  onDelete,
  onClearAll,
}) {
  const [filter, setFilter] = useState("");

  const q = filter.trim().toLowerCase();
  const filtered = tasks.filter((t) => {
    if (!q) return true;
    return (
      t.input?.toLowerCase().includes(q) ||
      t.tool_used?.toLowerCase().includes(q)
    );
  });

  return (
    <div className="history-container">
      <div className="history-controls">
        <input
          type="text"
          className="history-search"
          placeholder="Filter history..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        />
        {tasks.length > 0 && onClearAll && (
          <button
            type="button"
            className="clear-all-btn"
            onClick={onClearAll}
            title="Clear history"
          >
            Clear
          </button>
        )}
      </div>

      {tasks.length === 0 ? (
        <div className="history-empty">No tasks recorded yet.</div>
      ) : filtered.length === 0 ? (
        <div className="history-empty">No matching tasks found.</div>
      ) : (
        filtered.map((t) => {
          const isCurrent = t.id === activeId;
          const timeStr = formatTime(t.timestamp);

          return (
            <div
              key={t.id}
              className={`history-card ${isCurrent ? "active" : ""}`}
              onClick={() => onSelect(t.id)}
            >
              <div className="card-top">
                <span className="card-input" title={t.input}>
                  {t.input}
                </span>
                {onDelete && (
                  <button
                    type="button"
                    className="delete-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDelete(t.id);
                    }}
                    title="Delete task"
                    aria-label={`Delete task ${t.id}`}
                  >
                    &times;
                  </button>
                )}
              </div>
              <div className="card-meta">
                <span className="tool-label">{t.tool_used}</span>
                <span>
                  {timeStr} &middot; {t.status}
                </span>
              </div>
            </div>
          );
        })
      )}
    </div>
  );
}

