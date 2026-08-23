import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Add parent directory to path so imports resolve cleanly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools import CalculatorTool, WeatherMockTool, TextProcessorTool
from agents import AgentController
from agents.router import heuristic_route
from app import app

client = TestClient(app)


def test_calculator_tool():
    assert CalculatorTool("2 + 2") == "4"
    assert CalculatorTool("10 * 5") == "50"
    assert CalculatorTool("sqrt(100)") == "10"
    assert CalculatorTool("abs(-25)") == "25"
    assert CalculatorTool("round(3.14159, 2)") == "3.14"
    assert CalculatorTool("") == "Expression is empty"
    assert CalculatorTool("10 / 0") == "Calculation error: division by zero"
    assert "Invalid math expression" in CalculatorTool("some random text")


def test_weather_mock_tool():
    res = WeatherMockTool("London")
    assert "London" in res
    assert "°C" in res
    assert WeatherMockTool("   ") == "Please provide a city name"

    # Verify temporal noise filtering
    res_today = WeatherMockTool("Toronto today")
    assert "Toronto:" in res_today


def test_text_processor_tool():
    assert TextProcessorTool("hello", "uppercase") == "HELLO"
    assert TextProcessorTool("WORLD", "lowercase") == "world"
    assert TextProcessorTool("code", "reverse") == "edoc"
    assert "3 words" in TextProcessorTool("one two three", "word_count")
    assert "Unknown action" in TextProcessorTool("test", "nonexistent")


def test_heuristic_router_weather_variations():
    test_cases = [
        ("forecast Toronto for today?", "Toronto"),
        ("forecast Toronto for tomorrow", "Toronto"),
        ("weather in London tomorrow", "London"),
        ("what is the weather today in Paris", "Paris"),
        ("weather in Tokyo next week", "Tokyo"),
        ("current temperature in Berlin this weekend", "Berlin"),
    ]

    for prompt, expected_city in test_cases:
        tool, args = heuristic_route(prompt)
        assert tool == "WeatherMockTool"
        assert args["city"] == expected_city


def test_agent_missing_api_key_uses_fallback():
    # If no api key is configured, agent should seamlessly use fallback router
    controller = AgentController(api_key="")
    res = controller.execute("forecast Toronto for today?")
    assert res["tool_used"] == "WeatherMockTool"
    assert "Toronto" in res["result"]
    assert len(res["steps"]) >= 4


@patch("agents.base.genai.Client")
def test_agent_execution_trace(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client

    mock_call = MagicMock()
    mock_call.name = "CalculatorTool"
    mock_call.args = {"expression": "5 * 5"}

    mock_resp = MagicMock()
    mock_resp.function_calls = [mock_call]
    mock_resp.text = None
    mock_client.models.generate_content.return_value = mock_resp

    controller = AgentController(api_key="fake-test-key")
    res = controller.execute("5 * 5")

    assert res["tool_used"] == "CalculatorTool"
    assert res["result"] == "25"
    assert len(res["steps"]) >= 4
    assert "Step 1: Received input" in res["steps"][0]
    assert "Step 2: Selected tool: CalculatorTool" in res["steps"][1]
    assert "Step 3: Tool result: 25" in res["steps"][2]
    assert "Step 4: Returning result to user" in res["steps"][3]


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_empty_input_rejected():
    res = client.post("/api/task", json={"input": "   "})
    assert res.status_code == 400


@patch("app.agent_controller.execute")
def test_task_crud_flow(mock_exec):
    mock_exec.return_value = {
        "result": "HELLO WORLD",
        "tool_used": "TextProcessorTool",
        "duration_ms": 12.5,
        "steps": [
            'Step 1: Received input "Convert hello world to uppercase"',
            'Step 2: Selected tool: TextProcessorTool',
            'Step 3: Tool result: HELLO WORLD',
            'Step 4: Returning result to user',
        ],
    }

    # 1. Create task
    post_res = client.post("/api/task", json={"input": "Convert hello world to uppercase"})
    assert post_res.status_code == 201
    data = post_res.json()
    task_id = data["id"]
    assert data["result"] == "HELLO WORLD"
    assert data["tool_used"] == "TextProcessorTool"
    assert len(data["steps"]) == 4

    # 2. Get task by ID
    get_res = client.get(f"/api/tasks/{task_id}")
    assert get_res.status_code == 200
    assert get_res.json()["steps"] == data["steps"]

    # 3. List tasks
    list_res = client.get("/api/tasks")
    assert list_res.status_code == 200
    assert any(t["id"] == task_id for t in list_res.json())

    # 4. Delete task
    del_res = client.delete(f"/api/tasks/{task_id}")
    assert del_res.status_code == 200
    assert del_res.json() == {"deleted": True}
