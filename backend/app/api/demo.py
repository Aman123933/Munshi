from typing import Dict, List
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["demo"])


class DemoMessageItem(BaseModel):
    id: str
    title: str
    scenario: str
    class_label: str
    text: str


@router.get("/demo/messages", response_model=List[DemoMessageItem])
def get_demo_messages():
    """
    GET /api/demo/messages -> 6 ready-made demo messages:
    1. Clean English
    2. Hindi Devanagari
    3. Hinglish
    4. Three-Kabirs Collision
    5. Count Mismatch
    6. Sunday Date (Holiday)
    Uses real names and classes from the seeded roster.
    """
    messages = [
        DemoMessageItem(
            id="demo-1",
            title="Clean English Attendance",
            scenario="Standard clear attendance with two unique students in 8A",
            class_label="8A",
            text="8A: 2 absent - Sneha Reddy, Aditya Das. Covered Chapter 3 Linear Equations. Homework Ex 3.2.",
        ),
        DemoMessageItem(
            id="demo-2",
            title="Hindi Devanagari Script",
            scenario="Devanagari message demonstrating transliteration and Hindi NLP",
            class_label="8A",
            text="8A में आज 2 अनुपस्थित - स्नेहा, आदित्य। पाठ 3 पढ़ाया। गृहकार्य अभ्यास 3.2।",
        ),
        DemoMessageItem(
            id="demo-3",
            title="Hinglish Classroom Update",
            scenario="Colloquial Hinglish phrase structure with lesson diary",
            class_label="8A",
            text="8A: 2 absent the - Sneha, Aditya. Aaj chapter 3 Linear Equations padhaya. Homework Ex 3.2.",
        ),
        DemoMessageItem(
            id="demo-4",
            title="Three-Kabirs Name Collision",
            scenario="Ambiguity detection: 3 students named Kabir in class 8A (Roll 801, 806, 811)",
            class_label="8A",
            text="8A: 1 absent - Kabir. Covered chapter 3 Linear Equations. Homework Ex 3.2.",
        ),
        DemoMessageItem(
            id="demo-5",
            title="Stated Count Mismatch",
            scenario="Rule R4 verification: teacher stated 3 absent but only named 2 students",
            class_label="8A",
            text="8A: 3 absent - Sneha Reddy, Aditya Das. Covered chapter 3 Linear Equations. Homework Ex 3.2.",
        ),
        DemoMessageItem(
            id="demo-6",
            title="Sunday Date Verification",
            scenario="Rule R6 block: teacher attempted to submit attendance for a Sunday",
            class_label="8A",
            text="8A: 1 absent - Sneha Reddy on 2026-11-15. Covered chapter 3 Linear Equations.",
        ),
    ]
    return messages
