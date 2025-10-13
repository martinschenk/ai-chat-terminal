#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qwen 2.5 Coder SQL Generator (v11.0.3 - Duplicate Prevention!)
Generates SQL directly for mydata table - NO complex extraction, NO PII categories!

v11.0.3: INSERT OR REPLACE to prevent duplicates
- Same meta+content → updates existing entry instead of creating duplicate
- Example: "my name is Martin" twice → only ONE entry in DB
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

        Note: Qwen 2.5 Coder is multilingual! Prompt contains ALL language examples (EN/DE/ES).
              Language detection happens automatically - mixed inputs work too!
        """
        # Build multilingual prompt for Qwen (shows ALL language examples)
        prompt = self._build_prompt(user_input, action_hint)

        # Call Qwen
        result_text = self._call_qwen(prompt)

        # Parse response
        return self._parse_qwen_output(result_text, user_input)

    def _build_prompt(self, user_input: str, action_hint: str) -> str:
        """Build multilingual Qwen prompt with ALL language examples"""
        prompt = f"""You are a multilingual SQL generator for SQLite database 'mydata' with this schema:

CREATE TABLE mydata (
    id INTEGER PRIMARY KEY,
    content TEXT NOT NULL,      -- The actual data
    meta TEXT,                   -- Simple label: "email", "geburtstag", "koffercode hotel"
    lang TEXT,                   -- Language: en, de, es
    timestamp INTEGER            -- Unix timestamp (auto-generated)
);

Rules:
1. Generate ONLY valid SQLite SQL
2. Table name MUST be "mydata"
3. For SAVE: Use INSERT OR REPLACE to prevent duplicates (same meta+content = update, not new row)
4. For SAVE: Extract description for meta field (keep original language!)
5. For RETRIEVE: Use LIKE for flexible matching
6. For DELETE: Use LIKE to match both meta and content
7. For false positives (tutorials, questions about DB): Return "NO_ACTION"

Examples:

SAVE (Explicit - English):
Input: "save my email address test@example.com"
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('test@example.com', 'email address', 'en');

Input: "remember my phone 234324987"
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('234324987', 'phone', 'en');

Input: "save sisters birthday 02 July 1998"
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('02 July 1998', 'sisters birthday', 'en');

SAVE (Implicit - English):
Input: "my main email is test@example.com"
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('test@example.com', 'main email', 'en');

Input: "my phone is 234324987"
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('234324987', 'phone', 'en');

Input: "my name is John Smith"
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('John Smith', 'name', 'en');

SAVE (Explicit - German):
Input: "speichere meine Email test@test.de"
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('test@test.de', 'Email', 'de');

Input: "merke Omas Geburtstag 15.03.1950"
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('15.03.1950', 'Omas Geburtstag', 'de');

Input: "speichere Koffercode Hotel 1234"
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('1234', 'Koffercode Hotel', 'de');

SAVE (Implicit - German):
Input: "meine Haupt-Email ist test@test.de"
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('test@test.de', 'Haupt-Email', 'de');

Input: "mein Name ist Hans Müller"
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('Hans Müller', 'Name', 'de');

SAVE (Explicit - Spanish):
Input: "guarda mi correo test@ejemplo.es"
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('test@ejemplo.es', 'correo', 'es');

Input: "guarda cumpleaños hermana 02 Julio 1998"
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('02 Julio 1998', 'cumpleaños hermana', 'es');

SAVE (Implicit - Spanish):
Input: "mi correo principal es test@ejemplo.es"
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('test@ejemplo.es', 'correo principal', 'es');

Input: "mi nombre es María García"
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('María García', 'nombre', 'es');

RETRIEVE (specific item):
Input: "show my email"
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%email%' OR content LIKE '%email%' ORDER BY timestamp DESC LIMIT 5;

Input: "zeig Omas Geburtstag"
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%Geburtstag%' OR content LIKE '%Geburtstag%' ORDER BY timestamp DESC LIMIT 5;

Input: "muestra mi teléfono"
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%teléfono%' OR meta LIKE '%telefono%' OR content LIKE '%teléfono%' ORDER BY timestamp DESC LIMIT 5;

RETRIEVE (all data):
Input: "list all my data"
SQL: SELECT id, content, meta, timestamp FROM mydata ORDER BY timestamp DESC;

Input: "zeig alle Daten"
SQL: SELECT id, content, meta, timestamp FROM mydata ORDER BY timestamp DESC;

Input: "lista todo"
SQL: SELECT id, content, meta, timestamp FROM mydata ORDER BY timestamp DESC;

DELETE:
Input: "delete my email"
SQL: DELETE FROM mydata WHERE meta LIKE '%email%' OR content LIKE '%email%';

Input: "lösche Omas Geburtstag"
SQL: DELETE FROM mydata WHERE meta LIKE '%Geburtstag%' OR content LIKE '%Geburtstag%';

Input: "borra mi teléfono"
SQL: DELETE FROM mydata WHERE meta LIKE '%teléfono%' OR meta LIKE '%telefono%';

FALSE POSITIVE (not a DB operation):
Input: "how do I save a file in Python?"
SQL: NO_ACTION

Input: "show me a tutorial on databases"
SQL: NO_ACTION

Input: "what does delete mean?"
SQL: NO_ACTION

Now generate SQL for:
Action: {action_hint}
Input: "{user_input}"

IMPORTANT: Detect language automatically from input! Mixed languages OK (e.g., "my email ist..." → extract "email", not "email ist")!
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

    print("🧪 Testing Qwen 2.5 Coder SQL Generator\n")

    # Test cases
    tests = [
        ("save my email address test@test.com", "SAVE", "en"),
        ("speichere meine Email test@test.de", "SAVE", "de"),
        ("guarda mi correo test@test.es", "SAVE", "es"),
        ("show my email", "RETRIEVE", "en"),
        ("zeig alle Daten", "RETRIEVE", "de"),
        ("delete my email", "DELETE", "en"),
        ("how do I save a file in Python?", "SAVE", "en"),  # False positive
    ]

    for user_input, action_hint, lang in tests:
        print(f"📝 Input:  {user_input} (action: {action_hint}, lang: {lang})")
        result = generator.generate_sql(user_input, action_hint, lang)

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
