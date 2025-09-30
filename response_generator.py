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
        """Get response templates for different languages and data types"""
        return {
            'de': {
                'api_key': "🔑 Dein {service} API-Key wurde sicher gespeichert:\n`{value}`\n\n💡 Denk daran, ihn vertraulich zu behandeln!",
                'openai_api_key': "🤖 Dein OpenAI API-Key wurde lokal gespeichert:\n`{value}`\n\n✅ Er wird niemals an externe Server übertragen!",
                'credit_card': "💳 Deine {type} Kreditkarte endet auf **{last4}** wurde sicher gespeichert.",
                'email': "📧 Deine E-Mail-Adresse wurde notiert: {value}",
                'phone': "📱 Deine Telefonnummer wurde gespeichert: {value}",
                'password': "🔒 Dein Passwort für {service} wurde sicher lokal gespeichert:\n`{value}`\n\n💡 Tipp: Nutze einen Passwort-Manager für maximale Sicherheit!",
                'generic_sensitive': "🛡️ Deine sensiblen Daten wurden sicher lokal gespeichert und werden niemals an OpenAI übertragen.",
                'proprietary': "🏢 Die Unternehmensdaten wurden lokal gespeichert und bleiben vertraulich.",
                'personal': "👤 Die persönlichen Informationen wurden notiert.",
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
                'api_key': "🔑 Your {service} API key has been securely stored:\n`{value}`\n\n💡 Keep it confidential!",
                'openai_api_key': "🤖 Your OpenAI API key has been stored locally:\n`{value}`\n\n✅ It will never be transmitted to external servers!",
                'credit_card': "💳 Your {type} credit card ending in **{last4}** has been securely stored.",
                'email': "📧 Your email address has been noted: {value}",
                'phone': "📱 Your phone number has been stored: {value}",
                'password': "🔒 Your password for {service} has been securely stored locally:\n`{value}`\n\n💡 Tip: Use a password manager for maximum security!",
                'generic_sensitive': "🛡️ Your sensitive data has been securely stored locally and will never be sent to OpenAI.",
                'proprietary': "🏢 The business data has been stored locally and remains confidential.",
                'personal': "👤 The personal information has been noted.",
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
                'api_key': "🔑 Tu clave API de {service} ha sido guardada de forma segura:\n`{value}`\n\n💡 ¡Manténla confidencial!",
                'openai_api_key': "🤖 Tu clave API de OpenAI ha sido almacenada localmente:\n`{value}`\n\n✅ ¡Nunca será transmitida a servidores externos!",
                'credit_card': "💳 Tu tarjeta de crédito {type} terminada en **{last4}** ha sido guardada de forma segura.",
                'email': "📧 Tu dirección de correo ha sido anotada: {value}",
                'phone': "📱 Tu número de teléfono ha sido guardado: {value}",
                'password': "🔒 Tu contraseña para {service} ha sido guardada localmente:\n`{value}`\n\n💡 Consejo: ¡Usa un gestor de contraseñas para máxima seguridad!",
                'generic_sensitive': "🛡️ Tus datos sensibles han sido almacenados localmente y nunca serán enviados a OpenAI.",
                'proprietary': "🏢 Los datos empresariales han sido almacenados localmente y permanecen confidenciales.",
                'personal': "👤 La información personal ha sido anotada.",
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

    def confirm_storage(self, pii_types: List[str], language: str = None) -> str:
        """Generate confirmation message for stored PII"""
        if language is None:
            language = self.language

        # Map to base language if dialect
        base_lang = language.split('-')[0] if '-' in language else language
        if base_lang not in self.templates:
            base_lang = 'en'

        templates = self.templates[base_lang]

        # If Phi-3 is available, use it for more natural responses
        if self.phi3_available and self.config.get('PHI3_ENABLED', 'false').lower() == 'true':
            try:
                return self._generate_with_phi3_storage(pii_types, language)
            except Exception as e:
                print(f"Phi-3 generation failed: {e}", file=sys.stderr)
                # Fall through to template

        # Template-based response
        if len(pii_types) == 1:
            pii_type = pii_types[0].lower()

            # Map specific types to templates
            if 'openai' in pii_type.lower() or 'api_key' in pii_type.lower():
                return templates['generic_sensitive']
            elif 'credit' in pii_type.lower() or 'card' in pii_type.lower():
                return templates['generic_sensitive']
            elif 'password' in pii_type.lower():
                return templates['generic_sensitive']
            else:
                return templates['generic_sensitive']
        else:
            # Multiple types
            types_str = ', '.join(pii_types)
            return templates['generic_sensitive']

    def generate_response(self, query: str, db_results: List[Dict], intent: str = 'QUERY', language: str = None) -> str:
        """Generate response based on database results"""
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

    def _generate_with_phi3_storage(self, pii_types: List[str], language: str) -> str:
        """Generate storage confirmation using Phi-3"""
        lang_instruction = self._get_language_instruction(language)

        prompt = f"""You are a helpful privacy-focused assistant. {lang_instruction}

The user has just stored sensitive information of these types: {', '.join(pii_types)}

Generate a brief, friendly confirmation message that:
1. Confirms the data was stored locally
2. Emphasizes it was NOT sent to OpenAI
3. Mentions the data is secure
4. Uses appropriate emojis
5. Is conversational and reassuring

Keep it under 50 words.

Response:"""

        return self._call_phi3(prompt)

    def _generate_with_phi3_query(self, query: str, db_results: List[Dict], language: str) -> str:
        """Generate query response using Phi-3"""
        lang_instruction = self._get_language_instruction(language)

        result = db_results[0]
        content = result.get('content', '')

        prompt = f"""You are a helpful assistant. {lang_instruction}

User asked: "{query}"

Found in local database: {content}

Provide a brief, natural response that gives the user their requested information. Be conversational and use appropriate emojis.

Keep it under 30 words.

Response:"""

        return self._call_phi3(prompt)

    def _call_phi3(self, prompt: str) -> str:
        """Call Phi-3 model via Ollama"""
        try:
            result = subprocess.run(
                ['ollama', 'run', 'phi3'],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=10  # 10 second timeout
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