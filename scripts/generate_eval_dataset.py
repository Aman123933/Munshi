"""
Script to generate eval/messages.jsonl and eval/cache.json for Munshi evaluation harness.
All 60 messages are synthetic and written by the Munshi engineering team for this seeded roster.
"""

import json
from pathlib import Path

MESSAGES = [
    # =========================================================================
    # ENGLISH (20 messages: MSG01 to MSG20)
    # =========================================================================
    {
        "id": "MSG01",
        "language": "en",
        "text": "8A: 1 absent - Sneha Reddy on 2026-11-20. Covered Chapter 3 Linear Equations in Two Variables. Homework Ex 3.2.",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-20",
            "absent_students": ["MUN0052"],
            "topic": "Linear Equations in Two Variables",
            "homework": "Exercise 3.2"
        },
        "expected_status": "ready",
        "tags": ["standard", "ready", "en"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Sneha Reddy", "quote": "Sneha Reddy", "roman": "Sneha Reddy"},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "topic", "value": "Chapter 3 Linear Equations in Two Variables", "quote": "Covered Chapter 3 Linear Equations in Two Variables", "roman": None},
            {"type": "homework", "value": "Exercise 3.2", "quote": "Homework Ex 3.2", "roman": None}
        ]
    },
    {
        "id": "MSG02",
        "language": "en",
        "text": "8A: 1 absent - Aditya Das on 2026-11-19. Covered Chapter 4 Quadratic Equations. Homework Ex 4.1.",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-19",
            "absent_students": ["MUN0053"],
            "topic": "Quadratic Equations",
            "homework": "Exercise 4.1"
        },
        "expected_status": "ready",
        "tags": ["standard", "ready", "en"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Aditya Das", "quote": "Aditya Das", "roman": "Aditya Das"},
            {"type": "date", "value": "2026-11-19", "quote": "2026-11-19", "roman": None},
            {"type": "topic", "value": "Chapter 4 Quadratic Equations", "quote": "Covered Chapter 4 Quadratic Equations", "roman": None},
            {"type": "homework", "value": "Exercise 4.1", "quote": "Homework Ex 4.1", "roman": None}
        ]
    },
    {
        "id": "MSG03",
        "language": "en",
        "text": "8B: 1 absent - Ishaan Sharma on 2026-11-20. Covered Chapter 1 Number Systems & Real Numbers. Homework Ex 1.2 questions 1 to 5.",
        "teacher_id": "T01",
        "expected": {
            "class": "8B",
            "date": "2026-11-20",
            "absent_students": ["MUN0050"],
            "topic": "Number Systems & Real Numbers",
            "homework": "Exercise 1.2 questions 1 to 5"
        },
        "expected_status": "ready",
        "tags": ["standard", "ready", "en"],
        "cache_fields": [
            {"type": "class", "value": "8B", "quote": "8B", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Ishaan Sharma", "quote": "Ishaan Sharma", "roman": "Ishaan Sharma"},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "topic", "value": "Chapter 1 Number Systems & Real Numbers", "quote": "Covered Chapter 1 Number Systems & Real Numbers", "roman": None},
            {"type": "homework", "value": "Exercise 1.2 questions 1 to 5", "quote": "Homework Ex 1.2 questions 1 to 5", "roman": None}
        ]
    },
    {
        "id": "MSG04",
        "language": "en",
        "text": "8A: 2 absent - Kabir Bansal, Kabir Mehta on 2026-11-23. Covered Chapter 6 Coordinate Geometry. Homework Ex 6.1.",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-23",
            "absent_students": ["MUN0041", "MUN0046"],
            "topic": "Coordinate Geometry",
            "homework": "Exercise 6.1"
        },
        "expected_status": "ready",
        "tags": ["disambiguated", "ready", "en"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "stated_count", "value": "2", "quote": "2 absent", "roman": None},
            {"type": "absent_student", "value": "Kabir Bansal", "quote": "Kabir Bansal", "roman": "Kabir Bansal"},
            {"type": "absent_student", "value": "Kabir Mehta", "quote": "Kabir Mehta", "roman": "Kabir Mehta"},
            {"type": "date", "value": "2026-11-23", "quote": "2026-11-23", "roman": None},
            {"type": "topic", "value": "Chapter 6 Coordinate Geometry", "quote": "Covered Chapter 6 Coordinate Geometry", "roman": None},
            {"type": "homework", "value": "Exercise 6.1", "quote": "Homework Ex 6.1", "roman": None}
        ]
    },
    {
        "id": "MSG05",
        "language": "en",
        "text": "8A: 1 absent - Kabir on 2026-11-20. Covered Chapter 3 Linear Equations in Two Variables. Homework Ex 3.1.",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-20",
            "absent_students": ["MUN0041", "MUN0046", "MUN0051"],
            "topic": "Linear Equations in Two Variables",
            "homework": "Exercise 3.1"
        },
        "expected_status": "needs_review",
        "tags": ["name_collision", "needs_review", "en"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Kabir", "quote": "Kabir", "roman": "Kabir"},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "topic", "value": "Chapter 3 Linear Equations in Two Variables", "quote": "Covered Chapter 3 Linear Equations in Two Variables", "roman": None},
            {"type": "homework", "value": "Exercise 3.1", "quote": "Homework Ex 3.1", "roman": None}
        ]
    },
    {
        "id": "MSG06",
        "language": "en",
        "text": "8A: 1 absent - Ayaan on 2026-11-19. Covered Chapter 2 Polynomials & Algebraic Expressions. Homework Ex 2.3.",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-19",
            "absent_students": ["MUN0042", "MUN0048", "MUN0060"],
            "topic": "Polynomials & Algebraic Expressions",
            "homework": "Exercise 2.3"
        },
        "expected_status": "needs_review",
        "tags": ["name_collision", "needs_review", "en"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Ayaan", "quote": "Ayaan", "roman": "Ayaan"},
            {"type": "date", "value": "2026-11-19", "quote": "2026-11-19", "roman": None},
            {"type": "topic", "value": "Chapter 2 Polynomials & Algebraic Expressions", "quote": "Covered Chapter 2 Polynomials & Algebraic Expressions", "roman": None},
            {"type": "homework", "value": "Exercise 2.3", "quote": "Homework Ex 2.3", "roman": None}
        ]
    },
    {
        "id": "MSG07",
        "language": "en",
        "text": "9A: 1 absent - Arjun on 2026-11-20. Covered Chapter 5 Arithmetic Progressions. Homework Ex 5.2.",
        "teacher_id": "T01",
        "expected": {
            "class": "9A",
            "date": "2026-11-20",
            "absent_students": ["MUN0063", "MUN0077"],
            "topic": "Arithmetic Progressions",
            "homework": "Exercise 5.2"
        },
        "expected_status": "needs_review",
        "tags": ["name_collision", "needs_review", "en"],
        "cache_fields": [
            {"type": "class", "value": "9A", "quote": "9A", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Arjun", "quote": "Arjun", "roman": "Arjun"},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "topic", "value": "Chapter 5 Arithmetic Progressions", "quote": "Covered Chapter 5 Arithmetic Progressions", "roman": None},
            {"type": "homework", "value": "Exercise 5.2", "quote": "Homework Ex 5.2", "roman": None}
        ]
    },
    {
        "id": "MSG08",
        "language": "en",
        "text": "9A: 1 absent - Dev on 2026-11-23. Covered Chapter 7 Triangles & Congruence. Homework Theorem 7.1 proof.",
        "teacher_id": "T01",
        "expected": {
            "class": "9A",
            "date": "2026-11-23",
            "absent_students": ["MUN0069", "MUN0070"],
            "topic": "Triangles & Congruence",
            "homework": "Theorem 7.1 proof"
        },
        "expected_status": "needs_review",
        "tags": ["name_collision", "needs_review", "en"],
        "cache_fields": [
            {"type": "class", "value": "9A", "quote": "9A", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Dev", "quote": "Dev", "roman": "Dev"},
            {"type": "date", "value": "2026-11-23", "quote": "2026-11-23", "roman": None},
            {"type": "topic", "value": "Chapter 7 Triangles & Congruence", "quote": "Covered Chapter 7 Triangles & Congruence", "roman": None},
            {"type": "homework", "value": "Theorem 7.1 proof", "quote": "Homework Theorem 7.1 proof", "roman": None}
        ]
    },
    {
        "id": "MSG09",
        "language": "en",
        "text": "8B: 1 absent - Riya on 2026-11-20. Covered Chapter 2 Polynomials & Algebraic Expressions. Homework Ex 2.1.",
        "teacher_id": "T01",
        "expected": {
            "class": "8B",
            "date": "2026-11-20",
            "absent_students": ["MUN0044", "MUN0055"],
            "topic": "Polynomials & Algebraic Expressions",
            "homework": "Exercise 2.1"
        },
        "expected_status": "needs_review",
        "tags": ["name_collision", "needs_review", "en"],
        "cache_fields": [
            {"type": "class", "value": "8B", "quote": "8B", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Riya", "quote": "Riya", "roman": "Riya"},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "topic", "value": "Chapter 2 Polynomials & Algebraic Expressions", "quote": "Covered Chapter 2 Polynomials & Algebraic Expressions", "roman": None},
            {"type": "homework", "value": "Exercise 2.1", "quote": "Homework Ex 2.1", "roman": None}
        ]
    },
    {
        "id": "MSG10",
        "language": "en",
        "text": "8A: 3 absent - Sneha Reddy, Aditya Das on 2026-11-20. Covered Chapter 3 Linear Equations in Two Variables. Homework Ex 3.3.",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-20",
            "absent_students": ["MUN0052", "MUN0053"],
            "topic": "Linear Equations in Two Variables",
            "homework": "Exercise 3.3"
        },
        "expected_status": "needs_review",
        "tags": ["count_mismatch", "needs_review", "en"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "stated_count", "value": "3", "quote": "3 absent", "roman": None},
            {"type": "absent_student", "value": "Sneha Reddy", "quote": "Sneha Reddy", "roman": "Sneha Reddy"},
            {"type": "absent_student", "value": "Aditya Das", "quote": "Aditya Das", "roman": "Aditya Das"},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "topic", "value": "Chapter 3 Linear Equations in Two Variables", "quote": "Covered Chapter 3 Linear Equations in Two Variables", "roman": None},
            {"type": "homework", "value": "Exercise 3.3", "quote": "Homework Ex 3.3", "roman": None}
        ]
    },
    {
        "id": "MSG11",
        "language": "en",
        "text": "8A: 1 absent - Kavya Joshi, Nisha Saini on 2026-11-19. Covered Chapter 4 Quadratic Equations. Homework Ex 4.2.",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-19",
            "absent_students": ["MUN0049", "MUN0054"],
            "topic": "Quadratic Equations",
            "homework": "Exercise 4.2"
        },
        "expected_status": "needs_review",
        "tags": ["count_mismatch", "needs_review", "en"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Kavya Joshi", "quote": "Kavya Joshi", "roman": "Kavya Joshi"},
            {"type": "absent_student", "value": "Nisha Saini", "quote": "Nisha Saini", "roman": "Nisha Saini"},
            {"type": "date", "value": "2026-11-19", "quote": "2026-11-19", "roman": None},
            {"type": "topic", "value": "Chapter 4 Quadratic Equations", "quote": "Covered Chapter 4 Quadratic Equations", "roman": None},
            {"type": "homework", "value": "Exercise 4.2", "quote": "Homework Ex 4.2", "roman": None}
        ]
    },
    {
        "id": "MSG12",
        "language": "en",
        "text": "8B: 2 absent - Ishaan Sharma on 2026-11-20. Covered Chapter 1 Number Systems & Real Numbers. Homework Ex 1.3.",
        "teacher_id": "T01",
        "expected": {
            "class": "8B",
            "date": "2026-11-20",
            "absent_students": ["MUN0050"],
            "topic": "Number Systems & Real Numbers",
            "homework": "Exercise 1.3"
        },
        "expected_status": "needs_review",
        "tags": ["count_mismatch", "needs_review", "en"],
        "cache_fields": [
            {"type": "class", "value": "8B", "quote": "8B", "roman": None},
            {"type": "stated_count", "value": "2", "quote": "2 absent", "roman": None},
            {"type": "absent_student", "value": "Ishaan Sharma", "quote": "Ishaan Sharma", "roman": "Ishaan Sharma"},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "topic", "value": "Chapter 1 Number Systems & Real Numbers", "quote": "Covered Chapter 1 Number Systems & Real Numbers", "roman": None},
            {"type": "homework", "value": "Exercise 1.3", "quote": "Homework Ex 1.3", "roman": None}
        ]
    },
    {
        "id": "MSG13",
        "language": "en",
        "text": "8A: 1 absent - Sneha Reddy on 2026-11-22. Covered Chapter 3 Linear Equations in Two Variables. Homework Ex 3.2.",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-22",
            "absent_students": ["MUN0052"],
            "topic": "Linear Equations in Two Variables",
            "homework": "Exercise 3.2"
        },
        "expected_status": "blocked",
        "tags": ["sunday_date", "blocked", "en"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Sneha Reddy", "quote": "Sneha Reddy", "roman": "Sneha Reddy"},
            {"type": "date", "value": "2026-11-22", "quote": "2026-11-22", "roman": None},
            {"type": "topic", "value": "Chapter 3 Linear Equations in Two Variables", "quote": "Covered Chapter 3 Linear Equations in Two Variables", "roman": None},
            {"type": "homework", "value": "Exercise 3.2", "quote": "Homework Ex 3.2", "roman": None}
        ]
    },
    {
        "id": "MSG14",
        "language": "en",
        "text": "8A: 1 absent - Aditya Das on 2026-12-01. Covered Chapter 4 Quadratic Equations. Homework Ex 4.1.",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-12-01",
            "absent_students": ["MUN0053"],
            "topic": "Quadratic Equations",
            "homework": "Exercise 4.1"
        },
        "expected_status": "blocked",
        "tags": ["future_date", "blocked", "en"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Aditya Das", "quote": "Aditya Das", "roman": "Aditya Das"},
            {"type": "date", "value": "2026-12-01", "quote": "2026-12-01", "roman": None},
            {"type": "topic", "value": "Chapter 4 Quadratic Equations", "quote": "Covered Chapter 4 Quadratic Equations", "roman": None},
            {"type": "homework", "value": "Exercise 4.1", "quote": "Homework Ex 4.1", "roman": None}
        ]
    },
    {
        "id": "MSG15",
        "language": "en",
        "text": "7A: 1 absent - Manav Das on 2026-11-20. Covered Chapter 3 Linear Equations in Two Variables. Homework Ex 3.1.",
        "teacher_id": "T01",
        "expected": {
            "class": "7A",
            "date": "2026-11-20",
            "absent_students": ["MUN0024"],
            "topic": "Linear Equations in Two Variables",
            "homework": "Exercise 3.1"
        },
        "expected_status": "blocked",
        "tags": ["unassigned_class", "blocked", "en"],
        "cache_fields": [
            {"type": "class", "value": "7A", "quote": "7A", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Manav Das", "quote": "Manav Das", "roman": "Manav Das"},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "topic", "value": "Chapter 3 Linear Equations in Two Variables", "quote": "Covered Chapter 3 Linear Equations in Two Variables", "roman": None},
            {"type": "homework", "value": "Exercise 3.1", "quote": "Homework Ex 3.1", "roman": None}
        ]
    },
    {
        "id": "MSG16",
        "language": "en",
        "text": "10A: 1 absent - Aditya Jain on 2026-11-20. Covered Chapter 4 Quadratic Equations. Homework Ex 4.1.",
        "teacher_id": "T01",
        "expected": {
            "class": "10A",
            "date": "2026-11-20",
            "absent_students": ["MUN0081"],
            "topic": "Quadratic Equations",
            "homework": "Exercise 4.1"
        },
        "expected_status": "blocked",
        "tags": ["unassigned_class", "blocked", "en"],
        "cache_fields": [
            {"type": "class", "value": "10A", "quote": "10A", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Aditya Jain", "quote": "Aditya Jain", "roman": "Aditya Jain"},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "topic", "value": "Chapter 4 Quadratic Equations", "quote": "Covered Chapter 4 Quadratic Equations", "roman": None},
            {"type": "homework", "value": "Exercise 4.1", "quote": "Homework Ex 4.1", "roman": None}
        ]
    },
    {
        "id": "MSG17",
        "language": "en",
        "text": "8A: 1 absent - Kavya Joshi on 2026-11-20. Covered Chapter 7 Triangles & Congruence. No homework given today.",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-20",
            "absent_students": ["MUN0049"],
            "topic": "Triangles & Congruence",
            "homework": None
        },
        "expected_status": "ready",
        "tags": ["no_homework", "ready", "en"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Kavya Joshi", "quote": "Kavya Joshi", "roman": "Kavya Joshi"},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "topic", "value": "Chapter 7 Triangles & Congruence", "quote": "Covered Chapter 7 Triangles & Congruence", "roman": None}
        ]
    },
    {
        "id": "MSG18",
        "language": "en",
        "text": "8B: 1 absent - Aarav Singh on 2026-11-19. Covered Chapter 6 Coordinate Geometry. Practice during class, no homework assigned.",
        "teacher_id": "T01",
        "expected": {
            "class": "8B",
            "date": "2026-11-19",
            "absent_students": ["MUN0056"],
            "topic": "Coordinate Geometry",
            "homework": None
        },
        "expected_status": "ready",
        "tags": ["no_homework", "ready", "en"],
        "cache_fields": [
            {"type": "class", "value": "8B", "quote": "8B", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Aarav Singh", "quote": "Aarav Singh", "roman": "Aarav Singh"},
            {"type": "date", "value": "2026-11-19", "quote": "2026-11-19", "roman": None},
            {"type": "topic", "value": "Chapter 6 Coordinate Geometry", "quote": "Covered Chapter 6 Coordinate Geometry", "roman": None}
        ]
    },
    {
        "id": "MSG19",
        "language": "en",
        "text": "Good morning staff, please note the teacher council meeting is scheduled for 3 PM.",
        "teacher_id": "T01",
        "expected": {
            "class": None,
            "date": None,
            "absent_students": [],
            "topic": None,
            "homework": None
        },
        "expected_status": "blocked",
        "tags": ["short_unrelated", "blocked", "en"],
        "cache_fields": []
    },
    {
        "id": "MSG20",
        "language": "en",
        "text": "The monthly attendance register has been submitted to the office.",
        "teacher_id": "T01",
        "expected": {
            "class": None,
            "date": None,
            "absent_students": [],
            "topic": None,
            "homework": None
        },
        "expected_status": "blocked",
        "tags": ["short_unrelated", "blocked", "en"],
        "cache_fields": []
    },

    # =========================================================================
    # HINDI IN DEVANAGARI (20 messages: MSG21 to MSG40)
    # =========================================================================
    {
        "id": "MSG21",
        "language": "hi",
        "text": "8A: 2026-11-20 को 1 अनुपस्थित - स्नेहा रेड्डी। पाठ 3 दो चरों वाले रैखिक समीकरण पढ़ाया। गृहकार्य अभ्यास 3.2।",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-20",
            "absent_students": ["MUN0052"],
            "topic": "दो चरों वाले रैखिक समीकरण",
            "homework": "अभ्यास 3.2"
        },
        "expected_status": "ready",
        "tags": ["standard", "ready", "hi"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 अनुपस्थित", "roman": None},
            {"type": "absent_student", "value": "स्नेहा रेड्डी", "quote": "स्नेहा रेड्डी", "roman": "Sneha Reddy"},
            {"type": "topic", "value": "पाठ 3 दो चरों वाले रैखिक समीकरण", "quote": "पाठ 3 दो चरों वाले रैखिक समीकरण पढ़ाया", "roman": None},
            {"type": "homework", "value": "अभ्यास 3.2", "quote": "गृहकार्य अभ्यास 3.2", "roman": None}
        ]
    },
    {
        "id": "MSG22",
        "language": "hi",
        "text": "8A: 2026-11-19 को 1 अनुपस्थित - आदित्य दास। पाठ 4 द्विघात समीकरण पढ़ाया। गृहकार्य अभ्यास 4.1।",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-19",
            "absent_students": ["MUN0053"],
            "topic": "द्विघात समीकरण",
            "homework": "अभ्यास 4.1"
        },
        "expected_status": "ready",
        "tags": ["standard", "ready", "hi"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "date", "value": "2026-11-19", "quote": "2026-11-19", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 अनुपस्थित", "roman": None},
            {"type": "absent_student", "value": "आदित्य दास", "quote": "आदित्य दास", "roman": "Aditya Das"},
            {"type": "topic", "value": "पाठ 4 द्विघात समीकरण", "quote": "पाठ 4 द्विघात समीकरण पढ़ाया", "roman": None},
            {"type": "homework", "value": "अभ्यास 4.1", "quote": "गृहकार्य अभ्यास 4.1", "roman": None}
        ]
    },
    {
        "id": "MSG23",
        "language": "hi",
        "text": "8B: 2026-11-20 को 1 अनुपस्थित - ईशान शर्मा। पाठ 1 संख्या पद्धति पढ़ाया। गृहकार्य अभ्यास 1.1।",
        "teacher_id": "T01",
        "expected": {
            "class": "8B",
            "date": "2026-11-20",
            "absent_students": ["MUN0050"],
            "topic": "संख्या पद्धति",
            "homework": "अभ्यास 1.1"
        },
        "expected_status": "ready",
        "tags": ["standard", "ready", "hi"],
        "cache_fields": [
            {"type": "class", "value": "8B", "quote": "8B", "roman": None},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 अनुपस्थित", "roman": None},
            {"type": "absent_student", "value": "ईशान शर्मा", "quote": "ईशान शर्मा", "roman": "Ishaan Sharma"},
            {"type": "topic", "value": "पाठ 1 संख्या पद्धति", "quote": "पाठ 1 संख्या पद्धति पढ़ाया", "roman": None},
            {"type": "homework", "value": "अभ्यास 1.1", "quote": "गृहकार्य अभ्यास 1.1", "roman": None}
        ]
    },
    {
        "id": "MSG24",
        "language": "hi",
        "text": "8A: 2026-11-23 को 2 अनुपस्थित - कबीर बंसल और कबीर मेहता। पाठ 6 निर्देशांक ज्यामिति पढ़ाया। गृहकार्य अभ्यास 6.1।",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-23",
            "absent_students": ["MUN0041", "MUN0046"],
            "topic": "निर्देशांक ज्यामिति",
            "homework": "अभ्यास 6.1"
        },
        "expected_status": "ready",
        "tags": ["disambiguated", "ready", "hi"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "date", "value": "2026-11-23", "quote": "2026-11-23", "roman": None},
            {"type": "stated_count", "value": "2", "quote": "2 अनुपस्थित", "roman": None},
            {"type": "absent_student", "value": "कबीर बंसल", "quote": "कबीर बंसल", "roman": "Kabir Bansal"},
            {"type": "absent_student", "value": "कबीर मेहता", "quote": "कबीर मेहता", "roman": "Kabir Mehta"},
            {"type": "topic", "value": "पाठ 6 निर्देशांक ज्यामिति", "quote": "पाठ 6 निर्देशांक ज्यामिति पढ़ाया", "roman": None},
            {"type": "homework", "value": "अभ्यास 6.1", "quote": "गृहकार्य अभ्यास 6.1", "roman": None}
        ]
    },
    {
        "id": "MSG25",
        "language": "hi",
        "text": "8A: 2026-11-20 को 1 अनुपस्थित - कबीर। पाठ 3 दो चरों वाले रैखिक समीकरण पढ़ाया। गृहकार्य अभ्यास 3.1।",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-20",
            "absent_students": ["MUN0041", "MUN0046", "MUN0051"],
            "topic": "दो चरों वाले रैखिक समीकरण",
            "homework": "अभ्यास 3.1"
        },
        "expected_status": "needs_review",
        "tags": ["name_collision", "needs_review", "hi"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 अनुपस्थित", "roman": None},
            {"type": "absent_student", "value": "कबीर", "quote": "कबीर", "roman": "Kabir"},
            {"type": "topic", "value": "पाठ 3 दो चरों वाले रैखिक समीकरण", "quote": "पाठ 3 दो चरों वाले रैखिक समीकरण पढ़ाया", "roman": None},
            {"type": "homework", "value": "अभ्यास 3.1", "quote": "गृहकार्य अभ्यास 3.1", "roman": None}
        ]
    },
    {
        "id": "MSG26",
        "language": "hi",
        "text": "8A: 2026-11-19 को 1 अनुपस्थित - अयान। पाठ 2 बहुपद पढ़ाया। गृहकार्य अभ्यास 2.2।",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-19",
            "absent_students": ["MUN0042", "MUN0048", "MUN0060"],
            "topic": "बहुपद",
            "homework": "अभ्यास 2.2"
        },
        "expected_status": "needs_review",
        "tags": ["name_collision", "needs_review", "hi"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "date", "value": "2026-11-19", "quote": "2026-11-19", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 अनुपस्थित", "roman": None},
            {"type": "absent_student", "value": "अयान", "quote": "अयान", "roman": "Ayaan"},
            {"type": "topic", "value": "पाठ 2 बहुपद", "quote": "पाठ 2 बहुपद पढ़ाया", "roman": None},
            {"type": "homework", "value": "अभ्यास 2.2", "quote": "गृहकार्य अभ्यास 2.2", "roman": None}
        ]
    },
    {
        "id": "MSG27",
        "language": "hi",
        "text": "9A: 2026-11-20 को 1 अनुपस्थित - अर्जुन। पाठ 5 समांतर श्रेढ़ी पढ़ाया। गृहकार्य अभ्यास 5.1।",
        "teacher_id": "T01",
        "expected": {
            "class": "9A",
            "date": "2026-11-20",
            "absent_students": ["MUN0063", "MUN0077"],
            "topic": "समांतर श्रेढ़ी",
            "homework": "अभ्यास 5.1"
        },
        "expected_status": "needs_review",
        "tags": ["name_collision", "needs_review", "hi"],
        "cache_fields": [
            {"type": "class", "value": "9A", "quote": "9A", "roman": None},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 अनुपस्थित", "roman": None},
            {"type": "absent_student", "value": "अर्जुन", "quote": "अर्जुन", "roman": "Arjun"},
            {"type": "topic", "value": "पाठ 5 समांतर श्रेढ़ी", "quote": "पाठ 5 समांतर श्रेढ़ी पढ़ाया", "roman": None},
            {"type": "homework", "value": "अभ्यास 5.1", "quote": "गृहकार्य अभ्यास 5.1", "roman": None}
        ]
    },
    {
        "id": "MSG28",
        "language": "hi",
        "text": "9A: 2026-11-23 को 1 अनुपस्थित - देव। पाठ 7 त्रिभुज पढ़ाया। गृहकार्य प्रमेय 7.1 सिद्ध करो।",
        "teacher_id": "T01",
        "expected": {
            "class": "9A",
            "date": "2026-11-23",
            "absent_students": ["MUN0069", "MUN0070"],
            "topic": "त्रिभुज",
            "homework": "प्रमेय 7.1"
        },
        "expected_status": "needs_review",
        "tags": ["name_collision", "needs_review", "hi"],
        "cache_fields": [
            {"type": "class", "value": "9A", "quote": "9A", "roman": None},
            {"type": "date", "value": "2026-11-23", "quote": "2026-11-23", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 अनुपस्थित", "roman": None},
            {"type": "absent_student", "value": "देव", "quote": "देव", "roman": "Dev"},
            {"type": "topic", "value": "पाठ 7 त्रिभुज", "quote": "पाठ 7 त्रिभुज पढ़ाया", "roman": None},
            {"type": "homework", "value": "प्रमेय 7.1", "quote": "गृहकार्य प्रमेय 7.1", "roman": None}
        ]
    },
    {
        "id": "MSG29",
        "language": "hi",
        "text": "8B: 2026-11-20 को 1 अनुपस्थित - रिया। पाठ 2 बहुपद पढ़ाया। गृहकार्य अभ्यास 2.1।",
        "teacher_id": "T01",
        "expected": {
            "class": "8B",
            "date": "2026-11-20",
            "absent_students": ["MUN0044", "MUN0055"],
            "topic": "बहुपद",
            "homework": "अभ्यास 2.1"
        },
        "expected_status": "needs_review",
        "tags": ["name_collision", "needs_review", "hi"],
        "cache_fields": [
            {"type": "class", "value": "8B", "quote": "8B", "roman": None},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 अनुपस्थित", "roman": None},
            {"type": "absent_student", "value": "रिया", "quote": "रिया", "roman": "Riya"},
            {"type": "topic", "value": "पाठ 2 बहुपद", "quote": "पाठ 2 बहुपद पढ़ाया", "roman": None},
            {"type": "homework", "value": "अभ्यास 2.1", "quote": "गृहकार्य अभ्यास 2.1", "roman": None}
        ]
    },
    {
        "id": "MSG30",
        "language": "hi",
        "text": "8A: 2026-11-20 को 3 अनुपस्थित - स्नेहा रेड्डी और आदित्य दास। पाठ 3 दो चरों वाले रैखिक समीकरण पढ़ाया। गृहकार्य अभ्यास 3.3।",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-20",
            "absent_students": ["MUN0052", "MUN0053"],
            "topic": "दो चरों वाले रैखिक समीकरण",
            "homework": "अभ्यास 3.3"
        },
        "expected_status": "needs_review",
        "tags": ["count_mismatch", "needs_review", "hi"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "stated_count", "value": "3", "quote": "3 अनुपस्थित", "roman": None},
            {"type": "absent_student", "value": "स्नेहा रेड्डी", "quote": "स्नेहा रेड्डी", "roman": "Sneha Reddy"},
            {"type": "absent_student", "value": "आदित्य दास", "quote": "आदित्य दास", "roman": "Aditya Das"},
            {"type": "topic", "value": "पाठ 3 दो चरों वाले रैखिक समीकरण", "quote": "पाठ 3 दो चरों वाले रैखिक समीकरण पढ़ाया", "roman": None},
            {"type": "homework", "value": "अभ्यास 3.3", "quote": "गृहकार्य अभ्यास 3.3", "roman": None}
        ]
    },
    {
        "id": "MSG31",
        "language": "hi",
        "text": "8A: 2026-11-19 को 1 अनुपस्थित - काव्या जोशी और निशा सैनी। पाठ 4 द्विघात समीकरण पढ़ाया। गृहकार्य अभ्यास 4.2।",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-19",
            "absent_students": ["MUN0049", "MUN0054"],
            "topic": "द्विघात समीकरण",
            "homework": "अभ्यास 4.2"
        },
        "expected_status": "needs_review",
        "tags": ["count_mismatch", "needs_review", "hi"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "date", "value": "2026-11-19", "quote": "2026-11-19", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 अनुपस्थित", "roman": None},
            {"type": "absent_student", "value": "काव्या जोशी", "quote": "काव्या जोशी", "roman": "Kavya Joshi"},
            {"type": "absent_student", "value": "निशा सैनी", "quote": "निशा सैनी", "roman": "Nisha Saini"},
            {"type": "topic", "value": "पाठ 4 द्विघात समीकरण", "quote": "पाठ 4 द्विघात समीकरण पढ़ाया", "roman": None},
            {"type": "homework", "value": "अभ्यास 4.2", "quote": "गृहकार्य अभ्यास 4.2", "roman": None}
        ]
    },
    {
        "id": "MSG32",
        "language": "hi",
        "text": "8B: 2026-11-20 को 2 अनुपस्थित - ईशान शर्मा। पाठ 1 संख्या पद्धति पढ़ाया। गृहकार्य अभ्यास 1.3।",
        "teacher_id": "T01",
        "expected": {
            "class": "8B",
            "date": "2026-11-20",
            "absent_students": ["MUN0050"],
            "topic": "संख्या पद्धति",
            "homework": "अभ्यास 1.3"
        },
        "expected_status": "needs_review",
        "tags": ["count_mismatch", "needs_review", "hi"],
        "cache_fields": [
            {"type": "class", "value": "8B", "quote": "8B", "roman": None},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "stated_count", "value": "2", "quote": "2 अनुपस्थित", "roman": None},
            {"type": "absent_student", "value": "ईशान शर्मा", "quote": "ईशान शर्मा", "roman": "Ishaan Sharma"},
            {"type": "topic", "value": "पाठ 1 संख्या पद्धति", "quote": "पाठ 1 संख्या पद्धति पढ़ाया", "roman": None},
            {"type": "homework", "value": "अभ्यास 1.3", "quote": "गृहकार्य अभ्यास 1.3", "roman": None}
        ]
    },
    {
        "id": "MSG33",
        "language": "hi",
        "text": "8A: 2026-11-15 को 1 अनुपस्थित - स्नेहा रेड्डी। पाठ 3 दो चरों वाले रैखिक समीकरण पढ़ाया। गृहकार्य अभ्यास 3.2।",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-15",
            "absent_students": ["MUN0052"],
            "topic": "दो चरों वाले रैखिक समीकरण",
            "homework": "अभ्यास 3.2"
        },
        "expected_status": "blocked",
        "tags": ["sunday_date", "blocked", "hi"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "date", "value": "2026-11-15", "quote": "2026-11-15", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 अनुपस्थित", "roman": None},
            {"type": "absent_student", "value": "स्नेहा रेड्डी", "quote": "स्नेहा रेड्डी", "roman": "Sneha Reddy"},
            {"type": "topic", "value": "पाठ 3 दो चरों वाले रैखिक समीकरण", "quote": "पाठ 3 दो चरों वाले रैखिक समीकरण पढ़ाया", "roman": None},
            {"type": "homework", "value": "अभ्यास 3.2", "quote": "गृहकार्य अभ्यास 3.2", "roman": None}
        ]
    },
    {
        "id": "MSG34",
        "language": "hi",
        "text": "8A: 2026-12-10 को 1 अनुपस्थित - आदित्य दास। पाठ 4 द्विघात समीकरण पढ़ाया। गृहकार्य अभ्यास 4.1।",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-12-10",
            "absent_students": ["MUN0053"],
            "topic": "द्विघात समीकरण",
            "homework": "अभ्यास 4.1"
        },
        "expected_status": "blocked",
        "tags": ["future_date", "blocked", "hi"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "date", "value": "2026-12-10", "quote": "2026-12-10", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 अनुपस्थित", "roman": None},
            {"type": "absent_student", "value": "आदित्य दास", "quote": "आदित्य दास", "roman": "Aditya Das"},
            {"type": "topic", "value": "पाठ 4 द्विघात समीकरण", "quote": "पाठ 4 द्विघात समीकरण पढ़ाया", "roman": None},
            {"type": "homework", "value": "अभ्यास 4.1", "quote": "गृहकार्य अभ्यास 4.1", "roman": None}
        ]
    },
    {
        "id": "MSG35",
        "language": "hi",
        "text": "6A: 2026-11-20 को 1 अनुपस्थित - मानव सिंह। पाठ 1 संख्या पद्धति पढ़ाया। गृहकार्य अभ्यास 1.1।",
        "teacher_id": "T01",
        "expected": {
            "class": "6A",
            "date": "2026-11-20",
            "absent_students": ["MUN0001"],
            "topic": "संख्या पद्धति",
            "homework": "अभ्यास 1.1"
        },
        "expected_status": "blocked",
        "tags": ["unassigned_class", "blocked", "hi"],
        "cache_fields": [
            {"type": "class", "value": "6A", "quote": "6A", "roman": None},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 अनुपस्थित", "roman": None},
            {"type": "absent_student", "value": "मानव सिंह", "quote": "मानव सिंह", "roman": "Manav Singh"},
            {"type": "topic", "value": "पाठ 1 संख्या पद्धति", "quote": "पाठ 1 संख्या पद्धति पढ़ाया", "roman": None},
            {"type": "homework", "value": "अभ्यास 1.1", "quote": "गृहकार्य अभ्यास 1.1", "roman": None}
        ]
    },
    {
        "id": "MSG36",
        "language": "hi",
        "text": "11A: 2026-11-20 को 1 अनुपस्थित - रिया। पाठ 1 भौतिक जगत पढ़ाया। गृहकार्य नोट्स बनाओ।",
        "teacher_id": "T01",
        "expected": {
            "class": "11A",
            "date": "2026-11-20",
            "absent_students": [],
            "topic": "भौतिक जगत",
            "homework": "नोट्स बनाओ"
        },
        "expected_status": "blocked",
        "tags": ["unassigned_class", "blocked", "hi"],
        "cache_fields": [
            {"type": "class", "value": "11A", "quote": "11A", "roman": None},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 अनुपस्थित", "roman": None},
            {"type": "absent_student", "value": "रिया", "quote": "रिया", "roman": "Riya"},
            {"type": "topic", "value": "पाठ 1 भौतिक जगत", "quote": "पाठ 1 भौतिक जगत पढ़ाया", "roman": None},
            {"type": "homework", "value": "नोट्स बनाओ", "quote": "गृहकार्य नोट्स बनाओ", "roman": None}
        ]
    },
    {
        "id": "MSG37",
        "language": "hi",
        "text": "8A: 2026-11-20 को 1 अनुपस्थित - काव्या जोशी। पाठ 7 त्रिभुज और सर्वांगसमता पढ़ाया। आज कोई गृहकार्य नहीं दिया।",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-20",
            "absent_students": ["MUN0049"],
            "topic": "त्रिभुज और सर्वांगसमता",
            "homework": None
        },
        "expected_status": "ready",
        "tags": ["no_homework", "ready", "hi"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 अनुपस्थित", "roman": None},
            {"type": "absent_student", "value": "काव्या जोशी", "quote": "काव्या जोशी", "roman": "Kavya Joshi"},
            {"type": "topic", "value": "पाठ 7 त्रिभुज और सर्वांगसमता", "quote": "पाठ 7 त्रिभुज और सर्वांगसमता पढ़ाया", "roman": None}
        ]
    },
    {
        "id": "MSG38",
        "language": "hi",
        "text": "8A: 2026-11-20 को 1 अनुपस्थित - निशा सैनी। पाठ 8 त्रिकोणमिति का परिचय पढ़ाया। गृहकार्य अभ्यास 8.1।",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-20",
            "absent_students": ["MUN0054"],
            "topic": "त्रिकोणमिति का परिचय",
            "homework": "अभ्यास 8.1"
        },
        "expected_status": "ready",
        "tags": ["standard", "ready", "hi"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 अनुपस्थित", "roman": None},
            {"type": "absent_student", "value": "निशा सैनी", "quote": "निशा सैनी", "roman": "Nisha Saini"},
            {"type": "topic", "value": "पाठ 8 त्रिकोणमिति का परिचय", "quote": "पाठ 8 त्रिकोणमिति का परिचय पढ़ाया", "roman": None},
            {"type": "homework", "value": "अभ्यास 8.1", "quote": "गृहकार्य अभ्यास 8.1", "roman": None}
        ]
    },
    {
        "id": "MSG39",
        "language": "hi",
        "text": "सुप्रभात सभी को, आज का दिन आप सभी के लिए मंगलमय हो।",
        "teacher_id": "T01",
        "expected": {
            "class": None,
            "date": None,
            "absent_students": [],
            "topic": None,
            "homework": None
        },
        "expected_status": "blocked",
        "tags": ["short_unrelated", "blocked", "hi"],
        "cache_fields": []
    },
    {
        "id": "MSG40",
        "language": "hi",
        "text": "धन्यवाद सर, कल सुबह की प्रार्थना सभा में मिलते हैं।",
        "teacher_id": "T01",
        "expected": {
            "class": None,
            "date": None,
            "absent_students": [],
            "topic": None,
            "homework": None
        },
        "expected_status": "blocked",
        "tags": ["short_unrelated", "blocked", "hi"],
        "cache_fields": []
    },

    # =========================================================================
    # HINGLISH (20 messages: MSG41 to MSG60)
    # =========================================================================
    {
        "id": "MSG41",
        "language": "hinglish",
        "text": "8A me 2026-11-20 ko 1 absent tha - Sneha Reddy. Chapter 3 Linear Equations in Two Variables padhaya. Homework Ex 3.2 solve karna.",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-20",
            "absent_students": ["MUN0052"],
            "topic": "Linear Equations in Two Variables",
            "homework": "Exercise 3.2"
        },
        "expected_status": "ready",
        "tags": ["standard", "ready", "hinglish"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Sneha Reddy", "quote": "Sneha Reddy", "roman": "Sneha Reddy"},
            {"type": "topic", "value": "Chapter 3 Linear Equations in Two Variables", "quote": "Chapter 3 Linear Equations in Two Variables padhaya", "roman": None},
            {"type": "homework", "value": "Exercise 3.2", "quote": "Homework Ex 3.2", "roman": None}
        ]
    },
    {
        "id": "MSG42",
        "language": "hinglish",
        "text": "8A me 2026-11-19 ko 1 absent tha - Aditya Das. Chapter 4 Quadratic Equations cover kiya. Homework Ex 4.1 question 1 to 5.",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-19",
            "absent_students": ["MUN0053"],
            "topic": "Quadratic Equations",
            "homework": "Exercise 4.1 question 1 to 5"
        },
        "expected_status": "ready",
        "tags": ["standard", "ready", "hinglish"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "date", "value": "2026-11-19", "quote": "2026-11-19", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Aditya Das", "quote": "Aditya Das", "roman": "Aditya Das"},
            {"type": "topic", "value": "Chapter 4 Quadratic Equations", "quote": "Chapter 4 Quadratic Equations cover kiya", "roman": None},
            {"type": "homework", "value": "Exercise 4.1 question 1 to 5", "quote": "Homework Ex 4.1 question 1 to 5", "roman": None}
        ]
    },
    {
        "id": "MSG43",
        "language": "hinglish",
        "text": "8B me 2026-11-20 ko 1 absent tha - Ishaan Sharma. Chapter 1 Number Systems & Real Numbers padhaya. Homework Exercise 1.2 questions.",
        "teacher_id": "T01",
        "expected": {
            "class": "8B",
            "date": "2026-11-20",
            "absent_students": ["MUN0050"],
            "topic": "Number Systems & Real Numbers",
            "homework": "Exercise 1.2"
        },
        "expected_status": "ready",
        "tags": ["standard", "ready", "hinglish"],
        "cache_fields": [
            {"type": "class", "value": "8B", "quote": "8B", "roman": None},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Ishaan Sharma", "quote": "Ishaan Sharma", "roman": "Ishaan Sharma"},
            {"type": "topic", "value": "Chapter 1 Number Systems & Real Numbers", "quote": "Chapter 1 Number Systems & Real Numbers padhaya", "roman": None},
            {"type": "homework", "value": "Exercise 1.2", "quote": "Homework Exercise 1.2", "roman": None}
        ]
    },
    {
        "id": "MSG44",
        "language": "hinglish",
        "text": "8A me 2026-11-23 ko 2 absent the - Kabir Bansal, Kabir Mehta. Chapter 6 Coordinate Geometry padhaya. Homework Ex 6.1 complete karna.",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-23",
            "absent_students": ["MUN0041", "MUN0046"],
            "topic": "Coordinate Geometry",
            "homework": "Exercise 6.1"
        },
        "expected_status": "ready",
        "tags": ["disambiguated", "ready", "hinglish"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "date", "value": "2026-11-23", "quote": "2026-11-23", "roman": None},
            {"type": "stated_count", "value": "2", "quote": "2 absent", "roman": None},
            {"type": "absent_student", "value": "Kabir Bansal", "quote": "Kabir Bansal", "roman": "Kabir Bansal"},
            {"type": "absent_student", "value": "Kabir Mehta", "quote": "Kabir Mehta", "roman": "Kabir Mehta"},
            {"type": "topic", "value": "Chapter 6 Coordinate Geometry", "quote": "Chapter 6 Coordinate Geometry padhaya", "roman": None},
            {"type": "homework", "value": "Exercise 6.1", "quote": "Homework Ex 6.1", "roman": None}
        ]
    },
    {
        "id": "MSG45",
        "language": "hinglish",
        "text": "8A me 2026-11-20 ko 1 absent tha - Kabir. Chapter 3 Linear Equations in Two Variables padhaya. Homework Ex 3.1.",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-20",
            "absent_students": ["MUN0041", "MUN0046", "MUN0051"],
            "topic": "Linear Equations in Two Variables",
            "homework": "Exercise 3.1"
        },
        "expected_status": "needs_review",
        "tags": ["name_collision", "needs_review", "hinglish"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Kabir", "quote": "Kabir", "roman": "Kabir"},
            {"type": "topic", "value": "Chapter 3 Linear Equations in Two Variables", "quote": "Chapter 3 Linear Equations in Two Variables padhaya", "roman": None},
            {"type": "homework", "value": "Exercise 3.1", "quote": "Homework Ex 3.1", "roman": None}
        ]
    },
    {
        "id": "MSG46",
        "language": "hinglish",
        "text": "8A me 2026-11-19 ko 1 absent tha - Ayaan. Chapter 2 Polynomials & Algebraic Expressions padhaya. Homework Ex 2.3 questions.",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-19",
            "absent_students": ["MUN0042", "MUN0048", "MUN0060"],
            "topic": "Polynomials & Algebraic Expressions",
            "homework": "Exercise 2.3"
        },
        "expected_status": "needs_review",
        "tags": ["name_collision", "needs_review", "hinglish"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "date", "value": "2026-11-19", "quote": "2026-11-19", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Ayaan", "quote": "Ayaan", "roman": "Ayaan"},
            {"type": "topic", "value": "Chapter 2 Polynomials & Algebraic Expressions", "quote": "Chapter 2 Polynomials & Algebraic Expressions padhaya", "roman": None},
            {"type": "homework", "value": "Exercise 2.3", "quote": "Homework Ex 2.3", "roman": None}
        ]
    },
    {
        "id": "MSG47",
        "language": "hinglish",
        "text": "9A me 2026-11-20 ko 1 absent tha - Arjun. Chapter 5 Arithmetic Progressions padhaya. Homework Exercise 5.2.",
        "teacher_id": "T01",
        "expected": {
            "class": "9A",
            "date": "2026-11-20",
            "absent_students": ["MUN0063", "MUN0077"],
            "topic": "Arithmetic Progressions",
            "homework": "Exercise 5.2"
        },
        "expected_status": "needs_review",
        "tags": ["name_collision", "needs_review", "hinglish"],
        "cache_fields": [
            {"type": "class", "value": "9A", "quote": "9A", "roman": None},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Arjun", "quote": "Arjun", "roman": "Arjun"},
            {"type": "topic", "value": "Chapter 5 Arithmetic Progressions", "quote": "Chapter 5 Arithmetic Progressions padhaya", "roman": None},
            {"type": "homework", "value": "Exercise 5.2", "quote": "Homework Exercise 5.2", "roman": None}
        ]
    },
    {
        "id": "MSG48",
        "language": "hinglish",
        "text": "9A me 2026-11-23 ko 1 absent tha - Vivaan. Chapter 7 Triangles & Congruence padhaya. Homework Theorem 7.1 proof.",
        "teacher_id": "T01",
        "expected": {
            "class": "9A",
            "date": "2026-11-23",
            "absent_students": ["MUN0068", "MUN0071", "MUN0073"],
            "topic": "Triangles & Congruence",
            "homework": "Theorem 7.1 proof"
        },
        "expected_status": "needs_review",
        "tags": ["name_collision", "needs_review", "hinglish"],
        "cache_fields": [
            {"type": "class", "value": "9A", "quote": "9A", "roman": None},
            {"type": "date", "value": "2026-11-23", "quote": "2026-11-23", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Vivaan", "quote": "Vivaan", "roman": "Vivaan"},
            {"type": "topic", "value": "Chapter 7 Triangles & Congruence", "quote": "Chapter 7 Triangles & Congruence padhaya", "roman": None},
            {"type": "homework", "value": "Theorem 7.1 proof", "quote": "Homework Theorem 7.1 proof", "roman": None}
        ]
    },
    {
        "id": "MSG49",
        "language": "hinglish",
        "text": "8B me 2026-11-20 ko 1 absent thi - Riya. Chapter 2 Polynomials & Algebraic Expressions padhaya. Homework Ex 2.1 questions.",
        "teacher_id": "T01",
        "expected": {
            "class": "8B",
            "date": "2026-11-20",
            "absent_students": ["MUN0044", "MUN0055"],
            "topic": "Polynomials & Algebraic Expressions",
            "homework": "Exercise 2.1"
        },
        "expected_status": "needs_review",
        "tags": ["name_collision", "needs_review", "hinglish"],
        "cache_fields": [
            {"type": "class", "value": "8B", "quote": "8B", "roman": None},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Riya", "quote": "Riya", "roman": "Riya"},
            {"type": "topic", "value": "Chapter 2 Polynomials & Algebraic Expressions", "quote": "Chapter 2 Polynomials & Algebraic Expressions padhaya", "roman": None},
            {"type": "homework", "value": "Exercise 2.1", "quote": "Homework Ex 2.1", "roman": None}
        ]
    },
    {
        "id": "MSG50",
        "language": "hinglish",
        "text": "8A me 2026-11-20 ko 3 absent the - Sneha Reddy aur Aditya Das. Chapter 3 Linear Equations in Two Variables padhaya. Homework Ex 3.3.",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-20",
            "absent_students": ["MUN0052", "MUN0053"],
            "topic": "Linear Equations in Two Variables",
            "homework": "Exercise 3.3"
        },
        "expected_status": "needs_review",
        "tags": ["count_mismatch", "needs_review", "hinglish"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "stated_count", "value": "3", "quote": "3 absent", "roman": None},
            {"type": "absent_student", "value": "Sneha Reddy", "quote": "Sneha Reddy", "roman": "Sneha Reddy"},
            {"type": "absent_student", "value": "Aditya Das", "quote": "Aditya Das", "roman": "Aditya Das"},
            {"type": "topic", "value": "Chapter 3 Linear Equations in Two Variables", "quote": "Chapter 3 Linear Equations in Two Variables padhaya", "roman": None},
            {"type": "homework", "value": "Exercise 3.3", "quote": "Homework Ex 3.3", "roman": None}
        ]
    },
    {
        "id": "MSG51",
        "language": "hinglish",
        "text": "8A me 2026-11-19 ko 1 absent tha - Kavya Joshi aur Nisha Saini. Chapter 4 Quadratic Equations cover kiya. Homework Ex 4.2.",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-19",
            "absent_students": ["MUN0049", "MUN0054"],
            "topic": "Quadratic Equations",
            "homework": "Exercise 4.2"
        },
        "expected_status": "needs_review",
        "tags": ["count_mismatch", "needs_review", "hinglish"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "date", "value": "2026-11-19", "quote": "2026-11-19", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Kavya Joshi", "quote": "Kavya Joshi", "roman": "Kavya Joshi"},
            {"type": "absent_student", "value": "Nisha Saini", "quote": "Nisha Saini", "roman": "Nisha Saini"},
            {"type": "topic", "value": "Chapter 4 Quadratic Equations", "quote": "Chapter 4 Quadratic Equations cover kiya", "roman": None},
            {"type": "homework", "value": "Exercise 4.2", "quote": "Homework Ex 4.2", "roman": None}
        ]
    },
    {
        "id": "MSG52",
        "language": "hinglish",
        "text": "8B me 2026-11-20 ko 2 absent the - Ishaan Sharma. Chapter 1 Number Systems & Real Numbers padhaya. Homework Ex 1.3 questions.",
        "teacher_id": "T01",
        "expected": {
            "class": "8B",
            "date": "2026-11-20",
            "absent_students": ["MUN0050"],
            "topic": "Number Systems & Real Numbers",
            "homework": "Exercise 1.3"
        },
        "expected_status": "needs_review",
        "tags": ["count_mismatch", "needs_review", "hinglish"],
        "cache_fields": [
            {"type": "class", "value": "8B", "quote": "8B", "roman": None},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "stated_count", "value": "2", "quote": "2 absent", "roman": None},
            {"type": "absent_student", "value": "Ishaan Sharma", "quote": "Ishaan Sharma", "roman": "Ishaan Sharma"},
            {"type": "topic", "value": "Chapter 1 Number Systems & Real Numbers", "quote": "Chapter 1 Number Systems & Real Numbers padhaya", "roman": None},
            {"type": "homework", "value": "Exercise 1.3", "quote": "Homework Ex 1.3", "roman": None}
        ]
    },
    {
        "id": "MSG53",
        "language": "hinglish",
        "text": "8A me 2026-11-29 ko 1 absent thi - Sneha Reddy. Chapter 3 Linear Equations in Two Variables padhaya. Homework Ex 3.2.",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-29",
            "absent_students": ["MUN0052"],
            "topic": "Linear Equations in Two Variables",
            "homework": "Exercise 3.2"
        },
        "expected_status": "blocked",
        "tags": ["sunday_date", "blocked", "hinglish"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "date", "value": "2026-11-29", "quote": "2026-11-29", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Sneha Reddy", "quote": "Sneha Reddy", "roman": "Sneha Reddy"},
            {"type": "topic", "value": "Chapter 3 Linear Equations in Two Variables", "quote": "Chapter 3 Linear Equations in Two Variables padhaya", "roman": None},
            {"type": "homework", "value": "Exercise 3.2", "quote": "Homework Ex 3.2", "roman": None}
        ]
    },
    {
        "id": "MSG54",
        "language": "hinglish",
        "text": "8A me 2026-12-05 ko 1 absent tha - Aditya Das. Chapter 4 Quadratic Equations cover kiya. Homework Ex 4.1.",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-12-05",
            "absent_students": ["MUN0053"],
            "topic": "Quadratic Equations",
            "homework": "Exercise 4.1"
        },
        "expected_status": "blocked",
        "tags": ["future_date", "blocked", "hinglish"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "date", "value": "2026-12-05", "quote": "2026-12-05", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Aditya Das", "quote": "Aditya Das", "roman": "Aditya Das"},
            {"type": "topic", "value": "Chapter 4 Quadratic Equations", "quote": "Chapter 4 Quadratic Equations cover kiya", "roman": None},
            {"type": "homework", "value": "Exercise 4.1", "quote": "Homework Ex 4.1", "roman": None}
        ]
    },
    {
        "id": "MSG55",
        "language": "hinglish",
        "text": "7B me 2026-11-20 ko 1 absent tha - Arjun. Chapter 3 Linear Equations in Two Variables padhaya. Homework Ex 3.1.",
        "teacher_id": "T01",
        "expected": {
            "class": "7B",
            "date": "2026-11-20",
            "absent_students": [],
            "topic": "Linear Equations in Two Variables",
            "homework": "Exercise 3.1"
        },
        "expected_status": "blocked",
        "tags": ["unassigned_class", "blocked", "hinglish"],
        "cache_fields": [
            {"type": "class", "value": "7B", "quote": "7B", "roman": None},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Arjun", "quote": "Arjun", "roman": "Arjun"},
            {"type": "topic", "value": "Chapter 3 Linear Equations in Two Variables", "quote": "Chapter 3 Linear Equations in Two Variables padhaya", "roman": None},
            {"type": "homework", "value": "Exercise 3.1", "quote": "Homework Ex 3.1", "roman": None}
        ]
    },
    {
        "id": "MSG56",
        "language": "hinglish",
        "text": "12B me 2026-11-20 ko 1 absent tha - Rohan. Chapter 1 Number Systems padhaya. Homework questions solve karna.",
        "teacher_id": "T01",
        "expected": {
            "class": "12B",
            "date": "2026-11-20",
            "absent_students": [],
            "topic": "Number Systems",
            "homework": "questions solve karna"
        },
        "expected_status": "blocked",
        "tags": ["unassigned_class", "blocked", "hinglish"],
        "cache_fields": [
            {"type": "class", "value": "12B", "quote": "12B", "roman": None},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Rohan", "quote": "Rohan", "roman": "Rohan"},
            {"type": "topic", "value": "Chapter 1 Number Systems", "quote": "Chapter 1 Number Systems padhaya", "roman": None},
            {"type": "homework", "value": "questions solve karna", "quote": "Homework questions solve karna", "roman": None}
        ]
    },
    {
        "id": "MSG57",
        "language": "hinglish",
        "text": "8A me 2026-11-20 ko 1 absent thi - Kavya Joshi. Chapter 7 Triangles & Congruence revision kiya. Aaj koi homework nahi diya.",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-20",
            "absent_students": ["MUN0049"],
            "topic": "Triangles & Congruence",
            "homework": None
        },
        "expected_status": "ready",
        "tags": ["no_homework", "ready", "hinglish"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Kavya Joshi", "quote": "Kavya Joshi", "roman": "Kavya Joshi"},
            {"type": "topic", "value": "Chapter 7 Triangles & Congruence", "quote": "Chapter 7 Triangles & Congruence revision kiya", "roman": None}
        ]
    },
    {
        "id": "MSG58",
        "language": "hinglish",
        "text": "8A me 2026-11-20 ko 1 absent thi - Nisha Saini. Chapter 8 Introduction to Trigonometry padhaya. Homework Ex 8.1.",
        "teacher_id": "T01",
        "expected": {
            "class": "8A",
            "date": "2026-11-20",
            "absent_students": ["MUN0054"],
            "topic": "Introduction to Trigonometry",
            "homework": "Exercise 8.1"
        },
        "expected_status": "ready",
        "tags": ["standard", "ready", "hinglish"],
        "cache_fields": [
            {"type": "class", "value": "8A", "quote": "8A", "roman": None},
            {"type": "date", "value": "2026-11-20", "quote": "2026-11-20", "roman": None},
            {"type": "stated_count", "value": "1", "quote": "1 absent", "roman": None},
            {"type": "absent_student", "value": "Nisha Saini", "quote": "Nisha Saini", "roman": "Nisha Saini"},
            {"type": "topic", "value": "Chapter 8 Introduction to Trigonometry", "quote": "Chapter 8 Introduction to Trigonometry padhaya", "roman": None},
            {"type": "homework", "value": "Exercise 8.1", "quote": "Homework Ex 8.1", "roman": None}
        ]
    },
    {
        "id": "MSG59",
        "language": "hinglish",
        "text": "Ok sir noted, kal morning assembly me milte hain.",
        "teacher_id": "T01",
        "expected": {
            "class": None,
            "date": None,
            "absent_students": [],
            "topic": None,
            "homework": None
        },
        "expected_status": "blocked",
        "tags": ["short_unrelated", "blocked", "hinglish"],
        "cache_fields": []
    },
    {
        "id": "MSG60",
        "language": "hinglish",
        "text": "Attendance record desk pe rakh diya hai, kindly verify.",
        "teacher_id": "T01",
        "expected": {
            "class": None,
            "date": None,
            "absent_students": [],
            "topic": None,
            "homework": None
        },
        "expected_status": "blocked",
        "tags": ["short_unrelated", "blocked", "hinglish"],
        "cache_fields": []
    }
]


