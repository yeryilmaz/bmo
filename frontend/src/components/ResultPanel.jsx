import { useState } from "react";

export default function ResultPanel({ task }) {
  const [tab, setTab] = useState("output");
  const [copied, setCopied] = useState(false);

  if (!task) return null;

  const isError = task.status === "error";
  const steps = Array.isArray(task.steps) ? task.steps : [];

  const copyResult = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // clipboard access might be restricted in some iframe contexts
    }
  };

  return (
    <div className="result-container">
      <section className={`result-card ${isError ? "result-error" : ""}`}>
        <div className="result-header">
          <div className="header-meta">
            <span className={`status-label ${task.status}`}>
              {task.status === "success" ? "Success" : "Error"}
            </span>
            <code className="tool-name">{task.tool_used}</code>
            {task.duration_ms > 0 && (
              <span className="duration-info">{task.duration_ms} ms</span>
            )}
          </div>

          <div className="header-actions">
            <button
              type="button"
              className="copy-btn"
              onClick={() => copyResult(task.result)}
              title="Copy output"
            >
              {copied ? "Copied!" : "Copy"}
            </button>
            <div className="view-toggle">
              <button
                type="button"
                className={`toggle-btn ${tab === "output" ? "active" : ""}`}
                onClick={() => setTab("output")}
              >
                Output
              </button>
              <button
                type="button"
                className={`toggle-btn ${tab === "trace" ? "active" : ""}`}
                onClick={() => setTab("trace")}
              >
                Trace ({steps.length})
              </button>
              <button
                type="button"
                className={`toggle-btn ${tab === "json" ? "active" : ""}`}
                onClick={() => setTab("json")}
              >
                JSON
              </button>
            </div>
          </div>
        </div>

        <div className="result-body">
          {tab === "output" && (
            <pre className="output-content">{task.result}</pre>
          )}

          {tab === "trace" && (
            <div className="trace-steps">
              {steps.length === 0 ? (
                <div className="step-text muted">No trace recorded</div>
              ) : (
                steps.map((step, idx) => (
                  <div key={idx} className="trace-step">
                    <span className="step-num">#{idx + 1}</span>
                    <span className="step-text">{step}</span>
                  </div>
                ))
              )}
            </div>
          )}

          {tab === "json" && (
            <pre className="json-content">{JSON.stringify(task, null, 2)}</pre>
          )}
        </div>

        <div className="result-footer">
          <span>{task.timestamp}</span>
          <span>Task #{task.id}</span>
        </div>
      </section>

      {tab === "output" && steps.length > 0 && (
        <aside className="trace-card">
          <h3>Execution Trace</h3>
          <div className="trace-steps">
            {steps.map((step, idx) => (
              <div key={idx} className="trace-step">
                <span className="step-num">#{idx + 1}</span>
                <span className="step-text">{step}</span>
              </div>
            ))}
          </div>
        </aside>
      )}
    </div>
  );
}

