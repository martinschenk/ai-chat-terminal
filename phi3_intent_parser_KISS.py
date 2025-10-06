#!/usr/bin/env python3
"""
Phi-3 Intent Parser - ULTRA KISS VERSION
Simple, short prompt - NO complex rules!
"""
import json
import subprocess
import sys

def parse_intent_kiss(user_message: str, keywords: list) -> dict:
    """
    KISS Version: Ultra-short Phi-3 prompt

    Args:
        user_message: User input
        keywords: Matched keywords

    Returns:
        {"action": "SAVE|RETRIEVE|DELETE|LIST|NORMAL", "data": {...}}
    """

    # Ultra-short prompt
    prompt = f"""Classify database intent.

Message: "{user_message}"

Rules:
- "save/remember X" with data → SAVE
- "show/what's my X" → RETRIEVE
- "delete/forget X" → DELETE
- "list/all data" → LIST
- Otherwise → NORMAL

JSON response:
{{
  "action": "SAVE|RETRIEVE|DELETE|LIST|NORMAL",
  "data": {{
    "type": "email|phone|address|note",
    "value": "extracted data"
  }}
}}
"""

    try:
        result = subprocess.run(
            ['ollama', 'run', 'phi3'],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=10  # Faster timeout!
        )

        if result.returncode == 0:
            # Parse JSON from output
            output = result.stdout.strip()
            # Find JSON in output
            start = output.find('{')
            end = output.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = output[start:end]
                return json.loads(json_str)

    except Exception as e:
        print(f"Phi-3 error: {e}", file=sys.stderr)

    # Fallback
    return {"action": "NORMAL", "data": {}}

if __name__ == "__main__":
    # Test
    tests = [
        "save my phone 123456",
        "show my email",
        "what data do you have?"
    ]

    for test in tests:
        result = parse_intent_kiss(test, ["save", "show", "data"])
        print(f"{test} → {result['action']}")
