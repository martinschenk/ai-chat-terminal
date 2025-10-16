#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qwen 2.5 Coder SQL Generator (v11.2.0 - Pattern-Powered!)
Generates SQL directly for mydata table with PATTERN-based examples

v11.2.0: Pattern-based examples - ULTRA KISS!
- Uses placeholders <ITEM> instead of concrete words
- AI understands the PATTERN, not specific examples
- Works for ANY data type without updates
- Much shorter prompt, same power!
"""

import subprocess
import sys
import re
import json

class QwenSQLGenerator:
    """Generates SQL queries using Qwen 2.5 Coder 7B - specialized for SQL/code generation"""

    def __init__(self):
        """Initialize Qwen 2.5 Coder"""
        self.model = "qwen2.5-coder:7b"
        self._check_availability()

    def _check_availability(self):
        """Check if Qwen 2.5 Coder is available"""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if 'qwen2.5-coder' not in result.stdout:
                raise RuntimeError("❌ Qwen 2.5 Coder not installed. Run: ollama pull qwen2.5-coder:7b")
        except FileNotFoundError:
            raise RuntimeError("❌ Ollama not installed. Install from: https://ollama.ai")

    def generate_sql(self, user_input: str, action_hint: str) -> dict:
        """
        Generate SQL query from user input (language-agnostic!)

        Args:
            user_input: User's raw input ("save my email test@test.com" or "speichere meine Email...")
            action_hint: Detected action (SAVE, RETRIEVE, DELETE)

        Returns:
            dict: {
                'sql': 'INSERT INTO mydata...' or 'NO_ACTION',
                'action': 'SAVE|RETRIEVE|DELETE|FALSE_POSITIVE',
                'confidence': 0.0-1.0,
                'meta': extracted meta label (optional)
            }

        Note: Qwen 2.5 Coder is multilingual! Prompt contains PATTERN examples.
              Language detection happens automatically - mixed inputs work too!
        """
        # Build multilingual prompt for Qwen (shows PATTERN examples)
        prompt = self._build_prompt(user_input, action_hint)

        # Call Qwen
        result_text = self._call_qwen(prompt)

        # Parse response
        return self._parse_qwen_output(result_text, user_input)

    def _build_prompt(self, user_input: str, action_hint: str) -> str:
        """Build multilingual Qwen prompt with PATTERN-based examples"""
        prompt = f"""You are a multilingual SQL generator for SQLite database 'mydata' with this schema:

CREATE TABLE mydata (
    id INTEGER PRIMARY KEY,
    content TEXT NOT NULL,      -- The actual data
    meta TEXT,                   -- Simple label: "email", "birthday", "API key"
    lang TEXT,                   -- Language: en, de, es
    timestamp INTEGER            -- Unix timestamp (auto-generated)
);

Rules:
1. Generate ONLY valid SQLite SQL
2. Table name MUST be "mydata"
3. For SAVE: Use INSERT OR REPLACE to prevent duplicates
4. For SAVE: Extract description for meta field (keep original language!)
5. For RETRIEVE: Use LIKE for flexible matching
6. For DELETE: Use LIKE to match both meta and content
7. Multi-word meta labels are NORMAL (e.g., "API key", "wifi password")
8. FALSE_POSITIVE only for: database tutorials, unrelated queries
9. Mixed languages OK: "guarda mi email" → extract "email" as meta

Pattern Examples:

SAVE - English (verb synonyms: save, remember, store, keep):
Input: "save my <ITEM> <VALUE>"
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('<VALUE>', '<ITEM>', 'en');

Input: "remember my <ITEM> <VALUE>"
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('<VALUE>', '<ITEM>', 'en');

Input: "my <ITEM> is <VALUE>"
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('<VALUE>', '<ITEM>', 'en');

SAVE - German (verb synonyms: speichere, merke):
Input: "speichere meine <ITEM> <WERT>"
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('<WERT>', '<ITEM>', 'de');

Input: "meine <ITEM> ist <WERT>"
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('<WERT>', '<ITEM>', 'de');

SAVE - Spanish (verb synonyms: guarda, recuerda, almacena):
Input: "guarda mi <ITEM> <VALOR>"
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('<VALOR>', '<ITEM>', 'es');

