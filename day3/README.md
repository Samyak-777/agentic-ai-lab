# Day 3 — LLM-Based Agent

## Objective
Replace rule-based decision logic with a Large Language Model (Google Gemini) to autonomously decide which tool to invoke based on natural-language user queries.

## Architecture

```
User Input ──→ LLM (Gemini 3.1 Flash-Lite) ──→ Tool Selection ──→ Tool Execution ──→ Response
                       ↑                                           │
                       └──────── intermediate results ─────────────┘  (ReAct Loop)
```

## Key Concepts
- **ReAct Pattern**: The LLM reasons about which tool to use, acts by calling the tool, observes the result, and continues until it has a final answer.
- **LangGraph**: Modern replacement for the deprecated `AgentExecutor`, providing a graph-based execution model.
- **Tool Abstraction**: Tools are Python functions decorated with `@tool`, and the LLM receives their docstrings as function descriptions.

## Files

| File | Description |
|------|-------------|
| `agent.py` | Main agent loop with LangGraph ReAct agent and rich terminal UI |
| `tools.py` | Four tool definitions: Calculator, Weather, Summarizer, DateTime |
| `logger.py` | Structured JSON logging for every interaction |

## Tools Available

1. **Calculator** — Evaluates math expressions safely
2. **Weather** — Returns mock weather data for 6 cities
3. **Summarizer** — Extractive text summarization
4. **DateTime** — Returns current date and time

## How to Run

```bash
cd day3
python agent.py
```

## Example Queries
- `What is 25 * 4 + 10?`
- `What's the weather in Tokyo?`
- `Summarize: Artificial intelligence is transforming industries. It enables automation. It improves decision making.`
- `What is today's date?`
- `Calculate 2**10 and tell me the weather in Paris`

## Logging
All interactions are logged to `agent_logs.jsonl` with:
- Timestamp
- User input
- Tool selected by LLM
- Tool input arguments
- Agent output

Type `logs` during the session to view recent interactions in a formatted table.

## Key Improvement over Day 2
- **No more keyword matching** — The LLM understands intent from natural language
- **Multi-tool queries** — Can use multiple tools in a single query (e.g., "Calculate X and check weather in Y")
- **Conversational** — Handles follow-up and complex phrasing naturally
