from typing import Optional
import pytest

from app.extraction.cached import CachedClient
from app.extraction.factory import CompositeExtractionClient, get_client
from app.extraction.fallback import RegexFallback
from app.extraction.llm import LLMClient
from app.extraction.schema import ExtractedField, ExtractionResult
from app.extraction.verifier import verify_fields


class FakeLLM:
    """Mock LLM client executing offline with zero network calls."""

    def __init__(self, canned_result: Optional[ExtractionResult] = None):
        self.canned_result = canned_result

    def extract(
        self,
        text: str,
        today: str,
        class_hint: Optional[str] = None,
    ) -> ExtractionResult:
        if self.canned_result:
            return self.canned_result.model_copy(deep=True)
        # Default mock extraction matching standard 70-character message
        return ExtractionResult(
            language="en",
            llm_mode="fake",
            fields=[
                ExtractedField(type="class", value="8B", quote="8B"),
                ExtractedField(type="stated_count", value="3", quote="3 absent"),
                ExtractedField(type="absent_student", value="Rohan", quote="Rohan", roman="Rohan"),
                ExtractedField(type="absent_student", value="Aman", quote="Aman", roman="Aman"),
                ExtractedField(type="absent_student", value="Pooja", quote="Pooja", roman="Pooja"),
                ExtractedField(type="topic", value="Covered chapter 4", quote="Covered chapter 4"),
                ExtractedField(type="homework", value="Homework Ex 4.2", quote="Homework Ex 4.2"),
            ],
        )


def test_offsets_for_70_character_message():
    """
    For the 70-character message:
    '8B: 3 absent — Rohan, Aman, Pooja. Covered chapter 4. Homework Ex 4.2.'
    Offsets must be:
    class [0,2), count [4,12), Rohan [15,20), Aman [22,26), Pooja [28,33), topic [35,52), homework [54,69).
    """
    message = "8B: 3 absent — Rohan, Aman, Pooja. Covered chapter 4. Homework Ex 4.2."
    assert len(message) == 70, f"Expected 70 chars, got {len(message)}"

    fake_llm = FakeLLM()
    extracted = fake_llm.extract(message, today="2026-11-21")
    verified = verify_fields(message, extracted.fields)

    field_map = {f.type + (f"_{f.value}" if f.type == "absent_student" else ""): f for f in verified}

    # 1. class [0, 2)
    cls_f = field_map["class"]
    assert (cls_f.start, cls_f.end) == (0, 2)
    assert cls_f.status == "OK"

    # 2. count [4, 12)
    cnt_f = field_map["stated_count"]
    assert (cnt_f.start, cnt_f.end) == (4, 12)
    assert cnt_f.status == "OK"

    # 3. Rohan [15, 20)
    rohan_f = field_map["absent_student_Rohan"]
    assert (rohan_f.start, rohan_f.end) == (15, 20)
    assert rohan_f.status == "OK"

    # 4. Aman [22, 26)
    aman_f = field_map["absent_student_Aman"]
    assert (aman_f.start, aman_f.end) == (22, 26)
    assert aman_f.status == "OK"

    # 5. Pooja [28, 33)
    pooja_f = field_map["absent_student_Pooja"]
    assert (pooja_f.start, pooja_f.end) == (28, 33)
    assert pooja_f.status == "OK"

    # 6. topic [35, 52)
    top_f = field_map["topic"]
    assert (top_f.start, top_f.end) == (35, 52)
    assert top_f.status == "OK"

    # 7. homework [54, 69)
    hw_f = field_map["homework"]
    assert (hw_f.start, hw_f.end) == (54, 69)
    assert hw_f.status == "OK"


def test_fabricated_quote_becomes_review():
    """A quote that cannot be found in the message must get status='Review'."""
    message = "8A: 2 absent - Rohan, Aman. Covered lesson 3."
    fields = [
        ExtractedField(type="absent_student", value="Pooja", quote="Pooja Sharma"),
        ExtractedField(type="topic", value="Fake Topic", quote="Fabricated Topic Not Present"),
    ]

    verified = verify_fields(message, fields)
    for f in verified:
        assert f.status == "Review"
        assert f.start is None
        assert f.end is None
        assert f.reason == "quote not found in message"
        assert f.rule_id == "R1"


