"""
Day 4 — Step Planner & Execution Tracker
=========================================
Provides a custom planning layer that:
  1. Uses the LLM to decompose a task into numbered steps
  2. Tracks each step's status (pending → running → done)
  3. Shows a live progress dashboard in the terminal
"""

import json
import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class StepStatus(Enum):
    PENDING = "⏳ pending"
    RUNNING = "🔄 running"
    DONE    = "✅ done"
    FAILED  = "❌ failed"


@dataclass
class PlanStep:
    """A single step in the execution plan."""
    index: int
    description: str
    tool_hint: Optional[str] = None
    status: StepStatus = StepStatus.PENDING
    result: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None

    def start(self):
        self.status = StepStatus.RUNNING
        self.started_at = datetime.datetime.now().isoformat()

    def complete(self, result: str):
        self.status = StepStatus.DONE
        self.result = result
        self.finished_at = datetime.datetime.now().isoformat()

    def fail(self, error: str):
        self.status = StepStatus.FAILED
        self.result = f"ERROR: {error}"
        self.finished_at = datetime.datetime.now().isoformat()


@dataclass 
class ExecutionPlan:
    """Holds the full plan and tracks progress."""
    query: str
    steps: List[PlanStep] = field(default_factory=list)
    final_answer: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())

    def add_step(self, description: str, tool_hint: str = None):
        step = PlanStep(
            index=len(self.steps) + 1,
            description=description,
            tool_hint=tool_hint,
        )
        self.steps.append(step)
        return step

    @property
    def progress(self) -> str:
        done = sum(1 for s in self.steps if s.status == StepStatus.DONE)
        total = len(self.steps)
        return f"{done}/{total}"

    @property
    def is_complete(self) -> bool:
        return all(s.status in (StepStatus.DONE, StepStatus.FAILED) for s in self.steps)

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "created_at": self.created_at,
            "steps": [
                {
                    "step": s.index,
                    "description": s.description,
                    "status": s.status.value,
                    "result": s.result,
                }
                for s in self.steps
            ],
            "final_answer": self.final_answer,
        }


PLAN_GENERATION_PROMPT = """You are an expert task planner. Given a user query, break it down into 
clear, sequential steps that can be executed one at a time.

User Query: {query}

Return ONLY a JSON array of step objects. Each step should have:
- "description": what this step does
- "tool_hint": which tool to use (one of: extract_numbers, compute_average, compute_statistics, calculator, generate_summary, sort_numbers, get_current_datetime) or null if no tool needed

Example output:
[
  {{"description": "Extract numbers from the query", "tool_hint": "extract_numbers"}},
  {{"description": "Calculate the average of the extracted numbers", "tool_hint": "compute_average"}},
  {{"description": "Summarize the results", "tool_hint": "generate_summary"}}
]

Return ONLY the JSON array, no markdown formatting or extra text."""
