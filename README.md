# Exam Countdown Planner

[![Verify project](https://github.com/savinaysingh7/exam-countdown-agen/actions/workflows/ci.yml/badge.svg)](https://github.com/savinaysingh7/exam-countdown-agen/actions/workflows/ci.yml)

A Python study-planning agent that uses Groq tool calling to create a day-by-day revision plan for an exam. Built for T29, it demonstrates a bounded Think -> Act -> Observe loop with explicit tools and persistent state.

## Features

- Creates a revision schedule from an exam date and subject list.
- Retains earlier subjects when a user adds a new subject in a later turn.
- Rejects dates that are today or in the past instead of creating an invalid plan.
- Prints every model step, tool call, and tool observation for demonstration and debugging.

## How it works

1. The model decides whether to answer or call a tool.
2. The Python runtime executes only tools in a whitelist registry.
3. Each tool result is appended to the conversation as an observation.
4. The model receives that observation and decides the next action, up to `max_steps`.

The agent has dual memory: `self.messages` stores the conversation transcript, while `self.state` stores deterministic data such as the exam date, days remaining, topics, schedule, and latest validation error.

## Setup

Prerequisite: Python 3.10 or later and a [Groq API key](https://console.groq.com/keys).

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Set your key in `.env`:

```ini
GROQ_API_KEY=your_groq_api_key_here
```

Never commit `.env`; it is excluded by `.gitignore`.

## Run the demo

```powershell
python demo.py
```

The demo shows three scenarios: an initial plan, a stateful topic addition, and an honest invalid-date response.

## Test

The unit tests cover deterministic tool behavior and do not make API calls:

```powershell
python -m unittest discover -s tests -v
```

GitHub Actions runs this command for every push and pull request to `main`.

## Tools

The agent uses two tools: `set_exam(date_str)` and `allocate_topics(topics)`. `set_exam` parses an exam date, validates it against the fixed demo date, and calculates the exact number of days remaining. `allocate_topics` spreads subjects across the available days; days with no allocated subject are shown as revision days.

## Memory

The agent uses a dual-memory architecture. First, the LLM transcript (`self.messages`) persists across turns, allowing the model to retain conversational context. Second, a Python state dictionary (`self.state`) stores exact values such as the exam date, days left, saved topics, and schedule. The topic state makes an added subject deterministic even if the model supplies only that new subject on a later turn.

## Honest Failure

During testing, an exam date in the past or on the fixed demo date would have produced a broken zero-day schedule. The `set_exam` tool returns a validation error when `days_left <= 0`; that observation is appended to the transcript, so the agent can honestly explain that a multi-day plan is impossible instead of inventing one. An empty-model-response fallback still surfaces the same error.
