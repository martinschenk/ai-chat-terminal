#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Llama 3.2 Data Extractor (v10.1.0 - Multilingual!)
Extrahiert NUR die Daten aus User-Input (EN/DE/ES), KEINE Intent-Classification!
"""

import subprocess
import sys
import re

class LlamaDataExtractor:
    """Extrahiert Daten aus User-Prompts mit Llama 3.2 (3B) - Multilingual: EN, DE, ES"""

    def __init__(self):
        """Initialize Llama 3.2"""
        self.model = "llama3.2:3b"
        self._check_availability()

    def _check_availability(self):
        """Check if Llama 3.2 is available"""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if 'llama3.2' not in result.stdout:
                raise RuntimeError("❌ Llama 3.2 not installed. Run: ollama pull llama3.2:3b")
        except FileNotFoundError:
            raise RuntimeError("❌ Ollama not installed. Install from: https://ollama.ai")

    def extract_for_save(self, user_input: str) -> tuple:
        """
        Extract data to save from user input (Multilingual: EN/DE/ES)

        Args:
            user_input: "save my email test@test.com" or "speichere meine Email test@test.de"

        Returns:
            tuple: ("email: test@test.com", "llama") or (data, "regex")
        """
        # SAVE prompt with proper context structure
        prompt = f"""Extract data in format "description: value"

Example 1:
User wants to: SAVE
User said: save my email address test@example.com
Extract: email address: test@example.com

Example 2:
User wants to: SAVE
User said: remember my phone number 234324987
Extract: phone number: 234324987

Example 3:
User wants to: SAVE
User said: save my sisters birthday 02 July 1998
Extract: sisters birthday: 02 July 1998

Example 4:
User wants to: SAVE
User said: speichere meine Email Adresse test@test.de
Extract: Email Adresse: test@test.de

Example 5:
User wants to: SAVE
User said: merke Omas Geburtstag 15.03.1950
Extract: Omas Geburtstag: 15.03.1950

Example 6:
User wants to: SAVE
User said: guarda mi correo test@ejemplo.es
Extract: correo: test@ejemplo.es

Example 7:
User wants to: SAVE
User said: guarda cumpleaños de hermana 02 Julio 1998
Extract: cumpleaños de hermana: 02 Julio 1998

Now extract:
User wants to: SAVE
User said: {user_input}
Extract: """

        result = self._call_llama(prompt).strip()

        # Clean hallucinated brackets
        result = re.sub(r'^\[.*?\]\s*', '', result)  # Remove "[email] " prefix
        result = re.sub(r'\[.*?\]', '', result)       # Remove any [tags]
        result = result.strip()

        # Fallback: If Llama fails, do simple regex extraction
        if not result or len(result) > 100:
            # Extract everything after keywords
            cleaned = re.sub(r'^(save|remember|store|keep|merke|speicher|guarda)\s+(my|meine?|mi)\s+', '', user_input, flags=re.IGNORECASE)
            return (cleaned, 'regex')

        return (result, 'llama')

    def extract_for_retrieve(self, user_input: str) -> tuple:
        """
        Extract what user is looking for (Multilingual: EN/DE/ES)

        Args:
            user_input: "show my email" or "zeig meine Email"

        Returns:
            tuple: ("email", "llama") or (data, "regex")
        """
        # RETRIEVE prompt with proper context structure
        prompt = f"""Extract what user is searching for. Keep FULL phrase.

Example 1:
User wants to: RETRIEVE
User said: show my email address
Extract: email address

Example 2:
User wants to: RETRIEVE
User said: show my sisters birthday
Extract: sisters birthday

Example 3:
User wants to: RETRIEVE
User said: what's my phone number
Extract: phone number

Example 4:
User wants to: RETRIEVE
User said: zeig meine Email Adresse
Extract: Email Adresse

Example 5:
User wants to: RETRIEVE
User said: zeig Omas Geburtstag
Extract: Omas Geburtstag

Example 6:
User wants to: RETRIEVE
User said: muestra mi dirección de correo
Extract: dirección de correo

Example 7:
User wants to: RETRIEVE
User said: muestra cumpleaños de hermana
Extract: cumpleaños de hermana

Now extract:
User wants to: RETRIEVE
User said: {user_input}
Extract: """

        result = self._call_llama(prompt).strip()

        # Fallback: Simple keyword extraction
        if not result or len(result) > 30:
            # Remove common words
            cleaned = re.sub(r'\b(show|get|what|what\'s|my|mein|meine|mi|zeig|muestra)\b', '', user_input, flags=re.IGNORECASE)
            cleaned = cleaned.strip(' ?.,!')
            return (cleaned if cleaned else user_input, 'regex')

        return (result, 'llama')

    def extract_for_delete(self, user_input: str) -> tuple:
        """
        Extract what user wants to delete (Multilingual: EN/DE/ES)

        Args:
            user_input: "delete my email" or "lösche meine Email"

        Returns:
            tuple: ("email", "llama") or (data, "regex")
        """
        # DELETE prompt with proper context structure
        prompt = f"""Extract what user wants to delete. Keep FULL phrase.

Example 1:
User wants to: DELETE
User said: delete my email address
Extract: email address

Example 2:
User wants to: DELETE
User said: forget my phone number
Extract: phone number

