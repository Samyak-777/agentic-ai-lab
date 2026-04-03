# Day 1 — Rule-Based AI Agent

## Objective
Understand the concept of an AI agent using simple rule-based logic (keyword matching) to perform basic tasks.

## Approach
The agent is designed with a classic **Input → Decision → Action** pipeline:

1. **Input Handler**: Takes user natural language input and converts it to lowercase.
2. **Decision Logic**: Uses regular expressions and string matching to identify intent (e.g., "calculate", "date", "hello").
3. **Action Execution**: Performs the specific task associated with the intent.

### Implementation Details
- **Math**: Uses `re` to extract expressions and `eval()` for computation.
- **DateTime**: Uses Python's `datetime` module.
- **Greeting**: Simple string responses for user interaction.

## Files
- `agent.py`: Contains the `parse_input`, `execute_action`, and main interaction loop.

## How to Run
```bash
python agent.py
```
Example: `calculate 10 + 20` or `what is the current date?`
