import json
import logging
import os
import time
from datetime import date, datetime, timedelta
from typing import Optional, Protocol, runtime_checkable

from pydantic import ValidationError

from app.extraction.schema import ExtractedField, ExtractionResult

logger = logging.getLogger(__name__)

PROMPT_VERSION = "v1"


@runtime_checkable
class LLMClient(Protocol):
    """Protocol for all Munshi LLM extraction clients."""

    def extract(
        self,
        text: str,
        today: str,
        class_hint: Optional[str] = None,
    ) -> ExtractionResult:
        """Extract structured entities from message text."""
        ...


def build_system_instruction(today: str, class_hint: Optional[str] = None) -> str:
    hint_line = f"Class hint: The teacher is assigned to class '{class_hint}'." if class_hint else ""
    return f"""You are the extraction engine for Munshi, an intelligent classroom assistant for Indian schools.
Prompt Version: {PROMPT_VERSION}
Today's Date: {today}
{hint_line}

Your role is to extract typed fields from a single teacher message (English, Hindi, or Hinglish) into JSON conforming to the schema.

STRICT EXTRACTION RULES:
1. Exact Quotes: For every field, the `quote` MUST be copied verbatim from the message text, character-for-character. Never invent quotes.
2. Names & Romanisation:
   - Emit exactly one `absent_student` field per absent student name.
   - For names, `roman` is the English / Latin transliteration (e.g. for Devanagari 'कबीर', quote='कबीर', value='कबीर', roman='Kabir').
   - `roman` is ONLY used for names; leave it null/None for all other field types.
3. Field Types:
   - 'class': class section label (e.g. '8A', '9B').
   - 'date': ISO format YYYY-MM-DD. Resolve relative words using today ({today}):
     * 'today' / 'aaj' / 'आज' -> {today}
     * 'yesterday' / 'kal' / 'कल' -> yesterday's date
     * 'parso' / 'परसों' -> day before yesterday's date
   - 'stated_count': string of the integer count of absent students stated in the message (e.g. '3').
   - 'absent_student': one field per absent student name.
   - 'topic': class diary topic, lesson, or chapter taught.
   - 'homework': homework or assignment assigned to students.
4. Faithful Extraction:
   - Extract only what the message explicitly states.
   - NEVER invent or guess names, classes, or dates.
   - If unsure about a field, leave it out.
5. Language Detection:
   - Return language as 'en' (English), 'hi' (Devanagari Hindi), or 'hinglish' (Hinglish).
"""


class GeminiClient:
    """Gemini API client using google-genai SDK."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: float = 15.0,
    ):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model_name = (
            model_name
            or os.environ.get("GEMINI_MODEL")
            or "gemini-1.5-flash"
        )
        self.timeout = timeout
        self.prompt_version = PROMPT_VERSION

    def extract(
        self,
        text: str,
        today: str,
        class_hint: Optional[str] = None,
    ) -> ExtractionResult:
        """Call Gemini with structured output, retrying once on failure."""
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set or empty.")

        from google import genai
        from google.genai import types

        client = genai.Client(
            api_key=self.api_key,
            http_options=types.HttpOptions(timeout=int(self.timeout * 1000)),
        )

        system_instruction = build_system_instruction(today, class_hint)

        user_content = f"Message:\n{text}\n\nToday: {today}"
        if class_hint:
            user_content += f"\nAssigned Class: {class_hint}"

        last_err = None
        for attempt in range(2):  # 1 retry on failure
            try:
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=user_content,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.0,
                        response_mime_type="application/json",
                        response_schema=ExtractionResult,
                    ),
                )

                raw_text = response.text
                if not raw_text:
                    raise ValueError("Gemini returned empty response text")

                data = json.loads(raw_text)
                result = ExtractionResult.model_validate(data)
                result.llm_mode = "gemini"
                return result

            except Exception as e:
                last_err = e
                logger.warning(f"GeminiClient extraction attempt {attempt + 1} failed: {e}")
                if attempt == 0:
                    time.sleep(1.0)  # Brief delay before retry

        raise RuntimeError(f"GeminiClient failed after 2 attempts: {last_err}") from last_err
