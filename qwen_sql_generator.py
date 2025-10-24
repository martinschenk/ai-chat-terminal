#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qwen 2.5 Coder SQL Generator (v11.5.1 - Intent-Based Detection!)
Generates SQL directly for mydata table with SPECIALIZED prompts per action

v11.5.1: Intent over Pattern Matching (KISS!)
- Added _get_intent_principle() helper - DRY for all 3 prompts
- SAVE: Intent block + diverse examples (address, birthday, wifi password)
- RETRIEVE: Removed ALL LIMIT logic - always show everything (simpler!)
- DELETE: Intent block + diverse examples
- "Examples show PATTERNS, not complete list" - works with ANY label!
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

    def _get_intent_principle(self, operation: str) -> str:
        """
        Returns intent detection block for SAVE/RETRIEVE/DELETE (v11.5.1)

        Args:
            operation: 'SAVE', 'RETRIEVE', or 'DELETE'

        Returns:
            Formatted intent detection block with examples
        """
        examples = {
            'SAVE': [
                "✅ YES: 'guarda mi dirección Hiruela 3' (wants to store address)",
                "✅ YES: 'save my license plate ABC-123' (wants to store license)",
                "✅ YES: 'speichere mein Passwort Secret123' (wants to store password)",
                "❌ NO: 'how do I save a file?' (tutorial question)",
                "❌ NO: 'save money for vacation' (idiom, no data)"
            ],
            'RETRIEVE': [
                "✅ YES: 'muestra mi dirección' (wants stored address)",
                "✅ YES: 'show all emails' (wants stored emails)",
                "✅ YES: 'zeig meine Notizen' (wants stored notes)",
                "❌ NO: 'show me how to code' (tutorial request)",
                "❌ NO: 'find nearest restaurant' (external location search)"
            ],
            'DELETE': [
                "✅ YES: 'borra mi dirección' (wants to delete stored address)",
                "✅ YES: 'delete test@test.com' (wants to delete that email)",
                "✅ YES: 'lösche mein Passwort' (wants to delete stored password)",
                "❌ NO: 'delete files from desktop' (filesystem operation)",
                "❌ NO: 'how do I delete a record?' (tutorial question)"
            ]
        }

        operation_verbs = {
            'SAVE': 'STORE',
            'RETRIEVE': 'RETRIEVE',
            'DELETE': 'DELETE'
        }

        return f"""
🎯 CORE PRINCIPLE: Detect "{operation.lower()} intent"

Question: Does user want to {operation_verbs[operation]} data in/from the database?
{chr(10).join(examples[operation])}

CRITICAL: Works with ANY label (address, birthday, secret, license, wifi, etc.)
The examples below show PATTERNS, not a complete list of valid types!

YOUR JOB: If {operation.lower()} intent detected → Generate SQL
"""

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

        Note: Qwen 2.5 Coder is multilingual! Each action has specialized prompt.
              Language detection happens automatically - mixed inputs work too!
        """
        # Route to specialized prompt based on action
        if action_hint == 'SAVE':
            prompt = self._build_prompt_save(user_input)
        elif action_hint == 'RETRIEVE':
            prompt = self._build_prompt_retrieve(user_input)
        elif action_hint == 'DELETE':
            prompt = self._build_prompt_delete(user_input)
        else:
            # Fallback (shouldn't happen)
            prompt = self._build_prompt_save(user_input)

        # Call Qwen
        result_text = self._call_qwen(prompt)

        # Parse response
        return self._parse_qwen_output(result_text, user_input)

    def _build_prompt_save(self, user_input: str) -> str:
        """Focused SAVE prompt - KISS approach (v12.1.0)"""
        prompt = f"""Generate SQL INSERT for local database 'mydata'.

Schema: mydata(content TEXT, meta TEXT, lang TEXT)

Task: Extract VALUE and LABEL from user input, generate SQL.

Examples (VALUE can be at END of sentence!):

"save my email test@test.com"
→ INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('test@test.com', 'email', 'en');

