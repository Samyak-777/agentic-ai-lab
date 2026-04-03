"""
Day 4 — Multi-Step Planning Agent with Live Progress Dashboard
==============================================================
This agent demonstrates planning-based AI by:
  1. Taking a complex user query
  2. Using the LLM to decompose it into an ordered plan of steps
  3. Executing each step sequentially, feeding outputs into subsequent steps
  4. Showing intermediate results with a rich terminal dashboard
  5. Producing a final consolidated answer

Architecture
────────────
  User Query
      │
      ▼
  ┌─────────────────┐
  │  LLM Planner    │ ← Decomposes query into steps
  └────────┬────────┘
           │ 
      ┌────▼───────────────────────────────────────┐
      │  Step Executor (LangGraph ReAct Agent)     │
      │                                            │
      │  Step 1 → Tool Call → Result ──────┐       │
      │  Step 2 → Tool Call → Result ──────┤       │
      │  Step 3 → Tool Call → Result ──────┤       │
      │           ...                      │       │
      └────────────────────────────────────┼───────┘
                                           │
                                      ┌────▼────┐
                                      │  Final  │
                                      │ Summary │
                                      └─────────┘
"""

import os
import sys
import json
import time
from dotenv import load_dotenv

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import box

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from tools import ALL_TOOLS
from planner import ExecutionPlan, PlanStep, StepStatus, PLAN_GENERATION_PROMPT

# ──────────────────── Setup ────────────────────
load_dotenv(dotenv_path="../.env")

console = Console()

if not os.getenv("GOOGLE_API_KEY"):
    console.print("[bold red]✘ GOOGLE_API_KEY not found![/]")
    sys.exit(1)

# LLM instances - Using Flash-Lite for better rate-limit performance on free tier
planner_llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview", temperature=0.1)
executor_llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview", temperature=0)

# ReAct agent for step execution
step_agent = create_react_agent(executor_llm, ALL_TOOLS)


# ──────────────────── Plan Generation ──────────
def generate_plan(query: str) -> ExecutionPlan:
    """Use the LLM to decompose a user query into steps."""
    plan = ExecutionPlan(query=query)

    prompt = PLAN_GENERATION_PROMPT.format(query=query)
    response = planner_llm.invoke(prompt)
    raw = response.content.strip()

    # Clean markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]  # remove first line
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

    try:
        steps_data = json.loads(raw)
        for s in steps_data:
            plan.add_step(
                description=s.get("description", "Unknown step"),
                tool_hint=s.get("tool_hint"),
            )
    except json.JSONDecodeError:
        # Fallback: create a single step
        console.print("[yellow]⚠ Could not parse plan, using single-step mode[/]")
        plan.add_step(description="Execute the full query directly", tool_hint=None)

    return plan


def clean_content(content) -> str:
    """Ensure model output content is a string, even if multi-modal/list of blocks."""
    if isinstance(content, list):
        return "\n".join([str(c.get("text", c)) if isinstance(c, dict) else str(c) for c in content])
    return str(content or "")


# ──────────────────── Step Execution ───────────
def execute_step(step: PlanStep, context: str) -> str:
    """Execute a single step using the ReAct agent with accumulated context."""
    step.start()

    prompt = (
        f"You are executing step {step.index} of a multi-step plan.\n\n"
        f"Step description: {step.description}\n\n"
        f"Context from previous steps:\n{context}\n\n"
        f"Execute this step and return ONLY the result. BE EXTREMELY CONCISE. No fluff."
    )

    try:
        result = step_agent.invoke({"messages": [("user", prompt)]})
        answer = clean_content(result["messages"][-1].content)
        step.complete(answer)
        return answer
    except Exception as e:
        step.fail(str(e))
        return f"Error: {e}"


# ──────────────────── Display Helpers ──────────
def display_plan(plan: ExecutionPlan):
    """Show the execution plan as a tree diagram."""
    tree = Tree(f"[bold cyan]📋 Execution Plan[/] — [dim]{plan.query}[/]")

    for step in plan.steps:
        step_label = f"[bold]Step {step.index}:[/] {step.description}"
        if step.tool_hint:
            step_label += f" [dim](→ {step.tool_hint})[/]"

        icon = step.status.value.split(" ")[0]
        branch = tree.add(f"{icon} {step_label}")

        if step.result:
            result_preview = step.result[:80] + "..." if len(step.result) > 80 else step.result
            branch.add(f"[green]{result_preview}[/]")

    console.print(tree)


