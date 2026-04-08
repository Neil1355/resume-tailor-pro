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
            "You are an expert Technical Resume Writer and ATS Optimization Specialist.\n\n"
            "### CRITICAL FILTERING RULES ###\n"
            "The provided 'Job Description' may contain irrelevant 'rubbish' (e.g., salary, EEO statements, office perks, "
            "application instructions, or company history). You MUST:\n"
            "1. Mentally discard all administrative and non-functional text.\n"
            "2. Extract ONLY the core technical requirements, hard skills, and functional responsibilities.\n"
            "3. Use these extracted keywords to optimize the bullets provided below.\n\n"
            
            "### REWRITE RULES ###\n"
            "- PRESERVE TRUTH: Do not invent experience or add technologies not mentioned in the original bullets.\n"
            "- ATS OPTIMIZATION: Use the 'XYZ Formula' (Accomplished [X] as measured by [Y], by doing [Z]) where possible.\n"
            "- ACTION VERBS: Start every bullet with a strong, high-impact action verb (e.g., 'Engineered', 'Architected', 'Streamlined').\n"
            "- CONSTRAINTS: Keep rewritten bullets close to the original character count to prevent layout shifts.\n\n"
            
            "### OUTPUT FORMAT ###\n"
            "Return ONLY a JSON object. Keys must match the input tags (e.g., 'bullet_1'). Values are the rewritten text.\n\n"
            
            "### INPUT DATA ###\n"
            f"JOB DESCRIPTION (Raw):\n{job_description}\n\n"
            f"ORIGINAL BULLETS:\n{bullet_lines}\n"
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