def test_unsupported_value_becomes_review():
    """If a quote is found but does not support the claimed value, status becomes Review."""
    message = "8B: 3 absent — Rohan, Aman, Pooja."
    fields = [
        # Claimed count 5 but quote is '3 absent'
        ExtractedField(type="stated_count", value="5", quote="3 absent"),
        # Claimed class 9A but quote is '8B'
        ExtractedField(type="class", value="9A", quote="8B"),
        # Claimed student Suresh but quote is 'Rohan'
        ExtractedField(type="absent_student", value="Suresh", quote="Rohan", roman="Suresh"),
    ]

    verified = verify_fields(message, fields)
    for f in verified:
        assert f.status == "Review"
        assert f.rule_id == "R1"
        assert f.start is not None  # Quote was found
        assert f.reason is not None  # Reason explains lack of support


def test_devanagari_message_roundtrip():
    """A Devanagari Hindi message round-trips with character spans and roman transliterations."""
    dev_text = "8A में आज 3 अनुपस्थित - कबीर, अयान, काव्या। पाठ 4 पढ़ाया। गृहकार्य अभ्यास 4.1।"

    fake_result = ExtractionResult(
        language="hi",
        fields=[
            ExtractedField(type="class", value="8A", quote="8A"),
            ExtractedField(type="date", value="2026-11-21", quote="आज"),
            ExtractedField(type="stated_count", value="3", quote="3 अनुपस्थित"),
            ExtractedField(type="absent_student", value="कबीर", quote="कबीर", roman="Kabir"),
            ExtractedField(type="absent_student", value="अयान", quote="अयान", roman="Ayaan"),
            ExtractedField(type="absent_student", value="काव्या", quote="काव्या", roman="Kavya"),
            ExtractedField(type="topic", value="पाठ 4 पढ़ाया", quote="पाठ 4 पढ़ाया"),
            ExtractedField(type="homework", value="गृहकार्य अभ्यास 4.1", quote="गृहकार्य अभ्यास 4.1"),
        ],
    )

    verified = verify_fields(dev_text, fake_result.fields)

    for f in verified:
        assert f.status == "OK"
        assert f.start is not None and f.end is not None
        # Verify the span in the original string matches the quote exactly
        assert dev_text[f.start : f.end] == f.quote

    # Check that Roman transliterations exist for names
    names = [f for f in verified if f.type == "absent_student"]
    assert len(names) == 3
    assert {n.roman for n in names} == {"Kabir", "Ayaan", "Kavya"}


def test_regex_fallback_hinglish_and_english():
    """RegexFallback extracts both standard English and Hinglish messages."""
    fallback = RegexFallback()

    # Hinglish message
    hi_msg = "8A: 2 absent the - Rohan, Aman. Chapter 4 padhaya. Homework Ex 4.2."
    hi_res = fallback.extract(hi_msg, today="2026-11-21")
    assert hi_res.language == "hinglish"
    verified_hi = verify_fields(hi_msg, hi_res.fields)
    assert all(f.status == "OK" for f in verified_hi)
    assert len([f for f in verified_hi if f.type == "absent_student"]) == 2

    # English message with em-dash
    en_msg = "8B: 3 absent — Rohan, Aman, Pooja. Covered chapter 4. Homework Ex 4.2."
    en_res = fallback.extract(en_msg, today="2026-11-21")
    assert en_res.language == "en"
    verified_en = verify_fields(en_msg, en_res.fields)
    assert all(f.status == "OK" for f in verified_en)


def test_cached_client():
    """CachedClient extracts pre-stored demo messages."""
    cached = CachedClient()
    demo_msg = "8A: 3 absent - Kabir, Ayaan, Kavya. Covered Chapter 3 Linear Equations. Homework Ex 3.2."
    res = cached.extract(demo_msg, today="2026-11-21")

    assert res.llm_mode == "cached"
    assert len(res.fields) == 7
    verified = verify_fields(demo_msg, res.fields)
    assert all(f.status == "OK" for f in verified)


def test_factory_cascades_on_gemini_failure():
    """CompositeExtractionClient falls back to RegexFallback and CachedClient on Gemini exception."""
    class FailingGeminiClient:
        def extract(self, text, today, class_hint=None):
            raise ConnectionError("Network unreachable in sandbox")

    client = CompositeExtractionClient(
        mode="gemini",
        gemini_client=FailingGeminiClient(),
        fallback_client=RegexFallback(),
        cached_client=CachedClient(),
    )

    msg = "8B: 3 absent — Rohan, Aman, Pooja. Covered chapter 4. Homework Ex 4.2."
    res, mode_used = client.extract_with_mode(msg, today="2026-11-21")

    assert mode_used == "fallback"
    assert res.llm_mode == "fallback"
    assert len(res.fields) >= 5
