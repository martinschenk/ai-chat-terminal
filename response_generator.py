#!/usr/bin/env python3
"""
AI Chat Terminal - Response Generator
Generates natural responses using Phi-3 or template fallback
"""

import os
import re
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any

class ResponseGenerator:
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = Path.home() / '.aichat'

        self.config_dir = Path(config_dir)
        self.phi3_available = self._check_phi3()

        # Load configuration
        self.config = self._load_config()
        self.language = self.config.get('AI_CHAT_LANGUAGE', 'en')

        # Response templates for different languages and data types
        self.templates = self._get_templates()

    def _load_config(self) -> Dict[str, str]:
        """Load configuration from config file"""
        config = {}
        config_file = self.config_dir / 'config'

        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            config[key] = value.strip().strip('"\'')
            except Exception as e:
                print(f"Warning: Could not load config: {e}", file=sys.stderr)

        return config

    def _check_phi3(self) -> bool:
        """Check if Ollama with Phi-3 is available"""
        try:
            # Check if ollama command exists
            result = subprocess.run(
                ['which', 'ollama'],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode != 0:
                return False

            # Check if phi3 model is available
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )

            return 'phi3' in result.stdout.lower()

        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return False

    def _get_templates(self) -> Dict[str, Dict[str, str]]:
        """Get response templates - ONLY for fallback when Phi-3 unavailable"""
        return {
            'de': {
                # Single generic template - Phi-3 handles variations
                'generic_sensitive': "✅ Gespeichert 🔒",
                'not_found': "❌ Ich habe keine Informationen zu '{query}' in der lokalen Datenbank gefunden.",
                'found_credit_card': "💳 Deine Kreditkarte: {value}",
                'found_api_key': "🔑 Dein {service} API-Key: `{value}`",
                'found_password': "🔒 Dein Passwort für {service}: `{value}`",
                'found_email': "📧 Deine E-Mail: {value}",
                'found_phone': "📱 Deine Telefonnummer: {value}",
                'found_generic': "ℹ️ Gefunden: {value}",
                'deleted': "🗑️ {count} Einträge wurden aus der lokalen Datenbank gelöscht.",
                'delete_not_found': "❌ Keine passenden Einträge zum Löschen gefunden."
            },
            'en': {
                # Single generic template - Phi-3 handles variations
                'generic_sensitive': "✅ Stored 🔒",
                'not_found': "❌ I don't have any information about '{query}' in the local database.",
                'found_credit_card': "💳 Your credit card: {value}",
                'found_api_key': "🔑 Your {service} API key: `{value}`",
                'found_password': "🔒 Your password for {service}: `{value}`",
                'found_email': "📧 Your email: {value}",
                'found_phone': "📱 Your phone number: {value}",
                'found_generic': "ℹ️ Found: {value}",
                'deleted': "🗑️ {count} entries have been deleted from the local database.",
                'delete_not_found': "❌ No matching entries found to delete."
            },
            'es': {
                # Single generic template - Phi-3 handles variations
                'generic_sensitive': "✅ Guardado 🔒",
                'not_found': "❌ No tengo información sobre '{query}' en la base de datos local.",
                'found_credit_card': "💳 Tu tarjeta de crédito: {value}",
                'found_api_key': "🔑 Tu clave API de {service}: `{value}`",
                'found_password': "🔒 Tu contraseña para {service}: `{value}`",
                'found_email': "📧 Tu correo: {value}",
                'found_phone': "📱 Tu teléfono: {value}",
                'found_generic': "ℹ️ Encontrado: {value}",
                'deleted': "🗑️ {count} entradas han sido eliminadas de la base de datos local.",
                'delete_not_found': "❌ No se encontraron entradas coincidentes para eliminar."
            }
        }

    def format_stored_data(self, user_message: str, language: str = None) -> str:
        """
        Format confirmation for data stored locally (v8.0.0 keyword system)
        User explicitly said "speichere lokal" or similar

        Args:
            user_message: The original user message that was stored
            language: Language code (de, en, es, etc.)

        Returns:
            Natural confirmation message
        """
        if language is None:
            language = self.language

        # Map to base language if dialect
        base_lang = language.split('-')[0] if '-' in language else language
        if base_lang not in self.templates:
            base_lang = 'en'

        templates = self.templates[base_lang]

        # Prefer Phi-3 for dynamic, natural responses
        if self.phi3_available and self.config.get('PHI3_ENABLED', 'false').lower() == 'true':
            try:
                return self._generate_with_phi3_stored(user_message, language)
            except Exception as e:
                print(f"Phi-3 generation failed: {e}", file=sys.stderr)
                # Fall through to simple fallback

        # Simple fallback when Phi-3 unavailable
        return templates['generic_sensitive']

    def confirm_storage(self, pii_types: List[str], language: str = None) -> str:
        """
        Generate confirmation message for stored PII
        DEPRECATED in v8.0.0 - use format_stored_data() instead
        """
        if language is None:
            language = self.language

        # Map to base language if dialect
        base_lang = language.split('-')[0] if '-' in language else language
        if base_lang not in self.templates:
            base_lang = 'en'

        templates = self.templates[base_lang]

        # Prefer Phi-3 for dynamic, varied responses
        if self.phi3_available and self.config.get('PHI3_ENABLED', 'false').lower() == 'true':
            try:
                return self._generate_with_phi3_storage(pii_types, language)
            except Exception as e:
                print(f"Phi-3 generation failed: {e}", file=sys.stderr)
                # Fall through to simple fallback

        # Simple fallback when Phi-3 unavailable
        # No hardcoded cases - one template for all
        return templates['generic_sensitive']

    def format_retrieved_data(self, user_query: str, db_results: List[Dict], language: str = None) -> str:
        """
        Format retrieved data from local database (v8.0.0 keyword system)
        User explicitly said "aus meiner db" or similar

        Args:
            user_query: The user's query
            db_results: List of matching results from DB
            language: Language code (de, en, es, etc.)

        Returns:
            Natural response with the data
        """
        if language is None:
            language = self.language

        # Map to base language if dialect
        base_lang = language.split('-')[0] if '-' in language else language
        if base_lang not in self.templates:
            base_lang = 'en'

        templates = self.templates[base_lang]

        # Handle no results
        if not db_results:
            return templates['not_found'].format(query=user_query)

        # Prefer Phi-3 for natural responses
        if self.phi3_available and self.config.get('PHI3_ENABLED', 'false').lower() == 'true':
            try:
                return self._generate_with_phi3_retrieved(user_query, db_results, language)
            except Exception as e:
                print(f"Phi-3 generation failed: {e}", file=sys.stderr)
                # Fall through to template

        # Simple template fallback - just show the data
        result = db_results[0]  # Best match
        content = result.get('content', '')
        return templates['found_generic'].format(value=content)

    def generate_response(self, query: str, db_results: List[Dict], intent: str = 'QUERY', language: str = None) -> str:
        """
        Generate response based on database results
        DEPRECATED in v8.0.0 - use format_retrieved_data() instead
        """
        if language is None:
            language = self.language

        # Map to base language if dialect
        base_lang = language.split('-')[0] if '-' in language else language
        if base_lang not in self.templates:
            base_lang = 'en'

        templates = self.templates[base_lang]

        # Handle delete intent
        if intent == 'DELETE':
            count = len(db_results)
            if count > 0:
                return templates['deleted'].format(count=count)
            else:
                return templates['delete_not_found']

        # Handle query intent
        if not db_results:
            return templates['not_found'].format(query=query)

        # Use Phi-3 if available for more natural responses
        if self.phi3_available and self.config.get('PHI3_ENABLED', 'false').lower() == 'true':
            try:
                return self._generate_with_phi3_query(query, db_results, language)
            except Exception as e:
                print(f"Phi-3 generation failed: {e}", file=sys.stderr)
                # Fall through to template

        # Template-based response for query results
        result = db_results[0]  # Take best match
        content = result.get('content', '')
        data_type = result.get('data_type', '').lower()

        # Determine appropriate template
        if 'api' in data_type or 'key' in data_type:
            service = self._extract_service_name(content)
            return templates['found_api_key'].format(service=service, value=content)
        elif 'credit' in data_type or 'card' in data_type:
            return templates['found_credit_card'].format(value=content)
        elif 'password' in data_type:
            service = self._extract_service_name(query)
            return templates['found_password'].format(service=service, value=content)
        elif 'email' in data_type:
            return templates['found_email'].format(value=content)
        elif 'phone' in data_type:
            return templates['found_phone'].format(value=content)
        else:
            return templates['found_generic'].format(value=content)

    def _generate_with_phi3_stored(self, user_message: str, language: str) -> str:
        """
        Generate storage confirmation using Phi-3 (v8.0.0)
        User explicitly said "speichere lokal" or similar
        """
        lang_instruction = self._get_language_instruction(language)

        # Extract key info from message (remove "speichere lokal" keywords)
        clean_message = user_message
        for keyword in ['speichere lokal', 'save locally', 'guarda localmente', 'speicher lokal', 'store locally']:
            clean_message = clean_message.replace(keyword, '').strip(':, ')

        prompt = f"""{lang_instruction} Confirm data stored in 2-3 words + ONE emoji.

EXAMPLES:
💾 Hab's!
🔒 Gesichert!
✨ Notiert!

Your 2-3 word response:"""

        return self._call_phi3(prompt)

    def _generate_with_phi3_retrieved(self, user_query: str, db_results: List[Dict], language: str) -> str:
        """
        Generate retrieval response using Phi-3 (v8.0.0)
        User explicitly said "aus meiner db" or similar

        CRITICAL: MUST include 🔍 icon to show data comes from DB!
        """
        lang_instruction = self._get_language_instruction(language)

        result = db_results[0]
        content = result.get('content', '')

        # Generate playful phrase with Phi-3
        prompt = f"""{lang_instruction} Create a SHORT (2-4 words) playful phrase for retrieving data from database.

EXAMPLES (German):
- Aus DB geholt
- Gefunden
- Hier ist's
- DB sagt

EXAMPLES (English):
- Found in DB
- Got it
- Here you go

Your SHORT phrase (2-4 words max):"""

        try:
            phrase = self._call_phi3(prompt).strip(':!.,')
        except:
            # Fallback phrases
            phrases_de = ["Aus DB geholt", "Gefunden", "Hier ist's"]
            phrases_en = ["Found in DB", "Got it", "Here you go"]
            import random
            phrase = random.choice(phrases_de if 'deutsch' in lang_instruction.lower() else phrases_en)

        # ALWAYS add icon prefix (NON-NEGOTIABLE!)
        return f"🔍 {phrase}: {content}"

    def _generate_with_phi3_deleted(self, target: str, count: int, language: str) -> str:
        """Generate deletion confirmation using Phi-3 (v9.0.0)"""
        lang_instruction = self._get_language_instruction(language)

        prompt = f"""TASK: Confirm {count} entries deleted. {lang_instruction}

User deleted: "{target[:50]}"
Count: {count} entries

RULES:
1. 2-5 words max (short & punchy!)
2. Include 1-2 emojis (🗑️/✨/💨/🔥/👋)
3. Be PLAYFUL & VARIED - NOT robotic!
4. Change phrasing EVERY time
5. Varied verbs: gelöscht/entfernt/weggeräumt/verschwunden/weg/erledigt

PLAYFUL EXAMPLES:
🗑️ Weg damit! ({count}x)
✨ Erledigt - {count} weg
💨 Verschwunden! {count}x
🔥 {count} gelöscht
👋 Alles weg ({count})
🎯 {count}x entfernt!

Your creative response:"""

        return self._call_phi3(prompt)

    def format_deleted_data(self, target: str, count: int, language: str = None) -> str:
        """Format deletion confirmation (v9.0.0)"""
        if language is None:
            language = self.language

        base_lang = language.split('-')[0] if '-' in language else language
        if base_lang not in self.templates:
            base_lang = 'en'

        templates = self.templates[base_lang]

        if self.phi3_available and self.config.get('PHI3_ENABLED', 'false').lower() == 'true':
            try:
                return self._generate_with_phi3_deleted(target, count, language)
            except Exception as e:
                print(f"Phi-3 generation failed: {e}", file=sys.stderr)

        return templates['deleted'].format(count=count)

    def format_list_header(self, count: int, language: str = None) -> str:
        """Format LIST header (v9.0.0)"""
        if language is None:
            language = self.language

        base_lang = language.split('-')[0] if '-' in language else language
        if base_lang not in self.templates:
            base_lang = 'en'

        if self.phi3_available and self.config.get('PHI3_ENABLED', 'false').lower() == 'true':
            try:
                return self._generate_with_phi3_list_header(count, language)
            except Exception as e:
                print(f"Phi-3 generation failed: {e}", file=sys.stderr)

        if base_lang == 'de':
            return f"📦 Deine lokal gespeicherten Daten ({count}):"
        elif base_lang == 'es':
            return f"📦 Tus datos guardados ({count}):"
        else:
            return f"📦 Your locally stored data ({count}):"

    def _generate_with_phi3_list_header(self, count: int, language: str) -> str:
        """Generate LIST header using Phi-3 (v9.0.0)"""
        lang_instruction = self._get_language_instruction(language)

        prompt = f"""{lang_instruction} Create ONE short header for {count} stored items.

STRICT FORMAT: [EMOJI] [2-4 words]:

EXAMPLES:
📦 Deine Daten ({count}):
🗄️ Lokal gespeichert:
💾 {count} Einträge:

OUTPUT (ONE line only):"""

        return self._call_phi3(prompt)

    def _generate_with_phi3_storage(self, pii_types: List[str], language: str) -> str:
        """
        Generate storage confirmation using Phi-3 - DYNAMIC & COOL
        DEPRECATED in v8.0.0 - use _generate_with_phi3_stored() instead
        """
        lang_instruction = self._get_language_instruction(language)

        prompt = f"""TASK: Confirm data stored. {lang_instruction}

Data: {', '.join(pii_types)}

RULES (STRICT):
1. Maximum 4 words total (including emoji)
2. Must include exactly 1 emoji
3. Be cool and modern
4. Vary your response

VALID EXAMPLES:
✅ Safe! 🔒
💾 Got it!
🔐 Secured locally
✨ Locked down!
🎯 Stored securely

INVALID (TOO LONG):
✅ Safe & encrypted 🔐 Data stored
🛡️ Local backup complete now

Your response (4 words max):"""

        return self._call_phi3(prompt)

    def _generate_with_phi3_query(self, query: str, db_results: List[Dict], language: str) -> str:
        """
        Generate query response using Phi-3

        CRITICAL: MUST include 🔍 icon to show data comes from DB!
        """
        lang_instruction = self._get_language_instruction(language)

        result = db_results[0]
        content = result.get('content', '')

        # Generate playful phrase with Phi-3
        prompt = f"""{lang_instruction} Create a SHORT (2-4 words) playful phrase for retrieving data from database.

EXAMPLES (German):
- Aus DB geholt
- Gefunden
- Hier ist's
- DB sagt

EXAMPLES (English):
- Found in DB
- Got it
- Here you go

Your SHORT phrase (2-4 words max):"""

        try:
            phrase = self._call_phi3(prompt).strip(':!.,')
        except:
            # Fallback phrases
            phrases_de = ["Aus DB geholt", "Gefunden", "Hier ist's"]
            phrases_en = ["Found in DB", "Got it", "Here you go"]
            import random
            phrase = random.choice(phrases_de if 'deutsch' in lang_instruction.lower() else phrases_en)

        # ALWAYS add icon prefix (NON-NEGOTIABLE!)
        return f"🔍 {phrase}: {content}"

    def _call_phi3(self, prompt: str) -> str:
        """Call Phi-3 model via Ollama"""
        try:
            result = subprocess.run(
                ['ollama', 'run', 'phi3'],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout (first run needs model loading)
            )

            if result.returncode == 0 and result.stdout.strip():
                response = result.stdout.strip()
                # Clean up response
                response = re.sub(r'^(Response:|Assistant:|AI:)\s*', '', response, flags=re.IGNORECASE)
                return response

            raise Exception(f"Phi-3 returned error: {result.stderr}")

        except Exception as e:
            raise Exception(f"Failed to call Phi-3: {e}")

    def _get_language_instruction(self, language: str) -> str:
        """Get language instruction for Phi-3"""
        base_lang = language.split('-')[0] if '-' in language else language

        instructions = {
            'de': "Antworte auf Deutsch.",
            'en': "Respond in English.",
            'es': "Responde en español.",
            'fr': "Répondez en français.",
            'it': "Rispondi in italiano.",
        }

        return instructions.get(base_lang, "Respond in English.")

    def _extract_service_name(self, text: str) -> str:
        """Extract service name from text for better templating"""
        text_lower = text.lower()

        services = {
            'openai': 'OpenAI',
            'aws': 'AWS',
            'github': 'GitHub',
            'google': 'Google',
            'slack': 'Slack',
            'stripe': 'Stripe',
            'telegram': 'Telegram'
        }

        for key, name in services.items():
            if key in text_lower:
                return name

        return "den Service"  # Default for German, could be made language-aware

    def get_generator_info(self) -> Dict[str, Any]:
        """Get information about available generation methods"""
        return {
            'phi3_available': self.phi3_available,
            'phi3_enabled': self.config.get('PHI3_ENABLED', 'false').lower() == 'true',
            'language': self.language,
            'supported_languages': list(self.templates.keys()),
            'generation_mode': 'phi3' if (self.phi3_available and self.config.get('PHI3_ENABLED', 'false').lower() == 'true') else 'template'
        }

