#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Action Detector v10.0.0 - KISS!
Lädt Keywords aus lang/*.conf und erkennt ACTION
"""

import os

class ActionDetector:
    """Detect ACTION from user input using keywords from lang files"""

    def __init__(self, config_dir: str, language: str = 'en'):
        """
        Args:
            config_dir: Path to config directory (contains lang/)
            language: Language code (de, en, es, etc.)
        """
        self.config_dir = config_dir
        self.language = language
        self.keywords = self._load_keywords()

    def _load_keywords(self) -> dict:
        """Load keywords from lang/*.conf"""
        lang_file = os.path.join(self.config_dir, 'lang', f'{self.language}.conf')

        # Fallback to English if lang file not found
        if not os.path.exists(lang_file):
            lang_file = os.path.join(self.config_dir, 'lang', 'en.conf')

        keywords = {
            'SAVE': [],
            'RETRIEVE': [],
            'DELETE': [],
            'LIST': []
        }

        if not os.path.exists(lang_file):
            print(f"⚠️  No lang file found, using defaults", file=sys.stderr)
            return keywords

        # Parse lang file
        with open(lang_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()

                # Look for KEYWORDS_* lines
                if line.startswith('KEYWORDS_SAVE='):
                    keywords['SAVE'] = line.split('=', 1)[1].strip('"').split(',')
                elif line.startswith('KEYWORDS_RETRIEVE='):
                    keywords['RETRIEVE'] = line.split('=', 1)[1].strip('"').split(',')
                elif line.startswith('KEYWORDS_DELETE='):
                    keywords['DELETE'] = line.split('=', 1)[1].strip('"').split(',')
                elif line.startswith('KEYWORDS_LIST='):
                    keywords['LIST'] = line.split('=', 1)[1].strip('"').split(',')

        # If not English, also load English keywords (fallback)
        if self.language != 'en':
            en_file = os.path.join(self.config_dir, 'lang', 'en.conf')
            if os.path.exists(en_file):
                with open(en_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('KEYWORDS_SAVE='):
                            keywords['SAVE'].extend(line.split('=', 1)[1].strip('"').split(','))
                        elif line.startswith('KEYWORDS_RETRIEVE='):
                            keywords['RETRIEVE'].extend(line.split('=', 1)[1].strip('"').split(','))
                        elif line.startswith('KEYWORDS_DELETE='):
                            keywords['DELETE'].extend(line.split('=', 1)[1].strip('"').split(','))
                        elif line.startswith('KEYWORDS_LIST='):
                            keywords['LIST'].extend(line.split('=', 1)[1].strip('"').split(','))

        return keywords

    def detect(self, user_input: str) -> str:
        """
        Detect action from user input

        Args:
            user_input: User message

        Returns:
            'SAVE', 'RETRIEVE', 'DELETE', 'LIST', or 'NORMAL'
        """
        user_lower = user_input.lower()

        # Priority order: DELETE > LIST > SAVE > RETRIEVE
        # (to avoid conflicts)

        # DELETE
        for keyword in self.keywords['DELETE']:
            if keyword.strip().lower() in user_lower:
                return 'DELETE'

        # LIST (check for phrases like "show all", "list all")
        for keyword in self.keywords['LIST']:
            if keyword.strip().lower() in user_lower:
                return 'LIST'

        # SAVE
        for keyword in self.keywords['SAVE']:
            if keyword.strip().lower() in user_lower:
                return 'SAVE'

        # RETRIEVE
        for keyword in self.keywords['RETRIEVE']:
            if keyword.strip().lower() in user_lower:
                return 'RETRIEVE'

        # No action detected
        return 'NORMAL'


# Test
if __name__ == '__main__':
    import sys

    detector = ActionDetector(os.path.expanduser('~/.aichat'), 'de')

    tests = [
        "speichere my email test@test.com",
        "zeig my email",
        "lösche my email",
        "liste alle daten",
        "was ist das Wetter?",
    ]

    print("🧪 Testing Action Detector\n")
    for test in tests:
        action = detector.detect(test)
        print(f"{action:10} ← {test}")