Input: "recuerda mi <ITEM> <VALOR>"
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('<VALOR>', '<ITEM>', 'es');

Input: "mi <ITEM> es <VALOR>"
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('<VALOR>', '<ITEM>', 'es');

RETRIEVE - English (synonyms: show, what is, get, find, display):
Input: "show my <ITEM>"
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%<ITEM>%' OR content LIKE '%<ITEM>%' ORDER BY timestamp DESC LIMIT 5;

Input: "what is my <ITEM>"
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%<ITEM>%' OR content LIKE '%<ITEM>%' ORDER BY timestamp DESC LIMIT 5;

Input: "list all"
SQL: SELECT id, content, meta, timestamp FROM mydata ORDER BY timestamp DESC;

RETRIEVE - German (synonyms: zeig, was ist, hole, finde):
Input: "zeig meine <ITEM>"
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%<ITEM>%' OR content LIKE '%<ITEM>%' ORDER BY timestamp DESC LIMIT 5;

Input: "was ist meine <ITEM>"
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%<ITEM>%' OR content LIKE '%<ITEM>%' ORDER BY timestamp DESC LIMIT 5;

RETRIEVE - Spanish (synonyms: muestra, qué es, cuál es):
Input: "muestra mi <ITEM>"
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%<ITEM>%' OR content LIKE '%<ITEM>%' ORDER BY timestamp DESC LIMIT 5;

Input: "qué es mi <ITEM>"
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%<ITEM>%' OR content LIKE '%<ITEM>%' ORDER BY timestamp DESC LIMIT 5;

DELETE - English (synonyms: delete, remove, forget):
Input: "delete my <ITEM>"
SQL: DELETE FROM mydata WHERE meta LIKE '%<ITEM>%' OR content LIKE '%<ITEM>%';

Input: "delete all"
SQL: DELETE FROM mydata;

DELETE - German (synonyms: lösche, entferne, vergiss):
Input: "lösche meine <ITEM>"
SQL: DELETE FROM mydata WHERE meta LIKE '%<ITEM>%' OR content LIKE '%<ITEM>%';

DELETE - Spanish (synonyms: borra, elimina, olvida):
Input: "borra mi <ITEM>"
SQL: DELETE FROM mydata WHERE meta LIKE '%<ITEM>%' OR content LIKE '%<ITEM>%';

FALSE POSITIVE:
Input: "how do I save a file?"
SQL: NO_ACTION

Now generate SQL for:
Action: {action_hint}
Input: "{user_input}"

IMPORTANT:
- Detect language automatically from verb
- Extract <ITEM> from input (any word(s) between verb and value)
- <ITEM> can be ANY word: email, correo, Email, teléfono, API key, etc.
- Mixed languages OK: "guarda mi email" → use "email" as meta

