"""
Day 3 — LLM-Based Agent with LangGraph ReAct Pattern
=====================================================
This agent replaces rule-based keyword matching (Day 1-2) with an LLM
(Google Gemini) that autonomously decides which tool to call based on
the user's natural-language query.

Architecture
────────────
  User Input → LLM (Gemini) → Tool Selection → Tool Execution → Response
                  ↑                                    │
                  └────────── intermediate result ─────┘  (ReAct loop)

Key Features
────────────
• LangGraph ReAct agent (modern replacement for deprecated AgentExecutor)
• 4 tools: Calculator, Weather, Summarizer, DateTime
• Structured JSON logging of every interaction
• Rich terminal UI with color-coded output
"""

import os
import sys
import time
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich import box

# LangChain / LangGraph imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

# Local modules
from tools import ALL_TOOLS
from logger import log_interaction, load_logs

# ──────────────────── Setup ────────────────────
load_dotenv(dotenv_path="../.env")

console = Console()

# Verify API key
if not os.getenv("GOOGLE_API_KEY"):
    console.print("[bold red]✘ GOOGLE_API_KEY not found in .env file![/]")
    sys.exit(1)

# ──────────────────── LLM & Agent ──────────────
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite-preview",
    temperature=0,
)

# Build the ReAct agent graph — the LLM decides which tool(s) to call
agent = create_react_agent(llm, ALL_TOOLS)


# ──────────────────── Helpers ──────────────────
def extract_tool_calls(messages):
    """Extract tool call info from the message history for logging."""
    tool_calls = []
    for msg in messages:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls.append({
                    "tool": tc["name"],
                    "input": str(tc["args"]),
                })
        if msg.type == "tool":
            tool_calls.append({
                "tool_output": msg.content,
            })
    return tool_calls


def run_agent_query(query: str) -> str:
    """Send a query to the agent and return the final response (with retry for rate limits)."""
    # Retry logic for Gemini free-tier rate limits
    for attempt in range(3):
        try:
            # Added system-level style instruction for brevity to save quota
            styled_query = f"[STRICT: Be extremely concise. Use short sentences/bullets.]\nUser: {query}"
            result = agent.invoke({"messages": [("user", styled_query)]})
            break
        except Exception as e:
            if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                wait = 15 * (attempt + 1)
                console.print(f"[yellow]⚠ Rate limited, retrying in {wait}s... ({attempt+1}/3)[/]")
                time.sleep(wait)
                if attempt == 2:
                    raise Exception("API rate limit exceeded. Please wait a minute and try again.")
            else:
                raise
    messages = result["messages"]

    # Extract tool usage for logging
    tool_info = extract_tool_calls(messages)
    tools_used = [t["tool"] for t in tool_info if "tool" in t]
    tool_inputs = [t["input"] for t in tool_info if "input" in t]

    final_answer = messages[-1].content
    if isinstance(final_answer, list):
        # Convert list of content blocks to string (common in modern Gemini model outputs)
        final_answer = "\n".join([str(c.get("text", c)) if isinstance(c, dict) else str(c) for c in final_answer])
    else:
        final_answer = str(final_answer)

    # Log the interaction
    log_interaction(
        user_input=query,
        tool_name=", ".join(map(str, tools_used)) if tools_used else "direct_llm",
        tool_input=", ".join(map(str, tool_inputs)) if tool_inputs else "N/A",
        output=final_answer,
    )

    return final_answer, tools_used


def show_logs():
    """Display recent logs in a pretty table."""
    logs = load_logs(5)
    if not logs:
        console.print("[dim]No logs yet.[/]")
        return

    table = Table(
        title="📋 Recent Agent Logs",
        box=box.ROUNDED,
        show_lines=True,
    )
    table.add_column("#", style="dim", width=3)
    table.add_column("Timestamp", style="cyan", width=20)
    table.add_column("User Input", style="white", width=30)
    table.add_column("Tool Selected", style="green", width=15)
    table.add_column("Output", style="yellow", max_width=40)

    for i, entry in enumerate(logs, 1):
        ts = str(entry.get("timestamp", "")).split("T")[-1][:8] if "T" in str(entry.get("timestamp", "")) else "Unknown"
        user_input = str(entry.get("user_input", ""))
        tool_selected = str(entry.get("tool_selected", ""))
        agent_output = str(entry.get("agent_output", ""))

        table.add_row(
            str(i),
            ts,
            user_input[:30],
            tool_selected,
            agent_output[:40] + "..." if len(agent_output) > 40 else agent_output,
        )
    console.print(table)


# ──────────────────── Main Loop ────────────────
def main():
    console.print(Panel.fit(
        "[bold cyan]🤖 Day 3 — LLM-Based Agent (LangGraph ReAct)[/]\n"
        "[dim]Powered by Google Gemini + LangGraph[/]\n\n"
        "Available tools: [green]Calculator[/], [blue]Weather[/], "
        "[magenta]Summarizer[/], [yellow]DateTime[/]\n\n"
        "Commands: [bold]logs[/] → view history  |  [bold]exit[/] → quit",
        border_style="bright_cyan",
        title="✦ Agentic AI Lab ✦",
    ))

    while True:
        console.print()
        query = console.input("[bold green]You ➤ [/]").strip()

        if not query:
            continue
        if query.lower() in ("exit", "quit", "q"):
            console.print("[dim]👋 Goodbye![/]")
            break
        if query.lower() == "logs":
            show_logs()
            continue

        with console.status("[bold cyan]🧠 Agent is thinking...[/]", spinner="dots"):
            try:
                answer, tools_used = run_agent_query(query)
            except Exception as e:
                console.print(f"[bold red]Error: {e}[/]")
                continue

        # Display tool usage
        if tools_used:
            tools_str = ", ".join(f"[green]{t}[/]" for t in tools_used)
            console.print(f"  [dim]🔧 Tools used: {tools_str}[/]")

        # Display the answer
        console.print(Panel(
            Markdown(answer),
            title="[bold yellow]Agent Response[/]",
            border_style="yellow",
            padding=(1, 2),
        ))


if __name__ == "__main__":
    main()