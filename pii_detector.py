#!/usr/bin/env python3
"""
AI Chat Terminal - PII Detection Module
Microsoft Presidio Integration for enhanced PII detection
"""

import os
import re
import sys
import warnings
from typing import Dict, List, Tuple, Optional

# Suppress warnings for clean operation
warnings.filterwarnings("ignore", category=UserWarning)
os.environ['PYTHONWARNINGS'] = 'ignore::UserWarning'

# Try to import Presidio - graceful fallback if not available
HAS_PRESIDIO = False
try:
    from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer
    from presidio_analyzer.nlp_engine import NlpEngineProvider
    HAS_PRESIDIO = True
except ImportError:
    print("Note: Presidio not available, using regex-based PII detection", file=sys.stderr)

class PIIDetector:
    def __init__(self, language='de'):
        self.language = language
        self.analyzer = None

        if HAS_PRESIDIO:
            try:
                # Initialize Presidio analyzer
                self.analyzer = AnalyzerEngine()
                self._add_custom_recognizers()
            except Exception as e:
                print(f"Warning: Could not initialize Presidio: {e}", file=sys.stderr)
                self.analyzer = None

    def _add_custom_recognizers(self):
        """Add custom recognizers for various API keys and tokens"""
        if not self.analyzer:
            return

        # Define custom patterns for different services
        api_patterns = [
            # OpenAI API Keys
            ('OPENAI_API_KEY', r'sk-[a-zA-Z0-9]{48}', 0.9),
            ('OPENAI_PROJECT_KEY', r'sk-proj-[a-zA-Z0-9]{48}', 0.9),

            # AWS Keys
            ('AWS_ACCESS_KEY', r'AKIA[0-9A-Z]{16}', 0.9),
            ('AWS_SECRET_KEY', r'[A-Za-z0-9/+=]{40}', 0.7),

            # GitHub Tokens
            ('GITHUB_TOKEN', r'ghp_[a-zA-Z0-9]{36}', 0.9),
            ('GITHUB_CLASSIC_TOKEN', r'gh[pousr]_[A-Za-z0-9_]{36,251}', 0.9),

            # Google API Keys
            ('GOOGLE_API_KEY', r'AIza[0-9A-Za-z-_]{35}', 0.9),

            # Slack Tokens
            ('SLACK_TOKEN', r'xox[baprs]-[0-9a-zA-Z\-]+', 0.9),

            # Generic API Keys (broader pattern)
            ('GENERIC_API_KEY', r'(?i)(api[_\s]?key|token|secret)["\s:=]+[A-Za-z0-9\-_]{20,}', 0.7),

            # Database Connection Strings
            ('DB_CONNECTION', r'(?i)(mongodb|mysql|postgres|redis)://[^\s\'"<>]+', 0.8),

            # JWT Tokens
            ('JWT_TOKEN', r'eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*', 0.8),

            # Private Keys
            ('PRIVATE_KEY', r'-----BEGIN[A-Z\s]+PRIVATE KEY-----[^-]+-----END[A-Z\s]+PRIVATE KEY-----', 0.9),

            # Additional patterns for various services
            ('STRIPE_KEY', r'sk_live_[0-9a-zA-Z]{24}', 0.9),
            ('STRIPE_PUBLISHABLE', r'pk_live_[0-9a-zA-Z]{24}', 0.8),
            ('TELEGRAM_BOT_TOKEN', r'[0-9]{8,10}:[a-zA-Z0-9_-]{35}', 0.9),
        ]

        # Add each pattern as a custom recognizer
        for name, pattern, score in api_patterns:
            try:
                recognizer = PatternRecognizer(
                    supported_entity=name,
                    patterns=[Pattern(name=name, regex=pattern, score=score)]
                )
                self.analyzer.registry.add_recognizer(recognizer)
            except Exception as e:
                # Continue if one pattern fails
                print(f"Warning: Could not add pattern {name}: {e}", file=sys.stderr)

    def check_for_pii(self, text: str) -> Tuple[bool, List[str], List[Dict]]:
        """
        Check if text contains PII (User is ENTERING PII)
        Returns: (has_pii, entity_types, details)
        """
        if not text or not text.strip():
            return False, [], []

        # Use Presidio if available
        if HAS_PRESIDIO and self.analyzer:
            try:
                return self._presidio_check(text)
            except Exception as e:
                print(f"Presidio check failed: {e}", file=sys.stderr)
                # Fall back to regex

        # Fallback to regex-based detection
        return self._regex_fallback_check(text)

    def _presidio_check(self, text: str) -> Tuple[bool, List[str], List[Dict]]:
        """Use Presidio for PII detection"""
        # Analyze with Presidio
        results = self.analyzer.analyze(text=text, language='en')  # Use 'en' for best coverage

        if not results:
            return False, [], []

        # Extract entity types and details
        entity_types = list(set([r.entity_type for r in results]))
        details = []

        for result in results:
            details.append({
                'type': result.entity_type,
                'text': text[result.start:result.end],
                'start': result.start,
                'end': result.end,
                'score': result.score
            })

        return True, entity_types, details

    def _regex_fallback_check(self, text: str) -> Tuple[bool, List[str], List[Dict]]:
        """Fallback regex-based PII detection when Presidio unavailable"""
        patterns = {
            'CREDIT_CARD': [
                r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b',
                r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
            ],
            'EMAIL': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            'PHONE': [
                r'\+?[1-9]\d{1,14}',
                r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
                r'\+\d{1,3}[\s-]?\d{1,14}'
            ],
            'API_KEY': [
                r'sk-[a-zA-Z0-9]{48}',
                r'AKIA[0-9A-Z]{16}',
                r'ghp_[a-zA-Z0-9]{36}',
                r'AIza[0-9A-Za-z-_]{35}',
                r'xox[baprs]-[0-9a-zA-Z\-]+'
            ],
            'PASSWORD': [
                r'(?i)(password|passwort|contraseña|mot\s+de\s+passe)["\s:=]+[^\s]{6,}',
                r'(?i)(pwd|pass)["\s:=]+[^\s]{6,}'
            ],
            'SSN': [
                r'\b\d{3}-\d{2}-\d{4}\b',
                r'\b\d{9}\b'
            ]
        }

        found_types = []
        details = []

        for entity_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    if entity_type not in found_types:
                        found_types.append(entity_type)

                    details.append({
                        'type': entity_type,
                        'text': match.group(),
                        'start': match.start(),
                        'end': match.end(),
                        'score': 0.8  # Default confidence for regex
                    })

        return len(found_types) > 0, found_types, details

    def is_asking_for_pii(self, text: str) -> bool:
        """
        Check if user is ASKING for PII (fallback when OpenAI Function Calling doesn't trigger)
        """
        if not text:
            return False

        text_lower = text.lower()

        # Patterns that indicate user is asking for private data
        asking_patterns = [
            # German
            r'(was ist |wie lautet |zeig mir |gib mir )?(mein|meine)',
            r'(welche|welcher|welches).*(habe ich|ist mein)',

            # English
            r'(what is |what\'s |show me |give me )?(my|the)',
            r'(which|what).*(do i have|is my)',

            # Spanish
            r'(qué es |cuál es |muestra mi |dame mi )?(mi|el mío)',
            r'(cuál|qué).*(tengo|es mi)',
        ]

        # PII-related keywords
        pii_keywords = [
            # German
            'kreditkarte', 'passwort', 'pin', 'nummer', 'schlüssel', 'api', 'token',
            'telefon', 'handy', 'email', 'adresse', 'konto', 'bank',

            # English
            'credit card', 'password', 'pin', 'number', 'key', 'api', 'token',
            'phone', 'mobile', 'email', 'address', 'account', 'bank',

            # Spanish
            'tarjeta', 'contraseña', 'número', 'clave', 'teléfono', 'correo'
        ]

        # Check if text matches asking pattern AND contains PII keywords
        has_asking_pattern = any(re.search(pattern, text_lower) for pattern in asking_patterns)
        has_pii_keyword = any(keyword in text_lower for keyword in pii_keywords)

        return has_asking_pattern and has_pii_keyword

    def get_detection_info(self) -> Dict:
        """Get information about available detection methods"""
        info = {
            'presidio_available': HAS_PRESIDIO,
            'analyzer_ready': self.analyzer is not None,
            'fallback_available': True,
            'supported_languages': ['en', 'de', 'es', 'fr'] if HAS_PRESIDIO else ['multi'],
            'detection_methods': []
        }

        if HAS_PRESIDIO and self.analyzer:
            info['detection_methods'].append('Presidio NER')
        info['detection_methods'].append('Regex patterns')

        return info

