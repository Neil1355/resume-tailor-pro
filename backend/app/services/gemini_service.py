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
            "You are an expert technical resume writer and ATS optimization specialist.\n\n"
            "Your task: Rewrite this resume's bullet points so they align with the role described below. "
            "The job description may contain paragraphs, mixed formatting, or unclear structure-extract "
            "the true responsibilities, required skills, and keywords before rewriting.\n\n"
            "Rewrite rules:\n"
            "- Preserve the original meaning and truthfulness of each bullet.\n"
            "- Match the tone, vocabulary, and skill emphasis of the job description.\n"
            "- Incorporate relevant keywords naturally (no keyword stuffing).\n"
            "- Keep each rewritten bullet approximately the same length as the original to avoid layout shifts.\n"
            "- Improve clarity, action verbs, and technical specificity.\n"
            "- Do NOT invent experience Neil does not have.\n\n"
            "Output format:\n"
            "Return ONLY a JSON object where:\n"
            "- Keys must remain exactly the provided tags (for example: bullet_1, bullet_2).\n"
            "- Values are the rewritten bullet text.\n\n"
            "Job Description (raw text, may be messy):\n"
            f"{job_description}\n\n"
            "Original Bullet Points:\n"
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
