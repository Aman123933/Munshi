import re
from typing import List, Optional, Tuple

from app.extraction.schema import ExtractedField


def find_quote_span(text: str, quote: str) -> Optional[Tuple[int, int]]:
    """
    Locates the character offsets [start, end) of a quote in text.
    First tries exact match. If missing, attempts whitespace and case-normalised regex matching.
    """
    if not quote:
        return None

    # 1. Exact match
    idx = text.find(quote)
    if idx != -1:
        return idx, idx + len(quote)

    # 2. Whitespace and case-normalised matching
    words = [re.escape(w) for w in quote.strip().split() if w]
    if words:
        pattern = r"\s+".join(words)
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.start(), match.end()

    return None


def verify_field_support(field: ExtractedField) -> Tuple[bool, Optional[str]]:
    """
    Verifies that the quote actually supports the value.
    - stated_count quote must contain that number
    - class quote must contain the class label
    - absent_student quote must contain the name
    """
    quote_lower = field.quote.lower().strip()
    val_str = str(field.value).strip()

    if field.type == "stated_count":
        # Extract digits from value (e.g. "3" from 3 or "3")
        num_match = re.search(r"\d+", val_str)
        if num_match:
            digit = num_match.group(0)
            if digit not in field.quote:
                return False, f"stated_count quote '{field.quote}' does not contain number {digit}"
        elif val_str.lower() not in quote_lower:
            return False, f"stated_count quote '{field.quote}' does not contain {val_str}"

    elif field.type == "class":
        clean_label = val_str.upper().strip()
        if clean_label not in field.quote.upper():
            return False, f"class quote '{field.quote}' does not contain class {clean_label}"

    elif field.type == "absent_student":
        name_val = val_str.lower().strip()
        name_roman = (field.roman or "").lower().strip()
        # Name should match either directly or via roman transliteration
        if (name_val not in quote_lower) and (name_roman not in quote_lower):
            return False, f"name quote '{field.quote}' does not contain name {field.value}"

    return True, None


def verify_fields(text: str, fields: List[ExtractedField]) -> List[ExtractedField]:
    """
    Computes [start, end) offsets for every field and applies Rule R1.
    If quote not found -> status="Review", reason="quote not found in message"
    If quote doesn't support value -> status="Review", reason="<support failure>"
    Otherwise -> status="OK"
    """
    verified: List[ExtractedField] = []

    for f in fields:
        field = f.model_copy()
        span = find_quote_span(text, field.quote)

        if span is None:
            field.start = None
            field.end = None
            field.status = "Review"
            field.rule_id = "R1"
            field.reason = "quote not found in message"
            verified.append(field)
            continue

        field.start, field.end = span

        # Check support
        supported, reason = verify_field_support(field)
        if not supported:
            field.status = "Review"
            field.rule_id = "R1"
            field.reason = reason
        else:
            field.status = "OK"
            field.rule_id = "R1"
            field.reason = None

        verified.append(field)

    return verified
