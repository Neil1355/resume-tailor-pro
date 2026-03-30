import json
import importlib
from typing import Any

genai: Any = importlib.import_module("google.generativeai")


class GeminiService:
    def __init__(self, api_key: str, timeout_seconds: int = 30) -> None:
        self.api_key = api_key
        self.model = None
        self.timeout_seconds = timeout_seconds

    def _ensure_model(self):
        if not self.api_key:
            raise TimeoutError("GOOGLE_API_KEY is missing for Gemini API calls.")
        if self.model is None:
            genai.configure(api_key=self.api_key)
            # Pick a model that explicitly supports generateContent.
            try:
                available_models = genai.list_models()
                model_names = [
                    m.name
                    for m in available_models
                    if "generateContent" in getattr(m, "supported_generation_methods", [])
                ]

                if not model_names:
                    raise RuntimeError(
                        "No generative models available in your account. "
                        "Visit https://aistudio.google.com to verify your API key and available models."
                    )

                preferred_order = [
                    "models/gemini-1.5-flash",
                    "models/gemini-1.5-pro",
                    "models/gemini-pro",
                ]
                chosen_model_name = next(
                    (name for name in preferred_order if name in model_names),
                    model_names[0],
                )
                self.model = genai.GenerativeModel(chosen_model_name)
                return self.model
            except Exception as e:
                raise RuntimeError(
                    f"Failed to list or initialize Gemini models: {e}. "
                    "Check your API key and account tier in Google AI Studio."
                )
        return self.model

    def rewrite_bullets(self, job_description: str, original_bullets: dict[str, str]) -> dict[str, str]:
        bullet_lines = "\n".join(
            [f"{tag}: {text}" for tag, text in original_bullets.items()]
        )

        prompt = (
            "You are a professional resume writer. Rephrase the following experience bullet "
            "points from Neil's resume to match these keywords. Constraint: Keep the sentence "
            "length similar to the original to prevent layout shifts. Return only a JSON object "
            "mapping the tag names to the new text.\n\n"
            "Job Description:\n"
            f"{job_description}\n\n"
            "Original bullet points:\n"
            f"{bullet_lines}\n"
        )

        model = self._ensure_model()
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"},
            request_options={"timeout": self.timeout_seconds},
        )

        response_text = (response.text or "").strip()
        if not response_text:
            raise TimeoutError("Gemini did not return content in time.")

        rewritten = json.loads(response_text)
        if not isinstance(rewritten, dict):
            raise ValueError("Gemini response was not a valid object.")

        return {str(k): str(v) for k, v in rewritten.items()}