def generate_all():
    base_dir = Path(__file__).resolve().parent.parent
    eval_dir = base_dir / "eval"
    eval_dir.mkdir(exist_ok=True)

    jsonl_path = eval_dir / "messages.jsonl"
    cache_path = eval_dir / "cache.json"

    # 1. Write messages.jsonl
    with open(jsonl_path, "w", encoding="utf-8") as f:
        # File header stating synthetic dataset
        f.write("# Synthetic evaluation dataset written by the Munshi engineering team for benchmark testing.\n")
        for m in MESSAGES:
            line_data = {
                "id": m["id"],
                "language": m["language"],
                "text": m["text"],
                "teacher_id": m.get("teacher_id", "T01"),
                "expected": m["expected"],
                "expected_status": m["expected_status"],
                "tags": m["tags"]
            }
            f.write(json.dumps(line_data, ensure_ascii=False) + "\n")

    print(f"Generated {len(MESSAGES)} messages in {jsonl_path}")

    # 2. Write cache.json
    cache_data = {}
    for m in MESSAGES:
        cache_data[m["text"]] = {
            "language": m["language"],
            "llm_mode": "gemini",
            "fields": m["cache_fields"]
        }

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(cache_data)} cache entries in {cache_path}")


if __name__ == "__main__":
    generate_all()
