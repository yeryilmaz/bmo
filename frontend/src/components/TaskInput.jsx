import { useState, useRef, useEffect } from "react";

const SAMPLES = [
  { label: "Math", prompt: "(5 * 2) + sqrt(144)" },
  { label: "Weather", prompt: "What is the weather in Toronto?" },
  { label: "Uppercase", prompt: "Convert 'hello my name is yusuf' to uppercase" },
  { label: "Word count", prompt: "Count words in 'Hello my name is yusuf'" },
];

export default function TaskInput({ onSubmit, loading }) {
  const [val, setVal] = useState("");
  const inputRef = useRef(null);

  useEffect(() => {
    if (!loading && inputRef.current) {
      inputRef.current.focus();
    }
  }, [loading]);

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    const query = val.trim();
    if (!query || loading) return;
    onSubmit(query);
  };

  const handleKeyDown = (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="task-composer">
      <form onSubmit={handleSubmit} className="composer-form">
        <div className="textarea-wrapper">
          <textarea
            ref={inputRef}
            value={val}
            onChange={(e) => setVal(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a math problem, text operation, or ask the weather... (Cmd+Enter to run)"
            rows={3}
            disabled={loading}
          />
          {val && !loading && (
            <button
              type="button"
              className="clear-input-btn"
              onClick={() => setVal("")}
              title="Clear"
              aria-label="Clear input"
            >
              &times;
            </button>
          )}
        </div>

        <div className="composer-footer">
          <div className="quick-suggestions">
            <span className="suggestions-label">Examples:</span>
            {SAMPLES.map((s) => (
              <button
                key={s.label}
                type="button"
                className="suggestion-tag"
                onClick={() => setVal(s.prompt)}
                disabled={loading}
              >
                {s.label}
              </button>
            ))}
          </div>

          <button
            type="submit"
            className="run-button"
            disabled={loading || !val.trim()}
          >
            {loading ? "Running..." : "Run"}
          </button>
        </div>
      </form>
    </div>
  );
}

