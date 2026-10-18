from services.config.workout_config import PROMPT


class LLMCoach:
    def __init__(self, groq_client):
        self.client = groq_client
        self.history = []
        self.system_prompt = PROMPT
        self.model = self._resolve_model()

    def _resolve_model(self) -> str:
        preferred = [
            "qwen/qwen3.8-27b",
            "openai/gpt-oss-20b",
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant"
        ]
        try:
            available = [m.id for m in self.client.models.list().data]
            for m in preferred:
                if m in available:
                    return m
            return available[0] if available else "qwen/qwen3.8-27b"
        except Exception:
            return "qwen/qwen3.8-27b"

    def give_feedback(self, event, issue, context_info=None):
        prompt = f"Event: {event}"

        if context_info:
            prompt += f" Context: {context_info}"

        if issue:
            prompt += f" Form Issue: {issue}"

        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.history[-10:],
            {"role": "user", "content": prompt}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.4,
        )

        text = response.choices[0].message.content.strip()
        self.history.append({"role": "assistant", "content": text})

        return text
    