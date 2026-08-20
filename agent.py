import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 1. Connect to the Free Groq API (Uses OpenAI SDK format)
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY"),
)
MODEL = "qwen/qwen3.6-27b" # Available model on Groq

# Fixed simulation date keeps the classroom trace reproducible.
DEMO_TODAY = datetime(2026, 8, 22)

# 2. The Tool Schemas (The only thing the model sees)
TOOL_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "set_exam",
            "description": "Sets the exam date and calculates days remaining. Use when the user gives an exam date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date_str": {"type": "string", "description": "Date in YYYY-MM-DD format."}
                },
                "required": ["date_str"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "allocate_topics",
            "description": "Creates a day-by-day schedule by distributing topics across remaining days. Use after exam date is set.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of topic names to study."
                    }
                },
                "required": ["topics"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are an intelligent Exam Countdown Planner.
Your goal is to help students plan their study schedule.
Use your tools to gather information and build the schedule.
After every tool result, read the observation before deciding the next action.
If a tool returns an error, explain it honestly and ask for the information needed to continue.
When the user adds a subject, use the existing subjects from the conversation and include the new subject in the regenerated plan.
When you have created the schedule, respond directly and stop calling tools."""

class ExamAgent:
    def __init__(self):
        # Memory Part 1: The LLM Transcript (Remembers conversation context)
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Memory Part 2: The Python State (Remembers exact math/dates for tools)
        self.state = {
            "exam_date": None,
            "days_left": 0,
            "topics": [],
            "schedule": {},
            "last_error": None,
        }
        self.tool_registry = {
            "set_exam": self._set_exam,
            "allocate_topics": self._allocate_topics,
        }

    def chat(self, user_input: str, max_steps: int = 5) -> str:
        self.messages.append({"role": "user", "content": user_input})

        # THE PLAN-ACT LOOP
        for step in range(1, max_steps + 1):
            print(f"\n--- Step {step} ---")

            response = client.chat.completions.create(
                model=MODEL,
                messages=self.messages,
                tools=TOOL_SCHEMA,
                tool_choice="auto"
            )

            message = response.choices[0].message

            # Append assistant reply to memory safely
            msg_dict = message.model_dump()
            msg_dict = {k: v for k, v in msg_dict.items() if v is not None}
            self.messages.append(msg_dict)

            # EXIT 1: Clean finish (No tool calls)
            if not message.tool_calls:
                final_answer = message.content or self.state["last_error"] or (
                    "I couldn't create a study plan. Please provide a future "
                    "exam date in YYYY-MM-DD format."
                )
                print(f"Agent Final Answer: {final_answer}")
                return final_answer

            # ACT & OBSERVE
            for tool_call in message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                print(f"Agent calls tool: {name} with args {args}")

                tool = self.tool_registry.get(name)
                result = tool(**args) if tool else f"Error: Unknown tool {name}"

                print(f"Tool Observation: {result}")
                if result.startswith("Error:"):
                    self.state["last_error"] = result.removeprefix("Error: ")
                else:
                    self.state["last_error"] = None

                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })

        return "Stopped: Max steps reached."

    # --- TOOL IMPLEMENTATIONS ---
    def _set_exam(self, date_str: str) -> str:
        try:
            exam_date = datetime.strptime(date_str, "%Y-%m-%d")
            days_left = (exam_date - DEMO_TODAY).days
            if days_left <= 0:
                return f"Error: The exam date {date_str} is in the past or today."
            self.state["exam_date"] = date_str
            self.state["days_left"] = days_left
            return f"Exam set to {date_str}. There are {days_left} days remaining."
        except ValueError:
            return "Error: Invalid date format. Please use YYYY-MM-DD."

    def _allocate_topics(self, topics: list) -> str:
        if not self.state["exam_date"]:
            return "Error: No exam date set. Please call set_exam first."

        # Preserve existing subjects when a later turn supplies only a new one.
        all_topics = list(self.state["topics"])
        for topic in topics:
            if topic not in all_topics:
                all_topics.append(topic)

        days = self.state["days_left"]
        schedule = {}
        num_topics = len(all_topics)

        # Algorithm to spread topics evenly across available days
        for i, topic in enumerate(all_topics):
            day_index = int(i * (days / num_topics)) if num_topics > 0 else 0
            day_num = day_index + 1
            if day_num not in schedule:
                schedule[day_num] = []
            schedule[day_num].append(topic)

        self.state["topics"] = all_topics
        self.state["schedule"] = schedule

        output = [f"Study Plan for {self.state['exam_date']} ({days} days left):"]
        for d in range(1, days + 1):
            day_topics = schedule.get(d, ["Rest / Revision"])
            output.append(f"Day {d}: {', '.join(day_topics)}")

        return "\n".join(output)
