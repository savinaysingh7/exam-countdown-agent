# Exam Countdown Planner

A Python study-planning agent that uses Groq tool calling to create a day-by-day revision plan for an exam. It was built for T29 and demonstrates a bounded Think → Act → Observe loop.

## Setup and run

1. Create and activate a Python virtual environment.
2. Install the dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env`, then set `GROQ_API_KEY` to your Groq API key.
4. Run `python demo.py` to see the three example traces.

Never commit `.env`; it is excluded by `.gitignore`.

## Tools
The agent uses two tools: `set_exam(date_str)` and `allocate_topics(topics)`. `set_exam` parses an exam date, validates it against the fixed demo date, and calculates the exact number of days remaining. `allocate_topics` spreads subjects across the available days; days with no allocated subject are shown as revision days.

## Memory
The agent uses a dual-memory architecture. First, the LLM transcript (`self.messages`) persists across turns, allowing the model to retain conversational context. Second, a Python state dictionary (`self.state`) stores exact values such as the exam date, days left, saved topics, and schedule. The topic state makes an added subject deterministic even if the model supplies only that new subject on a later turn.

## Honest Failure
During testing, an exam date in the past or on the fixed demo date would have produced a broken zero-day schedule. The `set_exam` tool returns a validation error when `days_left <= 0`; that observation is appended to the transcript, so the agent can honestly explain that a multi-day plan is impossible instead of inventing one. An empty-model-response fallback still surfaces the same error.
