import logging
import os
from typing import Optional, Tuple

from app.extraction.cached import CachedClient
from app.extraction.fallback import RegexFallback
from app.extraction.llm import GeminiClient, LLMClient
from app.extraction.schema import ExtractionResult

logger = logging.getLogger(__name__)


class CompositeExtractionClient:
    """
    Unified extraction client that respects LLM_MODE and cascades:
    Gemini -> RegexFallback -> CachedClient
    """

    def __init__(
        self,
        mode: Optional[str] = None,
        gemini_client: Optional[GeminiClient] = None,
        fallback_client: Optional[RegexFallback] = None,
        cached_client: Optional[CachedClient] = None,
    ):
        self.mode = (mode or os.environ.get("LLM_MODE", "gemini")).lower().strip()
        self.gemini = gemini_client or GeminiClient()
        self.fallback = fallback_client or RegexFallback()
        self.cached = cached_client or CachedClient()

    def extract(
        self,
        text: str,
        today: str,
        class_hint: Optional[str] = None,
    ) -> ExtractionResult:
        result, _ = self.extract_with_mode(text, today, class_hint)
        return result

    def extract_with_mode(
        self,
        text: str,
        today: str,
        class_hint: Optional[str] = None,
    ) -> Tuple[ExtractionResult, str]:
        """
        Extracts entities and returns (ExtractionResult, mode_used).
        mode_used will be 'gemini', 'fallback', or 'cached'.
        """
        if self.mode == "gemini":
            try:
                res = self.gemini.extract(text, today, class_hint)
                res.llm_mode = "gemini"
                return res, "gemini"
            except Exception as e:
                logger.warning(f"Gemini client failed ({e}); falling back to RegexFallback")

            # Fall back to RegexFallback
            try:
                res = self.fallback.extract(text, today, class_hint)
                if res and res.fields:
                    res.llm_mode = "fallback"
                    return res, "fallback"
            except Exception as e:
                logger.warning(f"RegexFallback failed ({e}); falling back to CachedClient")

            # Fall back to CachedClient
            try:
                res = self.cached.extract(text, today, class_hint)
                res.llm_mode = "cached"
                return res, "cached"
            except Exception as e:
                logger.error(f"CachedClient fallback also failed: {e}")
                # If cached also fails, return fallback output even if minimal
                res = self.fallback.extract(text, today, class_hint)
                res.llm_mode = "fallback"
                return res, "fallback"

        elif self.mode == "fallback":
            res = self.fallback.extract(text, today, class_hint)
            res.llm_mode = "fallback"
            return res, "fallback"

        elif self.mode == "cached":
            try:
                res = self.cached.extract(text, today, class_hint)
                res.llm_mode = "cached"
                return res, "cached"
            except KeyError:
                # If missing from cache, fallback to Regex
                res = self.fallback.extract(text, today, class_hint)
                res.llm_mode = "fallback"
                return res, "fallback"

        else:
            # Default fallback
            res = self.fallback.extract(text, today, class_hint)
            res.llm_mode = "fallback"
            return res, "fallback"


def get_client(mode: Optional[str] = None) -> CompositeExtractionClient:
    """Returns extraction client respecting LLM_MODE with graceful cascading."""
    return CompositeExtractionClient(mode=mode)
