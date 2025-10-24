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
        """Specialized prompt for SAVE - intent-based detection (v11.5.1)"""
        prompt = f"""You are a SQL INSERT specialist for SQLite database 'mydata'.

DATABASE SCHEMA:
CREATE TABLE mydata (
    id INTEGER PRIMARY KEY,
    content TEXT NOT NULL,      -- The actual VALUE (email address, phone, etc.)
    meta TEXT,                   -- The LABEL/description (email, phone, API key, etc.)
    lang TEXT,                   -- Language: en, de, es
    timestamp INTEGER            -- Auto-generated
);
{self._get_intent_principle('SAVE')}

YOUR JOB: Extract VALUE and LABEL from user input, then generate INSERT statement.

STEP 1 - ANALYZE INPUT:
Detect language from VERB:
- English verbs: save, note, record, add, log, write, register, put, set
- German verbs: speichere, merke, notiere, trag ein, schreib auf
- Spanish verbs: guarda, recuerda, anota, registra, apunta, graba

Extract TWO things from text after verb:
1. VALUE (content): The actual data - email address, phone number, password, API key, date, name, etc.
2. LABEL (meta): The type/description - can be single word OR multi-word like "API key", "wifi password"

STEP 2 - HANDLE FLEXIBLE STRUCTURE:
Text can have ANY of these structures:
- "save my email test@test.com" → VALUE: test@test.com, LABEL: email
- "save email test@test.com" → VALUE: test@test.com, LABEL: email
- "save the email test@test.com" → VALUE: test@test.com, LABEL: email
- "save test@test.com" → VALUE: test@test.com, LABEL: email (infer from format!)
- "add API key abc123" → VALUE: abc123, LABEL: API key (multi-word!)

Possessives (my/the/his/meine/die/mi/la) are OPTIONAL - ignore or use for LABEL extraction.

STEP 3 - GENERATE SQL:
Always use: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES (...);

EXAMPLES:

Input: "save my email test@test.com"
Analysis: Verb=save (EN), VALUE=test@test.com, LABEL=email
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('test@test.com', 'email', 'en');

Input: "speichere meine Email test@test.de"
Analysis: Verb=speichere (DE), VALUE=test@test.de, LABEL=Email
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('test@test.de', 'Email', 'de');

Input: "guarda mi email mschenk.pda@gmail.com"
Analysis: Verb=guarda (ES), VALUE=mschenk.pda@gmail.com, LABEL=email (mixed ES+EN!)
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('mschenk.pda@gmail.com', 'email', 'es');

Input: "note phone 669686832"
Analysis: Verb=note (EN), VALUE=669686832, LABEL=phone
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('669686832', 'phone', 'en');

Input: "add my API key sk-abc123xyz"
Analysis: Verb=add (EN), VALUE=sk-abc123xyz, LABEL=API key (multi-word!)
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('sk-abc123xyz', 'API key', 'en');

Input: "registra el teléfono de María 123456789"
Analysis: Verb=registra (ES), VALUE=123456789, LABEL=teléfono de María (context!)
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('123456789', 'teléfono de María', 'es');

Input: "save my address Hiruela 3, 7-5"
Analysis: Verb=save (EN), VALUE=Hiruela 3, 7-5, LABEL=address
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('Hiruela 3, 7-5', 'address', 'en');

Input: "guarda mi cumpleaños 15/03/1990"
Analysis: Verb=guarda (ES), VALUE=15/03/1990, LABEL=cumpleaños
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('15/03/1990', 'cumpleaños', 'es');

Input: "note my wifi password MyWifi123"
Analysis: Verb=note (EN), VALUE=MyWifi123, LABEL=wifi password (multi-word!)
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('MyWifi123', 'wifi password', 'en');

Input: "speichere den name meiner mutter irene"
Analysis: Verb=speichere (DE), VALUE=irene, LABEL=name meiner mutter (Genitiv!)
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('irene', 'name meiner mutter', 'de');

Input: "save my mothers name irene"
Analysis: Verb=save (EN), VALUE=irene, LABEL=mothers name (possessive!)
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('irene', 'mothers name', 'en');

Input: "guarda el nombre de mi madre maria"
Analysis: Verb=guarda (ES), VALUE=maria, LABEL=nombre de mi madre (de-Konstruktion!)
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('maria', 'nombre de mi madre', 'es');

Input: "remember my boss email boss@company.com"
Analysis: Verb=remember (EN), VALUE=boss@company.com, LABEL=boss email
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('boss@company.com', 'boss email', 'en');

Input: "store my license plate ABC-1234"
Analysis: Verb=store (EN), VALUE=ABC-1234, LABEL=license plate
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('ABC-1234', 'license plate', 'en');

Input: "keep my bank account DE89370400440532013000"
Analysis: Verb=keep (EN), VALUE=DE89370400440532013000, LABEL=bank account
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('DE89370400440532013000', 'bank account', 'en');

Input: "save the wifi password of my office SecureWiFi2024"
Analysis: Verb=save (EN), VALUE=SecureWiFi2024, LABEL=wifi password of my office
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('SecureWiFi2024', 'wifi password of my office', 'en');

Input: "add my fathers phone number 555-1234"
Analysis: Verb=add (EN), VALUE=555-1234, LABEL=fathers phone number
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('555-1234', 'fathers phone number', 'en');

Input: "note down my doctors name Dr. Smith"
Analysis: Verb=note (EN), VALUE=Dr. Smith, LABEL=doctors name
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('Dr. Smith', 'doctors name', 'en');

Input: "put my emergency contact john@email.com"
Analysis: Verb=put (EN), VALUE=john@email.com, LABEL=emergency contact
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('john@email.com', 'emergency contact', 'en');

Input: "record my passport number A12345678"
Analysis: Verb=record (EN), VALUE=A12345678, LABEL=passport number
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('A12345678', 'passport number', 'en');

Input: "merke dir die email meines chefs chef@firma.de"
Analysis: Verb=merke (DE), VALUE=chef@firma.de, LABEL=email meines chefs (Genitiv!)
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('chef@firma.de', 'email meines chefs', 'de');

Input: "speichere mein Kennzeichen M-AB-1234"
Analysis: Verb=speichere (DE), VALUE=M-AB-1234, LABEL=Kennzeichen
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('M-AB-1234', 'Kennzeichen', 'de');

Input: "notiere meine Kontonummer DE89370400440532013000"
Analysis: Verb=notiere (DE), VALUE=DE89370400440532013000, LABEL=Kontonummer
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('DE89370400440532013000', 'Kontonummer', 'de');

Input: "halt das WLAN-Passwort meines Büros fest SichererWiFi2024"
Analysis: Verb=halt fest (DE), VALUE=SichererWiFi2024, LABEL=WLAN-Passwort meines Büros (Genitiv!)
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('SichererWiFi2024', 'WLAN-Passwort meines Büros', 'de');

Input: "füg die Telefonnummer meines Vaters hinzu 0176-12345678"
Analysis: Verb=füg hinzu (DE), VALUE=0176-12345678, LABEL=Telefonnummer meines Vaters (Genitiv!)
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('0176-12345678', 'Telefonnummer meines Vaters', 'de');

Input: "schreib auf den Namen meines Arztes Dr. Müller"
Analysis: Verb=schreib auf (DE), VALUE=Dr. Müller, LABEL=Namen meines Arztes (Genitiv!)
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('Dr. Müller', 'Namen meines Arztes', 'de');

Input: "registriere meinen Notfallkontakt hans@email.de"
Analysis: Verb=registriere (DE), VALUE=hans@email.de, LABEL=Notfallkontakt
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('hans@email.de', 'Notfallkontakt', 'de');

Input: "leg meine Passnummer ab P12345678"
Analysis: Verb=leg ab (DE), VALUE=P12345678, LABEL=Passnummer
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('P12345678', 'Passnummer', 'de');

Input: "mi correo es test@ejemplo.com"
Analysis: Verb=implicit (ES), VALUE=test@ejemplo.com, LABEL=correo (NO verb - implicit save!)
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('test@ejemplo.com', 'correo', 'es');

Input: "mi teléfono es 669686832"
Analysis: Verb=implicit (ES), VALUE=669686832, LABEL=teléfono (NO verb - implicit save!)
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('669686832', 'teléfono', 'es');

Input: "mi cumpleaños es 15/03/1990"
Analysis: Verb=implicit (ES), VALUE=15/03/1990, LABEL=cumpleaños (NO verb - implicit save!)
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('15/03/1990', 'cumpleaños', 'es');

Input: "recuerda el correo de mi jefe jefe@empresa.es"
Analysis: Verb=recuerda (ES), VALUE=jefe@empresa.es, LABEL=correo de mi jefe (de-Konstruktion!)
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('jefe@empresa.es', 'correo de mi jefe', 'es');

Input: "guarda mi matrícula ABC-1234"
Analysis: Verb=guarda (ES), VALUE=ABC-1234, LABEL=matrícula
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('ABC-1234', 'matrícula', 'es');

Input: "anota mi cuenta bancaria ES9121000418450200051332"
Analysis: Verb=anota (ES), VALUE=ES9121000418450200051332, LABEL=cuenta bancaria
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('ES9121000418450200051332', 'cuenta bancaria', 'es');

Input: "almacena la contraseña del wifi de mi oficina WiFiSeguro2024"
Analysis: Verb=almacena (ES), VALUE=WiFiSeguro2024, LABEL=contraseña del wifi de mi oficina
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('WiFiSeguro2024', 'contraseña del wifi de mi oficina', 'es');

Input: "apunta el teléfono de mi padre 555-1234"
Analysis: Verb=apunta (ES), VALUE=555-1234, LABEL=teléfono de mi padre
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('555-1234', 'teléfono de mi padre', 'es');

Input: "registra el nombre de mi doctor Dr. García"
Analysis: Verb=registra (ES), VALUE=Dr. García, LABEL=nombre de mi doctor
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('Dr. García', 'nombre de mi doctor', 'es');

Input: "pon mi contacto de emergencia juan@email.com"
Analysis: Verb=pon (ES), VALUE=juan@email.com, LABEL=contacto de emergencia
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('juan@email.com', 'contacto de emergencia', 'es');

Input: "guarda mi celular 669686832"
Analysis: Verb=guarda (ES), VALUE=669686832, LABEL=celular (LATAM: celular vs móvil!)
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('669686832', 'celular', 'es');

Input: "anota el número de mi computadora C-12345"
Analysis: Verb=anota (ES), VALUE=C-12345, LABEL=número de mi computadora (LATAM: computadora vs ordenador!)
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('C-12345', 'número de mi computadora', 'es');

Input: "recuerda mi licencia de conducir L-98765"
Analysis: Verb=recuerda (ES), VALUE=L-98765, LABEL=licencia de conducir (LATAM!)
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('L-98765', 'licencia de conducir', 'es');

Input: "agrega la dirección de mi mamá Calle Real 15"
Analysis: Verb=agrega (ES), VALUE=Calle Real 15, LABEL=dirección de mi mamá (LATAM: mamá vs madre!)
SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('Calle Real 15', 'dirección de mi mamá', 'es');

FALSE POSITIVES (respond with NO_ACTION):

Input: "how do I save a file in Python?"
Reason: Tutorial question, no actual data to save
SQL: NO_ACTION

Input: "save money for vacation"
Reason: Idiom/phrase, no data type detected
SQL: NO_ACTION

Input: "remember to call mom"
Reason: Todo/reminder, no extractable VALUE
SQL: NO_ACTION

Now analyze this input:
"{user_input}"

Think step-by-step:
1. What is the VERB and language?
2. What is the VALUE (actual data)?
3. What is the LABEL (description)?
4. Is this a false positive?

Respond with ONLY the SQL statement or "NO_ACTION". No explanation needed.
"""
        return prompt

    def _build_prompt_retrieve(self, user_input: str) -> str:
        """Specialized prompt for RETRIEVE - intent-based, no LIMIT (v11.5.1)"""
        prompt = f"""You are a SQL SELECT specialist for SQLite database 'mydata'.

DATABASE SCHEMA:
CREATE TABLE mydata (
    id INTEGER PRIMARY KEY,
    content TEXT NOT NULL,      -- The actual data
    meta TEXT,                   -- The label/description
    lang TEXT,                   -- Language: en, de, es
    timestamp INTEGER            -- Unix timestamp
);
{self._get_intent_principle('RETRIEVE')}

YOUR JOB: Generate SELECT query to find data. Always return ALL matching records (no LIMIT).

STEP 1 - ANALYZE INPUT:
Detect language from VERB:
- English verbs: show, get, find, display, tell, check, lookup, retrieve, fetch, read, view, see, list
- German verbs: zeige, zeig, hole, finde, sag, schau, prüf, lies, gib aus, ruf ab, such, liste
- Spanish verbs: muestra, busca, encuentra, dame, dime, consulta, mira, ve, obtén, saca, lista

Extract SEARCH TERM from text after verb:
- Can be a LABEL: "email", "phone", "birthday", "address", etc.
- Can be a VALUE: "test@test.com", "669686832"
- Can be partial: "maria" should find "maria@test.com"
- Can be "all"/"todo"/"alle" for complete list

STEP 2 - DETERMINE QUERY TYPE:
Case A: "show all" / "list all" → SELECT ... ORDER BY timestamp DESC (no WHERE, no LIMIT)
Case B: Specific search term → SELECT ... WHERE ... ORDER BY timestamp DESC (no LIMIT)

STEP 3 - GENERATE SQL:
Format: SELECT id, content, meta, timestamp FROM mydata WHERE ... ORDER BY timestamp DESC;
Note: NEVER use LIMIT - always show ALL matching records!

EXAMPLES:

Input: "show all"
Analysis: Generic "show all" → Show entire database
SQL: SELECT id, content, meta, timestamp FROM mydata ORDER BY timestamp DESC;

Input: "list all"
Analysis: Generic "list all" → Show entire database
SQL: SELECT id, content, meta, timestamp FROM mydata ORDER BY timestamp DESC;

Input: "show my email"
Analysis: Search for "email" → Show all matching entries
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%email%' OR content LIKE '%email%' ORDER BY timestamp DESC;

Input: "show all emails"
Analysis: Search for "email" → Show all matching entries
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%email%' OR content LIKE '%email%' ORDER BY timestamp DESC;

Input: "muestra todo"
Analysis: Generic "muestra todo" (ES) → Show entire database
SQL: SELECT id, content, meta, timestamp FROM mydata ORDER BY timestamp DESC;

Input: "muestra mi dirección"
Analysis: Search for "dirección" (ES) → Show all matching entries
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%dirección%' OR content LIKE '%dirección%' ORDER BY timestamp DESC;

Input: "muestra mi cumpleaños"
Analysis: Search for "cumpleaños" (ES) → Show all matching entries
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%cumpleaños%' OR content LIKE '%cumpleaños%' ORDER BY timestamp DESC;

Input: "zeig alles"
Analysis: Generic "zeig alles" (DE) → Show entire database
SQL: SELECT id, content, meta, timestamp FROM mydata ORDER BY timestamp DESC;

Input: "zeig meine Telefonnummer"
Analysis: Search for "Telefonnummer" (DE) → Show all matching entries
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%Telefonnummer%' OR content LIKE '%Telefonnummer%' ORDER BY timestamp DESC;

Input: "find maria"
Analysis: Search for "maria" → Show all matching entries
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%maria%' OR content LIKE '%maria%' ORDER BY timestamp DESC;

Input: "show my boss email"
Analysis: Search for "boss email" → Show all matching entries
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%boss email%' OR content LIKE '%boss email%' ORDER BY timestamp DESC;

Input: "find my license plate"
Analysis: Search for "license plate" → Show all matching entries
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%license plate%' OR content LIKE '%license plate%' ORDER BY timestamp DESC;

Input: "what is my fathers phone"
Analysis: Search for "fathers phone" → Show all matching entries
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%fathers phone%' OR content LIKE '%fathers phone%' ORDER BY timestamp DESC;

Input: "get my wifi password"
Analysis: Search for "wifi password" → Show all matching entries
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%wifi password%' OR content LIKE '%wifi password%' ORDER BY timestamp DESC;

Input: "list everything"
Analysis: Generic "list everything" → Show entire database
SQL: SELECT id, content, meta, timestamp FROM mydata ORDER BY timestamp DESC;

Input: "zeig die Email meines Chefs"
Analysis: Search for "Email meines Chefs" (DE) → Show all matching entries
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%Email meines Chefs%' OR content LIKE '%Email meines Chefs%' ORDER BY timestamp DESC;

Input: "finde mein Kennzeichen"
Analysis: Search for "Kennzeichen" (DE) → Show all matching entries
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%Kennzeichen%' OR content LIKE '%Kennzeichen%' ORDER BY timestamp DESC;

Input: "was ist die Telefonnummer meines Vaters"
Analysis: Search for "Telefonnummer meines Vaters" (DE) → Show all matching entries
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%Telefonnummer meines Vaters%' OR content LIKE '%Telefonnummer meines Vaters%' ORDER BY timestamp DESC;

Input: "hole das WLAN-Passwort"
Analysis: Search for "WLAN-Passwort" (DE) → Show all matching entries
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%WLAN-Passwort%' OR content LIKE '%WLAN-Passwort%' ORDER BY timestamp DESC;

Input: "liste alle Daten"
Analysis: Generic "liste alle Daten" (DE) → Show entire database
SQL: SELECT id, content, meta, timestamp FROM mydata ORDER BY timestamp DESC;

Input: "lista todo"
Analysis: Generic "lista todo" (ES) → Show entire database
SQL: SELECT id, content, meta, timestamp FROM mydata ORDER BY timestamp DESC;

Input: "cuál es mi correo"
Analysis: Search for "correo" (ES - implicit question!) → Show all matching entries
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%correo%' OR content LIKE '%correo%' ORDER BY timestamp DESC;

Input: "mi teléfono"
Analysis: Search for "teléfono" (ES - just label, implicit retrieve!) → Show all matching entries
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%teléfono%' OR content LIKE '%teléfono%' ORDER BY timestamp DESC;

Input: "muestra el correo de mi jefe"
Analysis: Search for "correo de mi jefe" (ES) → Show all matching entries
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%correo de mi jefe%' OR content LIKE '%correo de mi jefe%' ORDER BY timestamp DESC;

Input: "encuentra mi matrícula"
Analysis: Search for "matrícula" (ES) → Show all matching entries
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%matrícula%' OR content LIKE '%matrícula%' ORDER BY timestamp DESC;

Input: "busca la contraseña del wifi"
Analysis: Search for "contraseña del wifi" (ES) → Show all matching entries
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%contraseña del wifi%' OR content LIKE '%contraseña del wifi%' ORDER BY timestamp DESC;

Input: "dame el teléfono de mi padre"
Analysis: Search for "teléfono de mi padre" (ES) → Show all matching entries
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%teléfono de mi padre%' OR content LIKE '%teléfono de mi padre%' ORDER BY timestamp DESC;

Input: "muestra mi celular"
Analysis: Search for "celular" (ES - LATAM!) → Show all matching entries
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%celular%' OR content LIKE '%celular%' ORDER BY timestamp DESC;

Input: "dime mi número de computadora"
Analysis: Search for "número de computadora" (ES - LATAM!) → Show all matching entries
SQL: SELECT id, content, meta, timestamp FROM mydata WHERE meta LIKE '%número de computadora%' OR content LIKE '%número de computadora%' ORDER BY timestamp DESC;

FALSE POSITIVES (respond with NO_ACTION):

Input: "show me how to code in Python"
Reason: Tutorial request, not database search
SQL: NO_ACTION

Input: "call my mom"
Reason: Idiom/reminder (even though contains "call" - not a search verb!)
SQL: NO_ACTION

Input: "display system settings"
Reason: UI/system command, not database query
SQL: NO_ACTION

Input: "find the nearest restaurant"
Reason: Location search, not database query
SQL: NO_ACTION

Input: "remember to check email later"
Reason: Reminder/todo, not retrieval query
SQL: NO_ACTION

Now analyze this input:
"{user_input}"

Think step-by-step:
1. What is the VERB and language?
2. What is the SEARCH TERM?
3. Is this "show all" (no WHERE) or specific search (with WHERE)?
4. Is this a false positive?

Respond with ONLY the SQL statement or "NO_ACTION". No explanation needed.
"""
        return prompt

    def _build_prompt_delete(self, user_input: str) -> str:
        """SMART DELETE Prompt - intent-based, VALUE vs LABEL (v11.5.1)"""
        prompt = f"""You are a SMART SQL DELETE specialist for SQLite database 'mydata'.

DATABASE SCHEMA:
CREATE TABLE mydata (
    id INTEGER PRIMARY KEY,
    content TEXT NOT NULL,      -- The actual data (email, phone, etc.)
    meta TEXT,                   -- The label/description
    lang TEXT,
    timestamp INTEGER
);
{self._get_intent_principle('DELETE')}

YOUR JOB: Detect if user wants to delete by VALUE (specific data) or LABEL (category), then generate precise DELETE.

⚠️ CRITICAL RULE: NEVER use OR in WHERE clause! Choose ONE field: either content or meta!

STEP 1 - ANALYZE INPUT:
Detect language from VERB:
- English: delete, remove, forget, clear, erase, drop, wipe, purge
- German: lösche, entferne, vergiss, tilg, raum auf, wirf weg, streich
- Spanish: borra, elimina, olvida, quita, suprime, limpia, remueve

Extract text after verb and DETECT TYPE:

TYPE A - VALUE (specific data): Email format (@+domain), phone (digits 6+), date (/or-), API key (hyphens/long)
TYPE B - LABEL (category): Generic words without specific format (email, phone, birthday, name, etc.)

STEP 2 - DELETE STRATEGY:
Strategy A (VALUE): DELETE FROM mydata WHERE content = '<exact_value>';  ← Use = for precision!
Strategy B (LABEL): DELETE FROM mydata WHERE meta LIKE '%<label>%';     ← Use LIKE for variations
Strategy C (BOTH mentioned): Prefer VALUE (more specific!)

Special: "delete all"/"borra todo"/"lösche alle" → DELETE FROM mydata;

EXAMPLES (VALUE - Delete specific data):

Input: "borra test@test.com"
SQL: DELETE FROM mydata WHERE content = 'test@test.com';

Input: "delete 669686832"
SQL: DELETE FROM mydata WHERE content = '669686832';

Input: "elimina maria@test.com"
SQL: DELETE FROM mydata WHERE content = 'maria@test.com';

Input: "lösche sk-abc123xyz"
SQL: DELETE FROM mydata WHERE content = 'sk-abc123xyz';

Input: "borra el email test@test.com"
Note: BOTH mentioned but VALUE is specific → prefer VALUE!
SQL: DELETE FROM mydata WHERE content = 'test@test.com';

Input: "borra mi email test@test.com"
Note: BOTH mentioned but VALUE is specific → prefer VALUE!
SQL: DELETE FROM mydata WHERE content = 'test@test.com';

EXAMPLES (LABEL - Delete all of type):

Input: "borra mi email"
SQL: DELETE FROM mydata WHERE meta LIKE '%email%';

Input: "delete my phone"
SQL: DELETE FROM mydata WHERE meta LIKE '%phone%';

Input: "elimina el teléfono"
SQL: DELETE FROM mydata WHERE meta LIKE '%teléfono%';

Input: "lösche alle Emails"
SQL: DELETE FROM mydata WHERE meta LIKE '%Email%';

Input: "delete my address"
SQL: DELETE FROM mydata WHERE meta LIKE '%address%';

Input: "borra mi cumpleaños"
SQL: DELETE FROM mydata WHERE meta LIKE '%cumpleaños%';

Input: "delete my boss email"
SQL: DELETE FROM mydata WHERE meta LIKE '%boss email%';

Input: "forget my license plate"
SQL: DELETE FROM mydata WHERE meta LIKE '%license plate%';

Input: "remove boss@company.com"
SQL: DELETE FROM mydata WHERE content = 'boss@company.com';

Input: "erase my fathers phone"
SQL: DELETE FROM mydata WHERE meta LIKE '%fathers phone%';

Input: "lösche die Email meines Chefs"
SQL: DELETE FROM mydata WHERE meta LIKE '%email meines chefs%';

Input: "vergiss mein Kennzeichen"
SQL: DELETE FROM mydata WHERE meta LIKE '%Kennzeichen%';

Input: "entferne chef@firma.de"
SQL: DELETE FROM mydata WHERE content = 'chef@firma.de';

Input: "lösch die Telefonnummer meines Vaters"
SQL: DELETE FROM mydata WHERE meta LIKE '%Telefonnummer meines Vaters%';

Input: "borra el correo de mi jefe"
SQL: DELETE FROM mydata WHERE meta LIKE '%correo de mi jefe%';

Input: "elimina mi matrícula"
SQL: DELETE FROM mydata WHERE meta LIKE '%matrícula%';

Input: "olvida jefe@empresa.es"
SQL: DELETE FROM mydata WHERE content = 'jefe@empresa.es';

Input: "quita el teléfono de mi padre"
SQL: DELETE FROM mydata WHERE meta LIKE '%teléfono de mi padre%';

Input: "elimina mi celular"
SQL: DELETE FROM mydata WHERE meta LIKE '%celular%';

Input: "ya no necesito mi correo"
SQL: DELETE FROM mydata WHERE meta LIKE '%correo%';

Input: "limpia mis datos"
SQL: DELETE FROM mydata;

EXAMPLES (Special - Delete all):

Input: "borra todo"
SQL: DELETE FROM mydata;

Input: "delete all"
SQL: DELETE FROM mydata;

Input: "lösche alle Daten"
SQL: DELETE FROM mydata;

FALSE POSITIVES:

Input: "delete all files from desktop"
SQL: NO_ACTION

Input: "how do I delete a record?"
SQL: NO_ACTION

Input: "remove the background"
SQL: NO_ACTION

Now analyze this input:
"{user_input}"

Think step-by-step:
1. What is the VERB and language?
2. Is there a VALUE (specific format) or LABEL (generic category)?
3. If BOTH: which is more specific?
4. Is this a false positive?
5. What SQL to generate?

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
