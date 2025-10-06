#!/usr/bin/env python3
"""
Phi-3 Intent Parser - ULTRA KISS VERSION v2
Clean implementation without leftover code
"""

def build_kiss_prompt(user_message: str, matched_keywords: list) -> str:
    """
    Build ULTRA-KISS Phi-3 prompt - simple and fast

    Args:
        user_message: User input
        matched_keywords: Keywords detected (not used in KISS version)

    Returns:
        Simple Phi-3 prompt
    """
    # Escape user message for safe JSON
    safe_message = user_message.replace('"', '\\"').replace('\n', ' ')

    return f"""Classify database intent.

Message: "{safe_message}"

Rules:
- "save/remember/remind X" with data (email@, phone number, address) → SAVE
- "show/what/which is my X" (specific item) → RETRIEVE
- "delete/forget X" → DELETE
- "list/all/show all" → LIST
- Otherwise → NORMAL

EXAMPLES:
"save my phone 123456" → SAVE
"show my phone" → RETRIEVE
"what's my email?" → RETRIEVE
"list all data" → LIST
"delete my email" → DELETE
"hello there" → NORMAL

JSON response:
{{
  "action": "SAVE|RETRIEVE|DELETE|LIST|NORMAL",
  "data": {{
    "type": "email|phone|address|note",
    "value": "extracted data if SAVE"
  }}
}}"""


if __name__ == "__main__":
    # Test
    tests = [
        "save my phone number 13243546",
        "show my phone number",
        "show my email",
        "what data do you have?",
        "delete my phone"
    ]

    for test in tests:
        prompt = build_kiss_prompt(test, [])
        print(f"\n{'='*60}")
        print(f"TEST: {test}")
        print(f"{'='*60}")
        print(prompt)
