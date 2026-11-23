import re
from typing import Any, Dict, List, Optional
from rapidfuzz import fuzz
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.helpers import get_roster
from app.models import ClassSection


def _get_other_sections(class_label: str, db: Optional[Session] = None) -> List[str]:
    """Finds all other section labels for the same class (e.g. for '8A' returns ['8B'])."""
    match = re.search(r"\d+", class_label)
    if not match:
        return []
    class_num = int(match.group(0))

    should_close = False
    session = db
    if session is None:
        session = SessionLocal()
        should_close = True

    try:
        sections = (
            session.query(ClassSection.label)
            .filter(ClassSection.class_num == class_num, ClassSection.label != class_label)
            .all()
        )
        return [s[0] for s in sections]
    finally:
        if should_close:
            session.close()


def resolve_name(
    roman_name: str,
    quote: str,
    class_label: str,
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """
    Roster resolver using RapidFuzz matching against class-section roster.
    
    Order of resolution:
    1. Roll number disambiguation (e.g. 'Kabir roll 806' or '806' in quote).
    2. Surname / full name exact disambiguation (e.g. 'Kabir Mehta').
    3. Exact first-name match first.
    4. token_set_ratio on full name.
    5. WRatio >= 85 on full name.
    6. Cross-section check for the same class (e.g. found in 8B instead of 8A).
    7. No fit anywhere: review with 'no student with this name in {class_label}'.
    """
    clean_name = (roman_name or quote or "").strip()
    clean_quote = (quote or "").strip()
    clean_class = class_label.strip().upper()

    roster = get_roster(clean_class, db=db)
    if not roster:
        return {
            "status": "review",
            "candidates": [],
            "resolved_student_id": None,
            "reason": f"Class {clean_class} has no students enrolled.",
        }

    # 1. Roll number disambiguation in quote or name (e.g. 'Kabir roll 806' or 'roll 801')
    roll_match = re.search(r"\b(?:roll(?:\s*no\.?)?\s*)?(\d{3,4})\b", f"{clean_quote} {clean_name}", re.IGNORECASE)
    if roll_match:
        roll_val = int(roll_match.group(1))
        matching_by_roll = [s for s in roster if s["roll_no"] == roll_val]
        if len(matching_by_roll) == 1:
            winner = matching_by_roll[0]
            return {
                "status": "resolved",
                "candidates": [
                    {
                        "student_id": winner["student_id"],
                        "name": winner["name"],
                        "roll_no": winner["roll_no"],
                        "score": 100.0,
                    }
                ],
                "resolved_student_id": winner["student_id"],
                "reason": None,
            }

    # 2. Exact full-name match in roster
    query_lower = clean_name.lower()
    exact_full = [s for s in roster if s["name"].lower() == query_lower or s["name"].lower() in clean_quote.lower()]
    if len(exact_full) == 1:
        winner = exact_full[0]
        return {
            "status": "resolved",
            "candidates": [
                {
                    "student_id": winner["student_id"],
                    "name": winner["name"],
                    "roll_no": winner["roll_no"],
                    "score": 100.0,
                }
            ],
            "resolved_student_id": winner["student_id"],
            "reason": None,
        }

    # 3. Exact first-name match
    first_name_query = clean_name.split()[0].lower()
    first_name_matches = [s for s in roster if s["first_name"].lower() == first_name_query]

    if first_name_matches:
        if len(first_name_matches) == 1:
            winner = first_name_matches[0]
            return {
                "status": "resolved",
                "candidates": [
                    {
                        "student_id": winner["student_id"],
                        "name": winner["name"],
                        "roll_no": winner["roll_no"],
                        "score": 100.0,
                    }
                ],
                "resolved_student_id": winner["student_id"],
                "reason": None,
            }
        else:
            # Multiple exact first-name matches (e.g. 3 Kabirs in 8A)
            # Check if full name in query/quote breaks the tie
            scored_candidates = []
            for m in first_name_matches:
                score = fuzz.token_set_ratio(clean_name, m["name"])
                scored_candidates.append((score, m))
            scored_candidates.sort(key=lambda x: (x[0], -x[1]["roll_no"]), reverse=True)

            # If top score is clearly distinct from the others (e.g. 'Kabir Mehta' vs 'Kabir Bansal')
            if scored_candidates[0][0] >= 90 and scored_candidates[1][0] < 80:
                winner = scored_candidates[0][1]
                return {
                    "status": "resolved",
                    "candidates": [
                        {
                            "student_id": winner["student_id"],
                            "name": winner["name"],
                            "roll_no": winner["roll_no"],
                            "score": float(scored_candidates[0][0]),
                        }
                    ],
                    "resolved_student_id": winner["student_id"],
                    "reason": None,
                }

            # Return review listing all candidates
            candidates_list = [
                {
                    "student_id": m["student_id"],
                    "name": m["name"],
                    "roll_no": m["roll_no"],
                    "score": 100.0,
                }
                for m in first_name_matches
            ]
            candidates_list.sort(key=lambda x: x["roll_no"])
            return {
                "status": "review",
                "candidates": candidates_list,
                "resolved_student_id": None,
                "reason": f"{clean_name} matches {len(first_name_matches)} students in {clean_class}. Choose one.",
            }

    # 4. token_set_ratio on full name
    token_scores = []
    for s in roster:
        score = fuzz.token_set_ratio(clean_name, s["name"])
        if score >= 85:
            token_scores.append((score, s))

    if token_scores:
        token_scores.sort(key=lambda x: x[0], reverse=True)
        if len(token_scores) == 1:
            winner = token_scores[0][1]
            return {
                "status": "resolved",
                "candidates": [
                    {
                        "student_id": winner["student_id"],
                        "name": winner["name"],
                        "roll_no": winner["roll_no"],
                        "score": float(token_scores[0][0]),
                    }
                ],
                "resolved_student_id": winner["student_id"],
                "reason": None,
            }
        else:
            candidates_list = [
                {
                    "student_id": s["student_id"],
                    "name": s["name"],
                    "roll_no": s["roll_no"],
                    "score": float(sc),
                }
                for sc, s in token_scores
            ]
            return {
                "status": "review",
                "candidates": candidates_list,
                "resolved_student_id": None,
                "reason": f"{clean_name} matches multiple candidates in {clean_class}.",
            }

    # 5. WRatio >= 85
    wratio_scores = []
    for s in roster:
        score = fuzz.WRatio(clean_name, s["name"])
        if score >= 85:
            wratio_scores.append((score, s))

    if wratio_scores:
        wratio_scores.sort(key=lambda x: x[0], reverse=True)
        if len(wratio_scores) == 1:
            winner = wratio_scores[0][1]
            return {
                "status": "resolved",
                "candidates": [
                    {
                        "student_id": winner["student_id"],
                        "name": winner["name"],
                        "roll_no": winner["roll_no"],
                        "score": float(wratio_scores[0][0]),
                    }
                ],
                "resolved_student_id": winner["student_id"],
                "reason": None,
            }
        else:
            candidates_list = [
                {
                    "student_id": s["student_id"],
                    "name": s["name"],
                    "roll_no": s["roll_no"],
                    "score": float(sc),
                }
                for sc, s in wratio_scores
            ]
            return {
                "status": "review",
                "candidates": candidates_list,
                "resolved_student_id": None,
                "reason": f"{clean_name} matches multiple candidates in {clean_class}.",
            }

    # 6. Check other sections of the same class
    other_sections = _get_other_sections(clean_class, db=db)
    for other_label in other_sections:
        other_roster = get_roster(other_label, db=db)
        # Check first name or token match in other section
        other_matches = [
            s
            for s in other_roster
            if s["first_name"].lower() == first_name_query
            or fuzz.token_set_ratio(clean_name, s["name"]) >= 85
        ]
        if other_matches:
            cands = [
                {
                    "student_id": s["student_id"],
                    "name": s["name"],
                    "roll_no": s["roll_no"],
                    "class_label": other_label,
                }
                for s in other_matches
            ]
            return {
                "status": "review",
                "candidates": cands,
                "resolved_student_id": None,
                "reason": f"No student named '{clean_name}' in {clean_class}, but found in {other_label}.",
            }

    # 7. No fit anywhere
    return {
        "status": "review",
        "candidates": [],
        "resolved_student_id": None,
        "reason": f"no student with this name in {clean_class}",
    }
