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
        """Build the Phi-3 prompt with false-positive detection"""

        keywords_str = ', '.join(matched_keywords) if matched_keywords else 'none'

        # Escape user message for safe inclusion in prompt (avoid @ and other special chars breaking JSON)
        safe_message = user_message.replace('"', '\\"').replace('\n', ' ')

        return f"""You are a MULTILINGUAL local database assistant (German/English/Spanish).
Keywords detected: [{keywords_str}] in message: "{safe_message}"

⚡ YOUR TASK:
Determine if this is a REAL database operation or FALSE POSITIVE.

📊 ACTIONS:
- SAVE: Store NEW data in local DB
- RETRIEVE: Get STORED data from local DB
- DELETE: Remove data from local DB
- LIST: Show ALL stored data
- UPDATE: Modify existing data
- NORMAL: FALSE POSITIVE (not a DB command → send to OpenAI)

🚨 CRITICAL RULES FOR RETRIEVE:

1. **"meine/my/mi X"** + keywords = RETRIEVE
   - "wie ist meine email?" → RETRIEVE
   - "what's my phone?" → RETRIEVE
   - "cuál es mi email?" → RETRIEVE

2. **"gespeicherte/stored/guardado"** = RETRIEVE
   - "meine gespeicherte email" → RETRIEVE
   - "my stored password" → RETRIEVE
   - "mi número guardado" → RETRIEVE

3. **Personal data questions** = RETRIEVE
   - Email, phone, address, password, API key, etc.
   - If user asks for THEIR data → RETRIEVE

4. **DB-explicit** = RETRIEVE
   - "hole aus db" / "get from db" / "saca de db" → RETRIEVE
   - "was ist in db?" / "what's in db?" → RETRIEVE

⛔ FALSE POSITIVES (send to OpenAI):
- Past tense stories: "Ich hatte gespeichert..." (telling a story)
- Educational: "Was ist eine Datenbank?" (learning question)
- General knowledge: "Wann wurde Einstein geboren?" (facts, NOT personal data)
- Weather/news: "Wie wird das Wetter?" (external info)
- Different context: "In der lokalen Zeitung..." ('lokal' ≠ database)

💡 DECISION LOGIC:
IF (keywords matched) AND (user asks for PERSONAL data) → RETRIEVE
IF (keywords matched) AND (command to save/delete/list) → SAVE/DELETE/LIST
IF (general knowledge OR educational OR past tense story) → FALSE POSITIVE

📝 MULTILINGUAL EXAMPLES:

**GERMAN (DE):**
✅ SAVE: "Merke dir meine Email ist test@test.com" | "speichere meine telefonnummer 123"
✅ RETRIEVE: "wie ist meine email?" | "meine gespeicherte telefonnummer?" | "hole meine adresse"
✅ LIST: "was hast du gespeichert?" | "zeig mir alle daten" | "db list"
✅ DELETE: "vergiss meine email" | "lösche telefonnummer"
❌ FALSE: "Ich habe gespeichert" (past) | "Was ist eine DB?" (educational) | "Wetter morgen?" (general)

**ENGLISH (EN):**
✅ SAVE: "remember my email is test@test.com" | "save my phone 123"
✅ RETRIEVE: "what's my email?" | "my stored phone number?" | "get my address from db"
✅ LIST: "what did you save?" | "show me all data" | "list db"
✅ DELETE: "forget my email" | "delete my phone"
❌ FALSE: "I saved it" (past) | "What is a database?" (educational) | "weather tomorrow?" (general)

**SPANISH (ES):**
✅ SAVE: "recuerda mi email es test@test.com" | "guarda mi teléfono 123"
✅ RETRIEVE: "cuál es mi email?" | "mi número guardado?" | "dame mi dirección"
✅ LIST: "qué has guardado?" | "muéstrame todos los datos" | "lista db"
✅ DELETE: "olvida mi email" | "borra mi teléfono"
❌ FALSE: "Lo guardé" (past) | "Qué es una base de datos?" (educational) | "clima mañana?" (general)

🎯 SMART RULES:
1. Personal data question ("my/meine/mi" + email/phone/etc) → RETRIEVE
2. Command with data ("save/speichere/guarda" + value) → SAVE
3. Request to show stored items → LIST
4. General knowledge / past tense / educational → FALSE POSITIVE

RESPOND IN JSON (NO COMMENTS, PURE JSON ONLY):
{{
  "action": "SAVE|RETRIEVE|DELETE|LIST|UPDATE|NORMAL",
  "confidence": 0.0-1.0,
  "reasoning": "short reason (max 50 chars)",
  "false_positive": true|false,
  "data": {{
    "type": "email|phone|name|address|api_key|password|note|...",
    "value": "the actual data",
    "label": "how user refers to it",
    "context": "additional info"
  }}
}}

IMPORTANT:
- NO // comments in JSON!
- Keep reasoning SHORT (max 50 characters)
- PURE JSON ONLY!

EXAMPLES:

User: "merke dir meine Email ist max@test.com"
Keywords: ['merke', 'speicher']
{{
  "action": "SAVE",
  "confidence": 0.98,
  "reasoning": "Save email command",
  "false_positive": false,
  "data": {{
    "type": "email",
    "value": "max@test.com",
    "label": "meine Email",
    "context": "user's personal email address"
  }}
}}

User: "wie war nochmal meine Telefonnummer?"
Keywords: ['meine']
{{
  "action": "RETRIEVE",
  "confidence": 0.95,
  "reasoning": "User asking for their stored phone number",
  "false_positive": false,
  "data": {{
    "type": "phone_number",
    "query": "Telefonnummer",
    "label": "meine Telefonnummer"
  }}
}}

User: "wie ist meine email in der db?"
Keywords: ['db', 'meine']
{{
  "action": "RETRIEVE",
  "confidence": 0.97,
  "reasoning": "Asking for stored email from database",
  "false_positive": false,
  "data": {{
    "type": "email",
    "query": "email",
    "label": "meine email"
  }}
}}

User: "wie ist meine gespeicherte email adresse?"
Keywords: ['meine', 'gespeichert']
{{
  "action": "RETRIEVE",
  "confidence": 0.95,
  "reasoning": "Asking for stored email - 'gespeicherte' indicates stored data",
  "false_positive": false,
  "data": {{
    "type": "email",
    "query": "email adresse",
    "label": "gespeicherte email"
  }}
}}

User: "was hast du über mich in der lokalen db gespeichert?"
Keywords: ['lokal', 'db', 'gespeichert']
{{
  "action": "LIST",
  "confidence": 0.96,
  "reasoning": "Asking what's stored about them - LIST operation",
  "false_positive": false,
  "data": {{
    "filter": "user_data"
  }}
}}

User: "liste alle lokalen daten auf"
Keywords: ['lokal']
{{
  "action": "LIST",
  "confidence": 0.97,
  "reasoning": "Clear command to list all stored data - imperative verb 'liste' indicates command",
  "false_positive": false,
  "data": {{
    "filter": null
  }}
}}

User: "db list"
Keywords: ['db']
{{
  "action": "LIST",
  "confidence": 0.99,
  "reasoning": "Direct database command to list data - 'db list' is a clear technical command",
  "false_positive": false,
  "data": {{
    "filter": null
  }}
}}

User: "Ich habe die Daten in der Datenbank gespeichert"
Keywords: ['datenbank', 'gespeichert']
{{
  "action": "NORMAL",
  "confidence": 0.92,
  "reasoning": "User talking ABOUT saving to a database (past tense), not commanding me to save. This is a false positive.",
  "false_positive": true,
  "data": null
}}

User: "Was ist eine lokale Datenbank?"
Keywords: ['lokal', 'datenbank']
{{
  "action": "NORMAL",
  "confidence": 0.96,
  "reasoning": "Educational question",
  "false_positive": true,
  "data": null
}}

User: "zeige mir wann albert einstein geboren wurde"
Keywords: ['zeig']
{{
  "action": "NORMAL",
  "confidence": 0.99,
  "reasoning": "General knowledge, not personal data",
  "false_positive": true,
  "data": null
}}

NOW ANALYZE THIS REQUEST AND RESPOND WITH JSON ONLY:
User: "{safe_message}"
Keywords detected: [{keywords_str}]
"""

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
