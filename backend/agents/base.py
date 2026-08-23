import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

from agents.router import heuristic_route
from agents.tools_registry import AVAILABLE_TOOLS, TOOL_MAP

load_dotenv(override=True)

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


class AgentController:
    def __init__(self, model: str | None = None, api_key: str | None = None):
        self.model = model or DEFAULT_MODEL
        self.api_key = api_key if api_key is not None else os.getenv("GEMINI_API_KEY", "")

    def execute(self, prompt: str) -> dict:
        t0 = time.perf_counter()
        trace = [f'Step 1: Received input "{prompt}"']

        chosen_tool, tool_args = None, {}
        used_fallback = False

        # Try tool calling via Gemini if key is provided
        if self.api_key:
            try:
                ai_client = genai.Client(api_key=self.api_key)
                cfg = types.GenerateContentConfig(
                    tools=AVAILABLE_TOOLS,
                    tool_config=types.ToolConfig(
                        function_calling_config=types.FunctionCallingConfig(mode="ANY")
                    ),
                    system_instruction=(
                        "You are a routing agent. Pick the right tool "
                        "(CalculatorTool, WeatherMockTool, TextProcessorTool) and supply its arguments."
                    ),
                )
                resp = ai_client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=cfg,
                )

                if resp.function_calls:
                    call = resp.function_calls[0]
                    chosen_tool = call.name
                    tool_args = dict(call.args or {})
                elif resp.text:
                    elapsed = round((time.perf_counter() - t0) * 1000, 1)
                    trace.extend(["Step 2: Direct model response", f"Step 3: Output: {resp.text}", "Step 4: Done"])
                    return {
                        "result": resp.text,
                        "tool_used": "none",
                        "duration_ms": elapsed,
                        "steps": trace,
                    }
            except Exception:
                # Quota issue or offline -> switch over to heuristic router
                used_fallback = True

        # LLM skipped or failed, fallback to local rule router
        if not chosen_tool:
            chosen_tool, tool_args = heuristic_route(prompt)

        tag = " (fallback router)" if used_fallback else ""
        trace.append(f"Step 2: Selected tool: {chosen_tool}{tag}")

        # Run the tool
        handler = TOOL_MAP.get(chosen_tool)
        if handler:
            try:
                output = str(handler(**tool_args))
                trace.append(f"Step 3: Tool result: {output}")
            except Exception as err:
                output = f"Tool error: {err}"
                trace.append(f"Step 3: {output}")
        else:
            output = f"Unknown tool: {chosen_tool}"
            trace.append(f"Step 3: {output}")

        trace.append("Step 4: Returning result to user")
        total_time = round((time.perf_counter() - t0) * 1000, 1)

        return {
            "result": output,
            "tool_used": chosen_tool,
            "duration_ms": total_time,
            "steps": trace,
        }

