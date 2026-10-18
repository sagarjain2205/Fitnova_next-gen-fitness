import json
import os
import re

from services.config.workout_config import PROMPT


class LLMCoach:
    def __init__(self, groq_client):
        self.client = groq_client
        self.system_prompt = PROMPT
        self.model = self._resolve_model()

    def _resolve_model(self) -> str:
        configured = os.environ.get("GROQ_MODEL", "").strip()
        preferred = [
            configured,
            "qwen/qwen3.8-27b",
            "openai/gpt-oss-20b",
            "openai/gpt-oss-120b",
            "llama-3.3-70b-versatile",
        ]
        preferred = [model for model in preferred if model]

        try:
            available = {model.id for model in self.client.models.list().data}
            for model in preferred:
                if model in available:
                    return model
        except Exception:
            # Keep coaching startup independent of model-list API availability.
            pass

        return configured or "qwen/qwen3.8-27b"

    def give_feedback(self, event, issue=None, context_info=None):
        request = {
            "event": event,
            "exercise": (context_info or {}).get("exercise"),
            "detected_form_signals": (context_info or {}).get("detected_form_signals", {}),
            "current_metrics": (context_info or {}).get("metrics", {}),
            "additional_context": (context_info or {}).get("additional_context", {}),
        }
        if issue:
            request["issue"] = issue
        if (context_info or {}).get("pose_detected") is False:
            request["pose_detected"] = False

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": json.dumps(request, ensure_ascii=False)},
            ],
            temperature=0.55,
            max_tokens=80,
        )

        text = response.choices[0].message.content or ""
        text = re.sub(r"<[^>]*>", " ", text)
        text = re.sub(r"\s+", " ", text).strip().strip("\"'` ")
        if not text:
            raise ValueError("Groq returned an empty coaching response")
        return text