"speichere den name meiner mutter irene"
→ INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('irene', 'name meiner mutter', 'de');

"guarda el nombre de mi madre maria"
→ INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('maria', 'nombre de mi madre', 'es');

"save my mothers name irene"
→ INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('irene', 'mothers name', 'en');

"note my boss's email boss@test.com"
→ INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('boss@test.com', 'boss\\'s email', 'en');

"don't forget my birthday is 01/01/1990"
→ INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('01/01/1990', 'birthday', 'en');

False positives (respond NO_ACTION):
- "how do I save?" (tutorial)
- "save money" (idiom)
- "save a file" (filesystem)

Analyze: "{user_input}"

Respond with SQL or NO_ACTION:
"""
        return prompt

    def _build_prompt_retrieve(self, user_input: str) -> str:
        """Focused RETRIEVE prompt - KISS approach (v12.1.0)"""
        prompt = f"""Generate SQL SELECT for local database 'mydata'.

Schema: mydata(id, content, meta, timestamp)

Task: Find stored data, return ALL matches (no LIMIT).

Examples:

"show all"
→ SELECT id, content, meta, timestamp FROM mydata ORDER BY timestamp DESC;

"show my email"
→ SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%email%' OR content LIKE '%email%' ORDER BY timestamp DESC;

"zeig meine Telefonnummer"
→ SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%Telefonnummer%' OR content LIKE '%Telefonnummer%' ORDER BY timestamp DESC;

"muestra el nombre de mi madre"
→ SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%nombre de mi madre%' OR content LIKE '%nombre de mi madre%' ORDER BY timestamp DESC;

False positives (respond NO_ACTION):
- "show me how to code" (tutorial)
- "find nearest restaurant" (external search)

Analyze: "{user_input}"

Respond with SQL or NO_ACTION:
"""
        return prompt

    def _build_prompt_delete(self, user_input: str) -> str:
        """Focused DELETE prompt - KISS approach (v12.1.0)"""
        prompt = f"""Generate SQL DELETE for local database 'mydata'.

Schema: mydata(content, meta)

Task: Delete by VALUE (exact) or LABEL (category).

Examples:

"delete test@test.com"
→ DELETE FROM mydata WHERE content = 'test@test.com';

"delete my email"
→ DELETE FROM mydata WHERE meta LIKE '%email%';

"borra mi contraseña"
→ DELETE FROM mydata WHERE meta LIKE '%contraseña%';

"lösche den name meiner mutter"
→ DELETE FROM mydata WHERE meta LIKE '%name meiner mutter%';

"delete all"
→ DELETE FROM mydata;

False positives (respond NO_ACTION):
- "how do I delete?" (tutorial)
- "delete all files" (filesystem)

Analyze: "{user_input}"

Respond with SQL or NO_ACTION:
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
        Parse Qwen's output to extract SQL or INCOMPLETE request (v12.0.0)

        Args:
            output: Qwen's raw output
            original_input: Original user input

        Returns:
            dict with sql, action, confidence, incomplete_msg (if INCOMPLETE)
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

    print("🧪 Testing Qwen 2.5 Coder SQL Generator (Intent-Based! v11.5.1)\n")

    # Test cases
    tests = [
        ("save my email test@test.com", "SAVE", "en"),
        ("guarda mi dirección Hiruela 3, 7-5", "SAVE", "es"),  # NEW: address test!
        ("guarda mi email mschenk.pda@gmail.com", "SAVE", "es"),  # Mixed ES+EN!
        ("speichere meine Email test@test.de", "SAVE", "de"),
        ("show my email", "RETRIEVE", "en"),
        ("muestra mi dirección", "RETRIEVE", "es"),  # NEW: address retrieval!
        ("zeig alle Daten", "RETRIEVE", "de"),
        ("delete my email", "DELETE", "en"),
        ("borra mi email test@test.com", "DELETE", "es"),
        ("borra mi email", "DELETE", "es"),  # Should delete ALL emails
        ("borra test@test.com", "DELETE", "es"),  # Should delete ONLY test@test.com
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
