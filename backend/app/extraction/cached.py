import json
from pathlib import Path
from typing import Dict, Optional

from app.extraction.schema import ExtractionResult


class CachedClient:
    """Client for retrieving pre-computed extractions for demo messages."""

    def __init__(self, cache_file: Optional[Path] = None):
        if cache_file is None:
            cache_file = Path(__file__).resolve().parent / "cache.json"
        self.cache_file = cache_file
        self._cache: Dict[str, dict] = self._load_cache()

    def _load_cache(self) -> Dict[str, dict]:
        if not self.cache_file.exists():
            return {}
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def extract(
        self,
        text: str,
        today: str,
        class_hint: Optional[str] = None,
    ) -> ExtractionResult:
        clean_text = text.strip()
        if clean_text in self._cache:
            entry = self._cache[clean_text]
            result = ExtractionResult.model_validate(entry)
            result.llm_mode = "cached"
            return result

        # Also attempt normalized whitespace lookup
        norm_key = " ".join(clean_text.split())
        for k, entry in self._cache.items():
            if " ".join(k.split()) == norm_key:
                result = ExtractionResult.model_validate(entry)
                result.llm_mode = "cached"
                return result

        raise KeyError(f"Message not found in extraction cache: '{clean_text[:50]}...'")