def display_final_summary(plan: ExecutionPlan):
    """Show the complete execution results."""
    table = Table(
        title="📊 Execution Results",
        box=box.DOUBLE_EDGE,
        show_lines=True,
        title_style="bold cyan",
    )
    table.add_column("Step", style="bold", width=5, justify="center")
    table.add_column("Description", style="white", width=30)
    table.add_column("Status", width=12, justify="center")
    table.add_column("Result", style="yellow", max_width=50)

    for step in plan.steps:
        table.add_row(
            str(step.index),
            step.description,
            step.status.value,
            step.result[:50] + "..." if step.result and len(step.result) > 50 else (step.result or "—"),
        )

    console.print(table)

    if plan.final_answer:
        console.print(Panel(
            Markdown(plan.final_answer),
            title="[bold green]✨ Final Answer[/]",
            border_style="green",
            padding=(1, 2),
        ))


# ──────────────────── Main Pipeline ────────────
def run_multi_step_agent(query: str):
    """Full pipeline: Plan → Execute each step → Summarize."""
    console.print(f"\n[bold cyan]🎯 Query:[/] {query}\n")

    # Phase 1: Generate Plan
    with console.status("[bold cyan]🧠 Generating execution plan...[/]", spinner="dots"):
        plan = generate_plan(query)

    console.print(f"[green]✓ Plan generated with {len(plan.steps)} steps[/]\n")
    display_plan(plan)
    console.print()

    # Phase 2: Execute Steps
    accumulated_context = f"Original query: {query}\n"

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        task = progress.add_task("Executing steps...", total=len(plan.steps))

        for step in plan.steps:
            progress.update(task, description=f"Step {step.index}: {step.description[:40]}...")

            result = execute_step(step, accumulated_context)
            accumulated_context += f"\nStep {step.index} result: {result}\n"

            progress.advance(task)

    console.print()

    # Phase 3: Generate Final Summary
    with console.status("[bold cyan]📝 Generating final summary...[/]", spinner="dots"):
        summary_prompt = (
            f"You completed a multi-step task. Here's what happened:\n\n"
            f"Original query: {query}\n\n"
            f"{accumulated_context}\n\n"
            f"Provide a clear, consolidated final answer to the original query. "
            f"Include all relevant intermediate values."
        )
        summary_result = step_agent.invoke({"messages": [("user", summary_prompt)]})
        plan.final_answer = clean_content(summary_result["messages"][-1].content)

    # Phase 4: Display Results
    display_plan(plan)
    console.print()
    display_final_summary(plan)


# ──────────────────── Interactive Mode ─────────
EXAMPLE_QUERIES = [
    "Find the average of 5, 10, 15 and summarize the result",
    "Extract numbers from 'scores are 88, 92, 75, 100', compute stats, and sort them",
    "Calculate (25 + 35) * 2, then find the average of the result with 100 and 200",
    "What is 2^10? Then take that number and compute its average with 512 and 2048",
]


def main():
    console.print(Panel.fit(
        "[bold cyan]🧠 Day 4 — Multi-Step Planning Agent[/]\n"
        "[dim]Task Decomposition • Sequential Execution • Live Progress[/]\n\n"
        "This agent breaks complex queries into steps, executes them\n"
        "sequentially, and shows intermediate results.\n\n"
        "Commands:\n"
        "  [bold]examples[/]  → show example queries\n"
        "  [bold]demo[/]      → run a demo query\n"
        "  [bold]exit[/]      → quit",
        border_style="bright_cyan",
        title="✦ Agentic AI Lab — Planning Agent ✦",
    ))

    while True:
        console.print()
        query = console.input("[bold green]You ➤ [/]").strip()

        if not query:
            continue
        if query.lower() in ("exit", "quit", "q"):
            console.print("[dim]👋 Goodbye![/]")
            break
        if query.lower() == "examples":
            console.print("\n[bold yellow]Example queries you can try:[/]")
            for i, eq in enumerate(EXAMPLE_QUERIES, 1):
                console.print(f"  [cyan]{i}.[/] {eq}")
            continue
        if query.lower() == "demo":
            query = EXAMPLE_QUERIES[0]
            console.print(f"[dim]Running demo query: {query}[/]")

        try:
            run_multi_step_agent(query)
        except Exception as e:
            console.print(f"[bold red]Error: {e}[/]")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
