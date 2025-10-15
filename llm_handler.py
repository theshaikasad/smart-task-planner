import os
import json
import json5
import re
import ast
import time
from datetime import datetime, timedelta
from typing import Dict, List
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

class LLMTaskPlanner:
    def __init__(self):
        self.api_key = os.getenv("HF_API_KEY")
        if not self.api_key:
            raise ValueError("Missing Hugging Face API key. Set HF_API_KEY in .env file.")

        # ✅ Models (primary and backup)
        self.primary_model = "openai/gpt-oss-120b"
        self.backup_model = "meta-llama/Llama-3.1-8B-Instruct"

        # ✅ Create HF inference client
        self.hf_client = InferenceClient(token=self.api_key)

    # ------------------------
    # PROMPT CREATION
    # ------------------------
    def create_task_breakdown_prompt(self, goal: str, deadline: str) -> str:
        return f"""You are an expert project manager. Break down this goal into actionable tasks with realistic timelines.

Goal: {goal}
Deadline: {deadline}

Create a detailed task breakdown following this EXACT JSON structure (return ONLY valid JSON, no other text):

{{
    "tasks": [
        {{
            "name": "Task name",
            "description": "What needs to be done",
            "duration": "2 days",
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD",
            "dependencies": [],
            "priority": "high",
            "category": "Planning"
        }}
    ],
    "critical_path": ["Task 1", "Task 3"],
    "estimated_total_time": "2 weeks",
    "risk_factors": ["Risk 1", "Risk 2"],
    "recommendations": ["Recommendation 1"]
}}

Requirements:
1. Create 5–8 specific, actionable tasks
2. Include realistic durations (hours/days)
3. Set proper start/end dates before {deadline}
4. Identify dependencies between tasks
5. Assign priorities: high, medium, or low
6. List critical path tasks
7. Identify 2–3 risk factors
8. Provide 2–3 recommendations

Return ONLY the JSON object — no explanations, no markdown formatting."""

    # ------------------------
    # QUERY API USING CHAT COMPLETIONS
    # ------------------------
    def query_hf_api(self, messages: List[Dict], model: str, max_retries: int = 3):
        """Query Hugging Face chat API with retry logic."""
        for attempt in range(max_retries):
            try:
                response = self.hf_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=3000,
                    temperature=0.3,
                    top_p=0.9,
                )
                return response
            except Exception as e:
                print(f"⚠️ Attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                else:
                    raise Exception(f"API request failed after {max_retries} attempts: {e}")

    # ------------------------
    # GENERATE PLAN
    # ------------------------
    def generate_task_plan(self, goal: str, deadline: str) -> Dict:
        prompt = self.create_task_breakdown_prompt(goal, deadline)
        messages = [
            {"role": "system", "content": "You are a helpful project planning assistant."},
            {"role": "user", "content": prompt},
        ]

        try:
            # Try primary model
            response = self.query_hf_api(messages, self.primary_model)
        except Exception as e:
            print(f"⚠️ Primary model failed: {e}")
            # Try backup model
            response = self.query_hf_api(messages, self.backup_model)

        # Extract text safely
        generated_text = (
            response.choices[0].message["content"]
            if hasattr(response, "choices") and response.choices
            else ""
        ).strip()

        # Remove code fences and extra text
        generated_text = re.sub(r"^```(json)?|```$", "", generated_text, flags=re.DOTALL).strip()

        # Optional: Remove lines before first '{' and after last '}'
        start_idx = generated_text.find("{")
        end_idx = generated_text.rfind("}") + 1
        if start_idx != -1 and end_idx != -1:
            generated_text = generated_text[start_idx:end_idx]

        # Use json5 to parse "almost JSON" (single quotes, trailing commas)
        try:
            result = json5.loads(generated_text)
        except Exception as e:
            print(f"⚠️ JSON parse failed with json5: {e}")
            print("Raw LLM output:", generated_text)
            # Fallback
            return {
                "tasks": self.generate_fallback_tasks(goal, deadline),
                "critical_path": [],
                "estimated_total_time": "Unknown",
                "risk_factors": ["Invalid LLM response"],
                "recommendations": ["Please retry or verify input."]
            }

        # Validate structure
        if "tasks" not in result or not isinstance(result["tasks"], list):
            print("⚠️ Invalid task structure — using fallback tasks.")
            result["tasks"] = self.generate_fallback_tasks(goal, deadline)

        return result

    # ------------------------
    # FALLBACK TASKS
    # ------------------------
    def generate_fallback_tasks(self, goal: str, deadline: str) -> List[Dict]:
        """Generate a basic fallback task plan when LLM fails."""
        try:
            deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
            start_date = datetime.now()
            total_days = max(5, (deadline_date - start_date).days)
            task_duration = max(1, total_days // 5)

            return [
                {
                    "name": "Research & Planning",
                    "description": f"Research and create a detailed plan for: {goal}",
                    "duration": f"{task_duration} days",
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": (start_date + timedelta(days=task_duration)).strftime("%Y-%m-%d"),
                    "dependencies": [],
                    "priority": "high",
                    "category": "Planning",
                },
                {
                    "name": "Implementation",
                    "description": "Develop and integrate the main components.",
                    "duration": f"{task_duration * 2} days",
                    "start_date": (start_date + timedelta(days=task_duration)).strftime("%Y-%m-%d"),
                    "end_date": (start_date + timedelta(days=task_duration * 3)).strftime("%Y-%m-%d"),
                    "dependencies": ["Research & Planning"],
                    "priority": "high",
                    "category": "Development",
                },
                {
                    "name": "Testing & Review",
                    "description": "Test features, fix bugs, and finalize project.",
                    "duration": f"{task_duration} days",
                    "start_date": (start_date + timedelta(days=task_duration * 3)).strftime("%Y-%m-%d"),
                    "end_date": deadline_date.strftime("%Y-%m-%d"),
                    "dependencies": ["Implementation"],
                    "priority": "medium",
                    "category": "Testing",
                },
            ]
        except Exception:
            return [{"name": "Project Planning", "description": "Basic fallback", "duration": "2 days"}]