def main():
    """Test the response generator"""
    generator = ResponseGenerator()

    print("🤖 Response Generator Test Suite")
    print("=" * 50)

    # Display generator info
    info = generator.get_generator_info()
    print(f"Phi-3 available: {info['phi3_available']}")
    print(f"Phi-3 enabled: {info['phi3_enabled']}")
    print(f"Generation mode: {info['generation_mode']}")
    print(f"Language: {info['language']}")
    print()

    # Test storage confirmations
    print("📝 Testing storage confirmations:")
    test_pii_types = [
        ['OPENAI_API_KEY'],
        ['CREDIT_CARD'],
        ['PASSWORD'],
        ['EMAIL', 'PHONE']
    ]

    for pii_types in test_pii_types:
        response = generator.confirm_storage(pii_types)
        print(f"PII types: {pii_types}")
        print(f"Response: {response}")
        print()

    # Test query responses
    print("🔍 Testing query responses:")
    test_queries = [
        ("What's my API key?", [{'content': 'sk-proj-abc123...', 'data_type': 'API_KEY'}]),
        ("Wie ist meine Kreditkarte?", [{'content': '4532-1234-5678-9012', 'data_type': 'CREDIT_CARD'}]),
        ("No data found", [])
    ]

    for query, results in test_queries:
        response = generator.generate_response(query, results)
        print(f"Query: {query}")
        print(f"Response: {response}")
        print()

if __name__ == "__main__":
    main()