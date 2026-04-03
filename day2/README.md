# Day 2 — Tool-Using Agent

## Objective
Enable a basic agent to interact with human-defined "tools" (functions) by manually routing intents to modular components.

## Approach
Built upon the Day 1 foundation, this assignment modularizes capabilities into separate tool functions and moves them into a dedicated file.

1. **Tool Abstraction**: Defined in `tools.py`, these functions handle specific logic (Calculator, Weather, Summarizer).
2. **Modular Architecture**:
   - `tools.py`: Houses the logic for external interactions.
   - `agent.py`: Houses the decision-making logic that routes inputs to tools.

### Tools Implemented
- **Calculator**: Safely evaluates math expressions.
- **Weather (Mocked)**: Simulates an API call with pre-defined responses for cities like Tokyo, London, and New York.
- **Summarizer**: Implements basic text shortening logic.

## Files
- `tools.py`: The tool library for the agent.
- `agent.py`: Main routing logic and user loop.

## How to Run
```bash
python agent.py
```
Example: `weather in Tokyo` or `summarize: [your text]`
