"""
Day 4 — Tool Definitions for Multi-Step Planning Agent
======================================================
Reusable tools that the planning agent can chain together
in multi-step execution pipelines.
"""

import datetime
import statistics
import re
from langchain.tools import tool


@tool
def extract_numbers(text: str) -> str:
    """Extract all numbers from a given text and return them as a comma-separated list.
    Use this when you need to find numeric values embedded in text.
    Example: 'The scores are 5, 10, and 15' → '5, 10, 15'"""
    numbers = re.findall(r'-?\d+\.?\d*', text)
    if not numbers:
        return "No numbers found in the text."
    return ", ".join(numbers)


@tool
def compute_average(numbers_csv: str) -> str:
    """Compute the arithmetic average of a comma-separated list of numbers.
    Input should be numbers separated by commas like '5, 10, 15'.
    Returns the average value."""
    try:
        nums = [float(n.strip()) for n in numbers_csv.split(",") if n.strip()]
        if not nums:
            return "Error: No valid numbers provided."
        avg = statistics.mean(nums)
        return f"The average of [{numbers_csv.strip()}] is {avg:.2f}"
    except ValueError as e:
        return f"Error parsing numbers: {e}"


@tool
def compute_statistics(numbers_csv: str) -> str:
    """Compute detailed statistics (mean, median, std dev, min, max) for a 
    comma-separated list of numbers. Use this for comprehensive analysis."""
    try:
        nums = [float(n.strip()) for n in numbers_csv.split(",") if n.strip()]
        if not nums:
            return "Error: No valid numbers provided."
        result = {
            "count": len(nums),
            "mean": round(statistics.mean(nums), 2),
            "median": round(statistics.median(nums), 2),
            "min": min(nums),
            "max": max(nums),
        }
        if len(nums) > 1:
            result["std_dev"] = round(statistics.stdev(nums), 2)
        lines = [f"📊 Statistics for [{numbers_csv.strip()}]:"]
        for k, v in result.items():
            lines.append(f"  • {k}: {v}")
        return "\n".join(lines)
    except ValueError as e:
        return f"Error: {e}"


@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression and return the result.
    Use this for calculations like '2+3', '25*4', '(10+20)/3'."""
    try:
        allowed = set("0123456789+-*/.() ")
        if not all(ch in allowed for ch in expression):
            return "Error: expression contains disallowed characters."
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error: {e}"


@tool
def generate_summary(text: str) -> str:
    """Generate a concise summary of the given text or result.
    Use this as the final step to summarize findings."""
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    if len(sentences) <= 1:
        return f"Summary: {text}"
    return f"Summary: {sentences[0]}. {sentences[-1]}."


@tool
def sort_numbers(numbers_csv: str) -> str:
    """Sort a comma-separated list of numbers in ascending order.
    Input: '15, 3, 8, 1' → Output: '1, 3, 8, 15'"""
    try:
        nums = sorted([float(n.strip()) for n in numbers_csv.split(",") if n.strip()])
        formatted = ", ".join(str(int(n) if n == int(n) else n) for n in nums)
        return f"Sorted: [{formatted}]"
    except ValueError as e:
        return f"Error: {e}"


@tool
def get_current_datetime(query: str) -> str:
    """Get the current date and time."""
    now = datetime.datetime.now()
    return f"Current: {now.strftime('%A, %B %d, %Y at %I:%M %p')}"


# All tools available for the planning agent
ALL_TOOLS = [
    extract_numbers,
    compute_average,
    compute_statistics,
    calculator,
    generate_summary,
    sort_numbers,
    get_current_datetime,
]
