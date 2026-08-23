from tools import CalculatorTool, WeatherMockTool, TextProcessorTool

# All tools the agent can call
AVAILABLE_TOOLS = [CalculatorTool, WeatherMockTool, TextProcessorTool]

# Quick lookup by name
TOOL_MAP: dict = {fn.__name__: fn for fn in AVAILABLE_TOOLS}
