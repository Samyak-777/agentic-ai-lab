"""
Day 3 — Tool Definitions for LLM-Based Agent
=============================================
Each tool is decorated with @tool so LangChain/LangGraph can
automatically generate the function-calling schema for the LLM.
"""

import datetime
import json
from langchain.tools import tool


# ──────────────────────────────────────────────
# Tool 1 : Calculator
# ──────────────────────────────────────────────
@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression and return the numeric result.
    Use this whenever the user asks to calculate, compute, or solve a math problem.
    Examples of valid expressions: '2+3', '25*4', '(10+20)/3', '2**8'."""
    try:
        # Only allow safe math operations
        allowed_chars = set("0123456789+-*/.() ")
        if not all(ch in allowed_chars for ch in expression):
            return "Error: expression contains disallowed characters."
        result = eval(expression)
        return f"{expression} = {result}"
    except ZeroDivisionError:
        return "Error: Division by zero."
    except Exception as e:
        return f"Error evaluating expression: {e}"


# ──────────────────────────────────────────────
# Tool 2 : Weather Lookup (mocked)
# ──────────────────────────────────────────────
@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city. Use this when the user asks about 
    weather, temperature, or climate conditions in a specific location."""
    mock_data = {
        "london":    {"temp": "14°C", "condition": "Rainy 🌧️",  "humidity": "82%"},
        "tokyo":     {"temp": "22°C", "condition": "Sunny ☀️",  "humidity": "55%"},
        "new york":  {"temp": "10°C", "condition": "Cloudy ☁️", "humidity": "68%"},
        "delhi":     {"temp": "38°C", "condition": "Hot 🔥",    "humidity": "30%"},
        "sydney":    {"temp": "20°C", "condition": "Clear 🌤️",  "humidity": "60%"},
        "paris":     {"temp": "16°C", "condition": "Overcast ☁️","humidity": "75%"},
    }
    info = mock_data.get(city.lower().strip())
    if info:
        return (f"Weather in {city.title()}: {info['temp']}, "
                f"{info['condition']}, Humidity {info['humidity']}")
    return f"Weather data not available for '{city}'. Try: London, Tokyo, New York, Delhi, Sydney, Paris."


# ──────────────────────────────────────────────
# Tool 3 : Text Summarizer
# ──────────────────────────────────────────────
@tool
def summarize_text(text: str) -> str:
    """Summarize a given block of text into a concise version.
    Use this when the user asks to summarize, shorten, or condense text."""
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    if len(sentences) <= 2:
        return text  # already short enough
    # Keep the first and last sentence as a simple extractive summary
    summary = f"{sentences[0]}. ... {sentences[-1]}."
    return f"Summary ({len(sentences)} sentences → 2): {summary}"


# ──────────────────────────────────────────────
# Tool 4 (Bonus) : Date & Time
# ──────────────────────────────────────────────
@tool
def get_datetime(query: str) -> str:
    """Get the current date and/or time. Use this when the user asks 
    'what time is it', 'what is today's date', or similar."""
    now = datetime.datetime.now()
    return f"Current date & time: {now.strftime('%A, %B %d, %Y — %I:%M %p')}"


# Convenience list for the agent builder
ALL_TOOLS = [calculator, get_weather, summarize_text, get_datetime]
