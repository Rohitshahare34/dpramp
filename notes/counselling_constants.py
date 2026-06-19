"""Shared constants for engineering admission counselling."""

from urllib.parse import quote

COUNSELLING_WHATSAPP_NUMBER = "919359919779"
COUNSELLING_WHATSAPP_MESSAGE = (
    "Hi DPRAMP, I need Engineering Admission Counselling guidance for 2026."
)
COUNSELLING_WHATSAPP_URL = (
    f"https://wa.me/{COUNSELLING_WHATSAPP_NUMBER}"
    f"?text={quote(COUNSELLING_WHATSAPP_MESSAGE)}"
)

COUNSELLING_BRANCH_CHOICES = [
    ("", "Select branch (optional)"),
    ("cse", "CSE — Computer Science & Engineering"),
    ("it", "IT — Information Technology"),
    ("ct", "CT — Computer Technology"),
    ("ai", "AI — Artificial Intelligence"),
    ("ds", "DS — Data Science"),
    ("cs", "CS — Computer Systems"),
    ("et", "ET — Electronics & Telecommunication"),
    ("ee", "EE — Electrical Engineering"),
    ("me", "ME — Mechanical Engineering"),
    ("other", "Other / Not sure yet"),
]
