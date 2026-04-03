import datetime

def calculator_tool(expression):
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error calculating: {e}"

def weather_tool(location):
    # Mocked API response
    mock_weather = {
        "london": "15°C and Rainy",
        "tokyo": "22°C and Sunny",
        "new york": "10°C and Cloudy"
    }
    return mock_weather.get(location.lower(), f"Weather data not available for {location}.")

def summarizer_tool(text):
    # Simple logic: truncate to first sentence or 50 characters
    sentences = text.split('.')
    return sentences[0] + "." if len(sentences) > 0 else text[:50] + "..."