Example 3:
User wants to: DELETE
User said: remove my sisters birthday
Extract: sisters birthday

Example 4:
User wants to: DELETE
User said: lösche meine Email Adresse
Extract: Email Adresse

Example 5:
User wants to: DELETE
User said: vergiss Omas Geburtstag
Extract: Omas Geburtstag

Example 6:
User wants to: DELETE
User said: borra mi dirección de correo
Extract: dirección de correo

Example 7:
User wants to: DELETE
User said: olvida cumpleaños de hermana
Extract: cumpleaños de hermana

Now extract:
User wants to: DELETE
User said: {user_input}
Extract: """

        result = self._call_llama(prompt).strip()

        # Fallback: Simple keyword extraction
        if not result or len(result) > 30:
            # Remove common words
            cleaned = re.sub(r'\b(delete|forget|remove|erase|lösche|vergiss|borra|my|mein|meine|mi)\b', '', user_input, flags=re.IGNORECASE)
            cleaned = cleaned.strip(' ?.,!')
            return (cleaned if cleaned else user_input, 'regex')

        return (result, 'llama')

    def extract_for_list(self, user_input: str) -> tuple:
        """
        Extract what user wants to list (filter) or '*' for all (Multilingual: EN/DE/ES)

        Args:
            user_input: "show all my emails" or "zeig alle Daten"

        Returns:
            tuple: ("email", "llama") or ("*", "llama") for all data
        """
        # LIST prompt with proper context structure
        prompt = f"""Extract what type of data user wants to list. Return "*" for everything.

Example 1:
User wants to: LIST
User said: show all my email addresses
Extract: email address

Example 2:
User wants to: LIST
User said: list my phone numbers
Extract: phone number

Example 3:
User wants to: LIST
User said: show all my data
Extract: *

Example 4:
User wants to: LIST
User said: list everything
Extract: *

Example 5:
User wants to: LIST
User said: zeig alle Email Adressen
Extract: Email Adresse

Example 6:
User wants to: LIST
User said: zeig alle meine Daten
Extract: *

Example 7:
User wants to: LIST
User said: lista todo
Extract: *

Now extract:
User wants to: LIST
User said: {user_input}
Extract: """

        result = self._call_llama(prompt).strip()

        # Fallback: Check for "all" keywords
        if not result or len(result) > 30:
            if re.search(r'\b(all|everything|alle|todo|tous|alles)\b', user_input, re.IGNORECASE):
                return ('*', 'regex')
            # Try to extract specific type
            cleaned = re.sub(r'\b(show|list|display|get|all|my|mein|meine|mi|zeig|liste|muestra)\b', '', user_input, flags=re.IGNORECASE)
            cleaned = cleaned.strip(' ?.,!')
            return (cleaned if cleaned else '*', 'regex')

        return (result, 'llama')

    def _call_llama(self, prompt: str) -> str:
        """Call Llama 3.2 via Ollama"""
        try:
            result = subprocess.run(
                ['ollama', 'run', 'llama3.2:3b', prompt],
                capture_output=True,
                text=True,
                timeout=15  # Llama might be slower than Phi-3
            )

            if result.returncode != 0:
                print(f"⚠️  Llama error: {result.stderr}", file=sys.stderr)
                return ""

            # Clean output
            output = result.stdout.strip()

            # Remove markdown code blocks if present
            if '```' in output:
                lines = output.split('\n')
                # Find lines between ```
                in_code = False
                clean_lines = []
                for line in lines:
                    if line.strip().startswith('```'):
                        in_code = not in_code
                        continue
                    if not in_code:
                        clean_lines.append(line)
                output = '\n'.join(clean_lines).strip()

            # Remove Llama's explanatory text (e.g., "Here is the extracted data...")
            # Keep only the last line if multiple lines
            if '\n' in output:
                lines = [l.strip() for l in output.split('\n') if l.strip()]
                # Find the line that looks like extracted data (contains ":" usually)
                for line in reversed(lines):
                    if ':' in line or line == '*':
                        output = line
                        break
                else:
                    # No colon found, take last non-empty line
                    output = lines[-1] if lines else output

            return output

        except subprocess.TimeoutExpired:
            print("⚠️  Llama timeout", file=sys.stderr)
            return ""
        except Exception as e:
            print(f"⚠️  Llama error: {e}", file=sys.stderr)
            return ""


# Test
if __name__ == '__main__':
    extractor = LlamaDataExtractor()

    print("🧪 Testing Llama 3.2 Data Extractor (Multilingual)\n")

    # Test SAVE - Multilingual
    tests = [
        ("save my email address test@test.com", "extract_for_save"),
        ("speichere meine Email test@test.de", "extract_for_save"),
        ("guarda mi correo test@test.es", "extract_for_save"),
        ("save my sisters birthday 02 July 1998", "extract_for_save"),
        ("show my sisters birthday", "extract_for_retrieve"),
        ("zeig Omas Geburtstag", "extract_for_retrieve"),
        ("delete my email", "extract_for_delete"),
        ("list all my data", "extract_for_list"),
    ]

    for user_input, method in tests:
        print(f"Input:  {user_input}")
        data, extraction_method = getattr(extractor, method)(user_input)
        print(f"Output: {data}")
        print(f"Method: {extraction_method}\n")