def main():
    """Test the PII detector"""
    detector = PIIDetector()

    print("🔍 PII Detector Test Suite")
    print("=" * 50)

    # Display detection info
    info = detector.get_detection_info()
    print(f"Presidio available: {info['presidio_available']}")
    print(f"Detection methods: {', '.join(info['detection_methods'])}")
    print()

    # Test cases
    test_cases = [
        # Credit cards
        "My credit card is 4532-1234-5678-9012",
        "Meine Kreditkartennummer ist 4111-1111-1111-1111",

        # API Keys
        "API key: sk-proj-abc123def456ghi789jkl012mno345pqr678stu901",
        "GitHub token: ghp_1234567890abcdef1234567890abcdef12",

        # Emails and phones
        "Contact me at test@example.com or +49 151 12345678",
        "Meine E-Mail: martin.test@domain.de",

        # Passwords
        "Password for account: mySecretPassword123",
        "Passwort für Database: SuperGeheim2023",

        # Non-PII (should not trigger)
        "What's the weather like today?",
        "Explain quantum physics",
        "Wie geht es dir?",

        # Edge cases
        "I need a card for the presentation",  # Should NOT trigger
        "Card number format is 1234-XXXX-XXXX-XXXX",  # Should NOT trigger
    ]

    for i, text in enumerate(test_cases, 1):
        print(f"Test {i}: {text}")

        has_pii, types, details = detector.check_for_pii(text)

        if has_pii:
            print(f"  ✅ PII detected: {', '.join(types)}")
            for detail in details:
                print(f"    - {detail['type']}: {detail['text']} (confidence: {detail['score']:.2f})")
        else:
            print("  ❌ No PII detected")

        print()

if __name__ == "__main__":
    main()