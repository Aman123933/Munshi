import re
from datetime import date, datetime, timedelta
from typing import List, Optional

from app.extraction.schema import ExtractedField, ExtractionResult


DEVANAGARI_TRANSLIT = {
    "कबीर": "Kabir",
    "अयान": "Ayaan",
    "काव्या": "Kavya",
    "रोहन": "Rohan",
    "अमन": "Aman",
    "पूजा": "Pooja",
    "अर्जुन": "Arjun",
    "देव": "Dev",
    "रिया": "Riya",
    "सिमरन": "Simran",
    "अनन्या": "Ananya",
    "तन्वी": "Tanvi",
    "रेयांश": "Reyansh",
    "विवान": "Vivaan",
    "निशा": "Nisha",
    "दिया": "Diya",
    "सान्वी": "Saanvi",
    "आरोही": "Aarohi",
}


class RegexFallback:
    """
    Deterministic rule-based fallback extractor supporting:
    - Standard English: '8A: 3 absent - Rohan, Aman, Pooja. Covered chapter 4. Homework Ex 4.2.'
    - Hinglish: '8A: 3 absent the - Rohan, Aman, Pooja. Chapter 4 padhaya. Homework Ex 4.2.'
    - Devanagari Hindi: '8A में आज 3 अनुपस्थित - कबीर, अयान, काव्या। पाठ 4 पढ़ाया। गृहकार्य अभ्यास 4.1।'
    """

    def extract(
        self,
        text: str,
        today: str,
        class_hint: Optional[str] = None,
    ) -> ExtractionResult:
        fields: List[ExtractedField] = []
        raw = text.strip()

        # 1. Detect language
        has_devanagari = bool(re.search(r"[\u0900-\u097F]", raw))
        has_hinglish = bool(
            re.search(
                r"\b(padhaya|padhai|aaj|kal|parso|absent\s+the|nahi\s+aaye|bache|bachhe|homework\s+diya)\b",
                raw,
                re.IGNORECASE,
            )
        )
        if has_devanagari:
            language = "hi"
        elif has_hinglish:
            language = "hinglish"
        else:
            language = "en"

        # 2. Extract Class
        class_match = re.search(r"\b([6-9]|1[0-2])([A-Za-z])\b", raw)
        if class_match:
            c_quote = class_match.group(0)
            fields.append(
                ExtractedField(
                    type="class",
                    value=c_quote.upper(),
                    quote=c_quote,
                )
            )
        elif class_hint:
            hint_match = re.search(re.escape(class_hint), raw, re.IGNORECASE)
            if hint_match:
                fields.append(
                    ExtractedField(
                        type="class",
                        value=class_hint.upper(),
                        quote=hint_match.group(0),
                    )
                )

        # 3. Extract Date (ISO date YYYY-MM-DD / aaj / today / kal / yesterday / parso / आज / कल)
        iso_date_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", raw)
        today_date = date.fromisoformat(today) if isinstance(today, str) else today
        today_match = re.search(r"\b(today|aaj)\b|आज", raw, re.IGNORECASE)
        yesterday_match = re.search(r"\b(yesterday|kal)\b|कल", raw, re.IGNORECASE)
        parso_match = re.search(r"\b(parso)\b|परसों", raw, re.IGNORECASE)

        if iso_date_match:
            fields.append(
                ExtractedField(
                    type="date",
                    value=iso_date_match.group(1),
                    quote=iso_date_match.group(1),
                )
            )
        elif today_match:
            fields.append(
                ExtractedField(
                    type="date",
                    value=today_date.isoformat(),
                    quote=today_match.group(0),
                )
            )
        elif yesterday_match:
            yest_date = today_date - timedelta(days=1)
            fields.append(
                ExtractedField(
                    type="date",
                    value=yest_date.isoformat(),
                    quote=yesterday_match.group(0),
                )
            )
        elif parso_match:
            parso_date = today_date - timedelta(days=2)
            fields.append(
                ExtractedField(
                    type="date",
                    value=parso_date.isoformat(),
                    quote=parso_match.group(0),
                )
            )

        # 4. Extract Stated Count
        count_match = re.search(
            r"(\d+)\s*(?:absent(?:\s+the)?|students?\s+absent|bache\s+absent|अनुपस्थित|गैरहाजिर)",
            raw,
            re.IGNORECASE,
        )
        if count_match:
            quote_str = count_match.group(0)
            count_num = re.search(r"\d+", quote_str).group(0)
            fields.append(
                ExtractedField(
                    type="stated_count",
                    value=count_num,
                    quote=quote_str,
                )
            )

        # 5. Extract Absent Student Names
        # English / Hinglish
        names_segment_en = re.search(
            r"(?:absent(?:\s+the)?|absent\s*[:\-])\s*[\-—:]\s*([A-Za-z\s,]+?)(?=\s+on\s+\d|\.\s+|\.\s*$|(?:\s+[A-Z][a-z]+\s+chapter)|Covered|padhaya|Homework|\n)",
            raw,
            re.IGNORECASE,
        )
        # Devanagari Hindi
        names_segment_hi = re.search(
            r"(?:अनुपस्थित|गैरहाजिर)\s*[\-—:]\s*([\u0900-\u097F\s,]+?)(?=।|\.\s*|पाठ|गृहकार्य|\n|$)",
            raw,
        )

        if names_segment_en:
            names_block = names_segment_en.group(1)
            raw_names = re.split(r",|\band\b", names_block)
            for rn in raw_names:
                clean_name = rn.strip()
                if clean_name and re.match(r"^[A-Za-z]+(?:\s+[A-Za-z]+)?$", clean_name):
                    pos = raw.find(clean_name)
                    if pos != -1:
                        exact_quote = raw[pos : pos + len(clean_name)]
                        fields.append(
                            ExtractedField(
                                type="absent_student",
                                value=clean_name,
                                quote=exact_quote,
                                roman=clean_name,
                            )
                        )
        elif names_segment_hi:
            names_block = names_segment_hi.group(1)
            raw_names = names_block.split(",")
            for rn in raw_names:
                clean_name = rn.strip()
                if clean_name:
                    pos = raw.find(clean_name)
                    if pos != -1:
                        exact_quote = raw[pos : pos + len(clean_name)]
                        roman_name = DEVANAGARI_TRANSLIT.get(clean_name, clean_name)
                        fields.append(
                            ExtractedField(
                                type="absent_student",
                                value=clean_name,
                                quote=exact_quote,
                                roman=roman_name,
                            )
                        )

        # 6. Extract Topic
        topic_match_en = re.search(r"(Covered\s+[^.\n]+)", raw, re.IGNORECASE)
        topic_match_hi_rom = re.search(r"((?:Aaj\s+)?[^.\n]+?\s+padhaya)", raw, re.IGNORECASE)
        topic_match_hi_dev = re.search(r"(पाठ\s+[^।\n]+?\s+पढ़ाया|[^।\n]+?\s+पढ़ाया)", raw)

        if topic_match_en:
            fields.append(
                ExtractedField(
                    type="topic",
                    value=topic_match_en.group(1).strip(),
                    quote=topic_match_en.group(1).strip(),
                )
            )
        elif topic_match_hi_rom:
            fields.append(
                ExtractedField(
                    type="topic",
                    value=topic_match_hi_rom.group(1).strip(),
                    quote=topic_match_hi_rom.group(1).strip(),
                )
            )
        elif topic_match_hi_dev:
            fields.append(
                ExtractedField(
                    type="topic",
                    value=topic_match_hi_dev.group(1).strip(),
                    quote=topic_match_hi_dev.group(1).strip(),
                )
            )

        # 7. Extract Homework
        hw_match_en = re.search(r"(Homework\s+[^.\n]+(?:\.\d+)?|H\.W\.?\s+[^.\n]+(?:\.\d+)?)", raw, re.IGNORECASE)
        hw_match_hi_dev = re.search(r"(गृहकार्य\s+[^।\n]+)", raw)

        if hw_match_en:
            fields.append(
                ExtractedField(
                    type="homework",
                    value=hw_match_en.group(1).strip(),
                    quote=hw_match_en.group(1).strip(),
                )
            )
        elif hw_match_hi_dev:
            hw_str = hw_match_hi_dev.group(1).strip().rstrip("। ")
            fields.append(
                ExtractedField(
                    type="homework",
                    value=hw_str,
                    quote=hw_str,
                )
            )

        return ExtractionResult(fields=fields, language=language, llm_mode="fallback")
