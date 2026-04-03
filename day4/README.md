# Day 4 — Multi-Step Planning Agent

## Objective
Design an agent that can break complex problems into multiple steps, execute them sequentially with context passing, and produce a consolidated final output.

## Architecture

```
User Query
    │
    ▼
┌─────────────────┐
│  LLM Planner    │  ← Decomposes query into ordered steps (JSON plan)
└────────┬────────┘      (Gemini 3.1 Pro Preview)
         │
    ┌────▼──────────────────────────────────────┐
    │  Step Executor (LangGraph ReAct Agent)    │
    │                                           │
    │  Step 1 → Tool → Result ──────┐           │
    │  Step 2 → Tool → Result ──────┤  context  │
    │  Step 3 → Tool → Result ──────┤  passing  │
    └───────────────────────────────┼───────────┘
                                    │
                               ┌────▼────┐
                               │  Final  │
                               │ Summary │
                               └─────────┘
```

## Key Concepts
- **Task Decomposition**: The LLM breaks a complex query into atomic, executable steps
- **Sequential Execution**: Each step receives the accumulated context from all previous steps
- **Planning + Acting**: Separate LLM calls for planning vs. execution (dual-LLM architecture)
- **Progress Tracking**: Every step has a status lifecycle: pending → running → done/failed

## Files

| File | Description |
|------|-------------|
| `agent.py` | Main agent with planning pipeline and rich terminal dashboard |
| `tools.py` | 7 tools: numbers extraction, average, statistics, calculator, summarizer, sort, datetime |
| `planner.py` | Custom planning module with step tracking, plan generation prompt |

## Tools Available

1. **extract_numbers** — Pull all numbers from natural text
2. **compute_average** — Calculate arithmetic mean
3. **compute_statistics** — Full stats: mean, median, std dev, min, max
4. **calculator** — Evaluate math expressions
5. **generate_summary** — Summarize text/results
6. **sort_numbers** — Sort a list of numbers
7. **get_current_datetime** — Get current date and time

## How to Run

```bash
cd day4
python agent.py
```

## Example Queries

1. **Basic multi-step**: `Find the average of 5, 10, 15 and summarize the result`
   - Step 1: Extract numbers → 5, 10, 15
   - Step 2: Compute average → 10.0
   - Step 3: Summarize → "The average of 5, 10, 15 is 10.0"

2. **Complex pipeline**: `Extract numbers from 'scores are 88, 92, 75, 100', compute stats, and sort them`
   - Step 1: Extract → 88, 92, 75, 100
   - Step 2: Statistics → mean=88.75, median=90, ...
   - Step 3: Sort → 75, 88, 92, 100

3. **Chained calculation**: `Calculate (25+35)*2, then find the average of that with 100 and 200`
   - Step 1: Calculate → 120
   - Step 2: Average of 120, 100, 200 → 140

## Interactive Commands
- `examples` — Show example queries
- `demo` — Run the first example query automatically
- `exit` — Quit the agent

## Key Improvement over Day 3
- **Planning phase**: The agent first creates a plan, then executes it
- **Context passing**: Each step receives results from all previous steps
- **Intermediate visibility**: You can see every step's result as it executes
- **Progress tracking**: Live progress bar shows execution progress
