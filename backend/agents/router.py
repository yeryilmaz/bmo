import re

# Quick intent matcher for fallback routing when LLM is unavailable
WEATHER_KEYWORDS = ("weather", "forecast", "temperature", "temp")
CITY_PATTERN = re.compile(r"\b(?:in|for|forecast)\s+([A-Za-z]+)", re.IGNORECASE)
MATH_CLEANUP = re.compile(r"(?i)calculate|what is|evaluate|\?")


def heuristic_route(prompt: str) -> tuple[str, dict]:
    query = prompt.strip()
    q_lower = query.lower()

    # Weather queries
    if any(k in q_lower for k in WEATHER_KEYWORDS):
        match = CITY_PATTERN.search(query)
        target_city = match.group(1) if match else "Current Location"
        return "WeatherMockTool", {"city": target_city.title()}

    # String operations (uppercase, lowercase, reverse)
    for act in ("uppercase", "lowercase", "reverse"):
        if act in q_lower:
            quoted = re.findall(r"['\"](.+?)['\"]", query)
            payload = quoted[0] if quoted else re.sub(rf"(?i){act}|to|in", "", query).strip()
            return "TextProcessorTool", {"text": payload, "action": act}

    # Word counting check
    if "word count" in q_lower or "count words" in q_lower:
        quoted = re.findall(r"['\"](.+?)['\"]", query)
        payload = quoted[0] if quoted else re.sub(r"(?i)count\s+words|word\s+count|in|for", "", query).strip()
        return "TextProcessorTool", {"text": payload, "action": "word_count"}

    # Default everything else to math expression evaluator
    clean_expr = MATH_CLEANUP.sub("", query).strip()
    return "CalculatorTool", {"expression": clean_expr}

