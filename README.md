# Agentic AI Lab — Software Lab Assignment

> This repository contains my progressive implementation of Agentic AI systems, moving from simple rule-based heuristics to multi-step reasoning using LangChain and LLMs

## Repository Structure

```
agentic-ai-lab/
├── day1/           → Rule-Based AI Agent
├── day2/           → Tool-Using Agent
├── day3/           → LLM-Based Agent (LangGraph + Gemini)
├── day4/           → Multi-Step Planning Agent
├── .env            → API keys (not committed)
├── .gitignore
└── README.md
```

## Assignment Overview

| Day | Title | Key Concept | Framework |
|-----|-------|-------------|-----------|
| 1 | Rule-Based Agent | Input → Decision → Action pipeline | Pure Python |
| 2 | Tool-Using Agent | Modular tools, function calling | Pure Python |
| 3 | LLM-Based Agent | LLM replaces keyword matching | LangChain + LangGraph |
| 4 | Multi-Step Planner | Task decomposition + sequential execution | LangGraph ReAct |

## Tech Stack

- **Language**: Python 3.9+
- **LLM**: Google Gemini 3.1 Series (Pro / Flash / Flash-Lite Preview)
- **Agent Framework**: LangChain + LangGraph (ReAct pattern)
- **UI**: Rich (terminal dashboards)

## Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd agentic-ai-lab

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install langchain langchain-google-genai langgraph python-dotenv rich

# 4. Set up API key
echo GOOGLE_API_KEY=your_key_here > .env

# 5. Run any day
cd day3
python agent.py
```

## Progression

```
Day 1: if/elif keyword matching     → "calculate 2+3"
Day 2: Modular tools + routing      → tools.py + agent.py
Day 3: LLM decides which tool       → Natural language understanding
Day 4: LLM plans + executes steps   → Complex multi-step reasoning
```
