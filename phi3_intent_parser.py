#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phi-3 Smart Intent Parser
Analyzes user messages to determine database intent and extract structured data
"""

import json
import subprocess
import sys
from typing import Dict, Any, Optional, List

class Phi3IntentParser:
    """Smart intent parser using Phi-3 via Ollama"""

    def __init__(self):
        """Initialize Phi-3 parser"""
        self.model = "phi3"
        self._check_availability()

    def _check_availability(self) -> bool:
        """
        Check if Phi-3 is available via Ollama

        Returns:
            True if Phi-3 is available and working

        Raises:
            RuntimeError if Phi-3 is not available (MANDATORY)
        """
        try:
            # Check if ollama command exists
            result = subprocess.run(
                ['which', 'ollama'],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode != 0:
                raise RuntimeError(
                    "❌ Ollama not found!\n"
                    "Phi-3 is MANDATORY for AI Chat Terminal.\n"
                    "Please install Ollama: https://ollama.ai/download"
                )

            # Check if phi3 model is available
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if 'phi3' not in result.stdout:
                print("⚠️  Phi-3 model not found. Attempting to pull...", file=sys.stderr)
                pull_result = subprocess.run(
                    ['ollama', 'pull', 'phi3'],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes for download
                )

                if pull_result.returncode != 0:
                    raise RuntimeError(
                        "❌ Failed to pull Phi-3 model!\n"
                        "Please install manually: ollama pull phi3"
                    )

            # Test inference
            test_result = self._test_inference()
            if not test_result:
                raise RuntimeError(
                    "❌ Phi-3 inference test failed!\n"
                    "Your system may not meet requirements:\n"
                    "  - Apple Silicon Mac (M1/M2/M3/M4) recommended\n"
                    "  - Minimum 8GB RAM\n"
                    "  - Phi-3 requires ~2GB disk space"
                )

            return True

        except subprocess.TimeoutExpired:
            raise RuntimeError("❌ Ollama command timed out. Is Ollama running?")
        except FileNotFoundError:
            raise RuntimeError(
                "❌ Ollama not found!\n"
                "Phi-3 is MANDATORY for AI Chat Terminal.\n"
                "Please install Ollama: https://ollama.ai/download"
            )

    def _test_inference(self) -> bool:
        """Test if Phi-3 can perform inference"""
        try:
            result = subprocess.run(
                ['ollama', 'run', 'phi3', 'Say OK'],
                capture_output=True,
                text=True,
                timeout=10
            )
            # Just check if ollama run completed successfully (returncode 0)
            # Output may contain ANSI codes, so don't check stdout content
            return result.returncode == 0
        except:
            return False

    def parse_intent(self, user_message: str, matched_keywords: List[str]) -> Dict[str, Any]:
        """
        Parse user intent using Phi-3

        Args:
            user_message: The user's input
            matched_keywords: Keywords that triggered DB intent detection

        Returns:
            Dictionary with:
                - action: SAVE|RETRIEVE|DELETE|LIST|UPDATE|NORMAL
                - confidence: 0.0-1.0
                - reasoning: why this action was chosen
                - false_positive: True if keyword match was false positive
                - data: extracted structured data (or None for NORMAL)
        """
        prompt = self._build_prompt(user_message, matched_keywords)

        try:
            # Call Phi-3 via Ollama
            result = subprocess.run(
                ['ollama', 'run', 'phi3', prompt],
                capture_output=True,
                text=True,
                timeout=15
            )

            if result.returncode != 0:
                print(f"⚠️  Phi-3 error: {result.stderr}", file=sys.stderr)
                return self._fallback_response()

            # Parse JSON response
            response_text = result.stdout.strip()

            # Extract JSON from response (Phi-3 might add extra text)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                print(f"⚠️  No JSON in Phi-3 response: {response_text[:100]}", file=sys.stderr)
                return self._fallback_response(user_message, matched_keywords)

            json_str = response_text[json_start:json_end]

            # Clean up JSON: remove comments and fix common issues
            import re
            # Remove // comments (Phi-3 sometimes adds them)
            json_str = re.sub(r'//[^\n]*', '', json_str)

            # Try to fix incomplete JSON (truncated reasoning field)
            if not json_str.endswith('}'):
                # Response was truncated - try to close it properly
                # Find last complete field and close JSON
                last_quote = json_str.rfind('"')
                if last_quote > 0:
                    # Truncate to last complete field
                    json_str = json_str[:last_quote+1]
                    # Close the JSON object
                    json_str += '\n  }\n}'

            parsed = json.loads(json_str)

            return parsed

        except subprocess.TimeoutExpired:
            print("⚠️  Phi-3 inference timeout", file=sys.stderr)
            return self._fallback_response(user_message, matched_keywords)
        except json.JSONDecodeError as e:
            print(f"⚠️  Failed to parse Phi-3 JSON: {e}", file=sys.stderr)
            print(f"⚠️  Problematic JSON: {json_str[:200]}", file=sys.stderr)
            # Try to extract action from malformed JSON
            if 'RETRIEVE' in response_text.upper():
                return {
                    "action": "RETRIEVE",
                    "confidence": 0.7,
                    "reasoning": "Recovered from JSON parse error - detected RETRIEVE intent",
                    "false_positive": False,
                    "data": {"type": "unknown", "query": user_message}
                }
            return self._fallback_response(user_message, matched_keywords)
        except Exception as e:
            print(f"⚠️  Phi-3 error: {e}", file=sys.stderr)
            return self._fallback_response(user_message, matched_keywords)

    def _build_prompt(self, user_message: str, matched_keywords: List[str]) -> str:
        """Build ULTRA-KISS Phi-3 prompt - simple and fast"""

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

    def _fallback_response(self, user_message: str = "", matched_keywords: List[str] = None) -> Dict[str, Any]:
        """Intelligent fallback response if Phi-3 fails - tries to guess intent from keywords"""

        # If we have keywords, try to guess the action
        if matched_keywords:
            msg_lower = user_message.lower()

            # RETRIEVE indicators: hole, get, wie ist, was ist mein/e
            if any(kw in msg_lower for kw in ['hole', 'get', 'wie ist', 'was ist mein', 'what is my']):
                return {
                    "action": "RETRIEVE",
                    "confidence": 0.6,
                    "reasoning": "Phi-3 failed, guessed RETRIEVE from keywords",
                    "false_positive": False,
                    "data": {"type": "unknown", "query": user_message}
                }

            # LIST indicators: zeig, liste, list, show all
            if any(kw in msg_lower for kw in ['zeig', 'liste', 'list', 'show', 'alle']):
                return {
                    "action": "LIST",
                    "confidence": 0.6,
                    "reasoning": "Phi-3 failed, guessed LIST from keywords",
                    "false_positive": False,
                    "data": {}
                }

            # DELETE indicators: vergiss, lösche, delete, forget
            if any(kw in msg_lower for kw in ['vergiss', 'lösche', 'delete', 'forget', 'remove']):
                return {
                    "action": "DELETE",
                    "confidence": 0.6,
                    "reasoning": "Phi-3 failed, guessed DELETE from keywords",
                    "false_positive": False,
                    "data": {"target": user_message}
                }

        # Default: send to OpenAI
        return {
            "action": "NORMAL",
            "confidence": 0.5,
            "reasoning": "Phi-3 inference failed, defaulting to OpenAI",
            "false_positive": True,
            "data": None
        }


# For testing
if __name__ == '__main__':
    parser = Phi3IntentParser()

    test_cases = [
        ("merke dir meine Email ist test@test.com", ['merke', 'speicher']),
        ("wie ist meine Telefonnummer?", ['meine']),
        ("zeig mir alles was du gespeichert hast", ['zeig', 'gespeichert']),
        ("Was ist eine Datenbank?", ['datenbank']),
        ("Ich habe das in der DB gespeichert", ['db', 'gespeichert']),
    ]

    print("🧪 Testing Phi-3 Intent Parser\n")

    for message, keywords in test_cases:
        print(f"📝 User: {message}")
        print(f"🔑 Keywords: {keywords}")

        result = parser.parse_intent(message, keywords)

        print(f"🤖 Action: {result['action']}")
        print(f"📊 Confidence: {result['confidence']}")
        print(f"💭 Reasoning: {result['reasoning']}")
        print(f"🚨 False Positive: {result['false_positive']}")
        if result['data']:
            print(f"📦 Data: {json.dumps(result['data'], indent=2, ensure_ascii=False)}")
        print()
