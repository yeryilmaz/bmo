import math
import random
import re

SAFE_MATH = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "abs": abs,
    "round": round,
    "pi": math.pi,
    "e": math.e,
}

WEATHER_CONDITIONS = ["Sunny", "Partly Cloudy", "Rainy", "Clear", "Overcast", "Windy"]
TIME_FILTERS = ("today", "tomorrow", "tonight", "yesterday", "this week", "this weekend")


def CalculatorTool(expression: str) -> str:
    expr = (expression or "").strip()
    if not expr:
        return "Expression is empty"

    try:
        # evaluate in sandboxed namespace
        val = eval(expr, {"__builtins__": {}}, SAFE_MATH)

        if isinstance(val, float) and val.is_integer():
            return str(int(val))
        return str(val)
    except ZeroDivisionError:
        return "Calculation error: division by zero"
    except SyntaxError:
        return "Invalid math expression: please provide numbers or mathematical operations"
    except Exception as err:
        return f"Calculation error: {err}"


def WeatherMockTool(city: str) -> str:
    raw = (city or "").strip()
    if not raw:
        return "Please provide a city name"

    # strip common time adverbs if passed into the tool query
    cleaned = raw
    for term in TIME_FILTERS:
        cleaned = re.sub(rf"\b{term}\b", "", cleaned, flags=re.IGNORECASE)

    cleaned = cleaned.strip(" ,.-/?!")
    target = cleaned if cleaned else raw.strip()

    condition = random.choice(WEATHER_CONDITIONS)
    temp = random.randint(14, 28)
    humidity = random.randint(40, 75)

    return f"{target.title()}: {temp}°C, {condition} (Humidity: {humidity}%)"


def TextProcessorTool(text: str, action: str) -> str:
    txt = text or ""
    act = (action or "").strip().lower()

    if act == "uppercase":
        return txt.upper()
    if act == "lowercase":
        return txt.lower()
    if act == "reverse":
        return txt[::-1]
    if act == "word_count":
        return f"{len(txt.split())} words"

    return f"Unknown action: {action}"