Respond with ONLY the SQL statement or "NO_ACTION". No explanation needed.
"""
        return prompt

    def _call_qwen(self, prompt: str) -> str:
        """Call Qwen 2.5 Coder via Ollama"""
        try:
            result = subprocess.run(
                ['ollama', 'run', self.model, prompt],
                capture_output=True,
                text=True,
                timeout=15  # Qwen might take longer for SQL generation
            )

            if result.returncode != 0:
                print(f"⚠️  Qwen error: {result.stderr}", file=sys.stderr)
                return "NO_ACTION"

            return result.stdout.strip()

        except subprocess.TimeoutExpired:
            print("⚠️  Qwen timeout - assuming invalid action", file=sys.stderr)
            return "NO_ACTION"
        except Exception as e:
            print(f"⚠️  Qwen error: {e}", file=sys.stderr)
            return "NO_ACTION"

    def _parse_qwen_output(self, output: str, original_input: str) -> dict:
        """
        Parse Qwen's output to extract SQL

        Args:
            output: Qwen's raw output
            original_input: Original user input

        Returns:
            dict with sql, action, confidence
        """
        # Clean output
        output = output.strip()

        # Remove markdown code blocks if present
        if '```' in output:
            # Extract SQL from code block
            match = re.search(r'```(?:sql)?\s*(.*?)\s*```', output, re.DOTALL | re.IGNORECASE)
            if match:
                output = match.group(1).strip()

        # Check for NO_ACTION
        if 'NO_ACTION' in output.upper() or not output:
            return {
                'sql': 'NO_ACTION',
                'action': 'FALSE_POSITIVE',
                'confidence': 0.9
            }

        # Extract SQL statement (first line that looks like SQL)
        lines = output.split('\n')
        sql = None
        for line in lines:
            line = line.strip()
            # Check if line starts with SQL keyword
            if re.match(r'^(SELECT|INSERT|DELETE|UPDATE)\s+', line, re.IGNORECASE):
                sql = line
                break

        if not sql:
            # No valid SQL found
            return {
                'sql': 'NO_ACTION',
                'action': 'FALSE_POSITIVE',
                'confidence': 0.7
            }

        # Remove trailing semicolon for consistency
        sql = sql.rstrip(';')

        # Determine action from SQL
        sql_upper = sql.upper()
        if sql_upper.startswith('INSERT'):
            action = 'SAVE'
        elif sql_upper.startswith('SELECT'):
            action = 'RETRIEVE'
        elif sql_upper.startswith('DELETE'):
            action = 'DELETE'
        else:
            action = 'UNKNOWN'

        # Extract meta from SQL (for SAVE operations)
        meta = None
        if action == 'SAVE':
            # Try to extract meta from VALUES clause
            match = re.search(r"VALUES\s*\([^,]+,\s*'([^']+)'", sql, re.IGNORECASE)
            if match:
                meta = match.group(1)

        return {
            'sql': sql,
            'action': action,
            'confidence': 0.95,  # Qwen 2.5 Coder is highly accurate for SQL
            'meta': meta
        }

    def validate_sql(self, sql: str) -> tuple:
        """
        Validate SQL for security (prevent SQL injection)

        Args:
            sql: SQL statement to validate

        Returns:
            (is_valid: bool, error_message: str or None)
        """
        if sql == 'NO_ACTION':
            return (True, None)

        sql_upper = sql.upper().strip()

        # Check for dangerous operations
        dangerous = ['DROP', 'ALTER', 'CREATE', 'PRAGMA', 'ATTACH', 'DETACH']
        for cmd in dangerous:
            if cmd in sql_upper:
                return (False, f"Forbidden operation: {cmd}")

        # Must reference mydata table
        if 'MYDATA' not in sql_upper:
            return (False, "SQL must reference 'mydata' table")

        # Must be SELECT, INSERT, or DELETE
        allowed_ops = ['SELECT', 'INSERT', 'DELETE']
        if not any(sql_upper.startswith(op) for op in allowed_ops):
            return (False, f"Only SELECT, INSERT, DELETE allowed. Got: {sql_upper.split()[0]}")

        # Check for multiple statements (SQL injection attempt)
        if ';' in sql and not sql.rstrip(';').count(';') == 0:
            return (False, "Multiple SQL statements not allowed")

        return (True, None)


# Test
if __name__ == '__main__':
    generator = QwenSQLGenerator()

    print("🧪 Testing Qwen 2.5 Coder SQL Generator (Pattern-Based!)\n")

    # Test cases
    tests = [
        ("save my email test@test.com", "SAVE", "en"),
        ("guarda mi email mschenk.pda@gmail.com", "SAVE", "es"),  # Mixed ES+EN!
        ("speichere meine Email test@test.de", "SAVE", "de"),
        ("guarda mi correo test@test.es", "SAVE", "es"),
        ("show my email", "RETRIEVE", "en"),
        ("zeig alle Daten", "RETRIEVE", "de"),
        ("delete my email", "DELETE", "en"),
        ("how do I save a file in Python?", "SAVE", "en"),  # False positive
    ]

    for user_input, action_hint, lang in tests:
        print(f"📝 Input:  {user_input} (action: {action_hint}, lang: {lang})")
        result = generator.generate_sql(user_input, action_hint)

        print(f"   SQL:    {result['sql']}")
        print(f"   Action: {result['action']}")
        print(f"   Confidence: {result['confidence']:.2f}")

        # Validate
        is_valid, error = generator.validate_sql(result['sql'])
        if is_valid:
            print(f"   ✅ Valid SQL")
        else:
            print(f"   ❌ Invalid: {error}")

        print()
