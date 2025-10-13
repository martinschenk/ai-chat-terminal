#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local Storage Detector - v10.2.0 (Dynamic Keyword Loading)
Loads keywords from lang/*.conf files instead of hardcoding
Triggers Llama 3.2 for intelligent classification + false-positive detection
"""

import os
import re
from pathlib import Path
from typing import Tuple, List, Dict, Set


class LocalStorageDetector:
    """Fast keyword detector to trigger Llama 3.2 classification"""

    def __init__(self, config_dir: str = None):
        """
        Initialize detector with keywords from lang/*.conf files

        Args:
            config_dir: Path to .aichat config directory (defaults to ~/.aichat)
        """
        self.config_dir = config_dir or str(Path.home() / '.aichat')
        self.keywords = self._load_keywords_from_lang_files()

    def _load_keywords_from_lang_files(self) -> Set[str]:
        """
        Load DB intent keywords from all lang/*.conf files

        Returns:
            Set of all keywords from all languages combined
        """
        all_keywords = set()
        lang_dir = Path(self.config_dir) / 'lang'

        if not lang_dir.exists():
            # Fallback to basic English keywords
            return {'save', 'store', 'remember', 'show', 'get', 'delete', 'remove',
                    'list', 'what', 'my', 'database', 'db', 'local', 'data'}

        # Keywords to load from each lang file
        keyword_vars = [
            'KEYWORDS_SAVE',
            'KEYWORDS_RETRIEVE',
            'KEYWORDS_DELETE',
            'KEYWORDS_LIST'
        ]

        # Common trigger words (add these too)
        common_words = ['my', 'mein', 'mi', 'mon', 'mio', 'meu',  # possessive
                       'db', 'database', 'datenbank', 'base de datos',  # DB words
                       'local', 'lokal', 'locally', 'localmente',  # local
                       'data', 'daten', 'datos', 'données']  # data

        for lang_file in lang_dir.glob('*.conf'):
            try:
                with open(lang_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract keywords from each KEYWORDS_* variable
                for var_name in keyword_vars:
                    pattern = rf'{var_name}="([^"]+)"'
                    match = re.search(pattern, content)
                    if match:
                        keywords_str = match.group(1)
                        # Split by comma and clean
                        keywords = [kw.strip().lower() for kw in keywords_str.split(',') if kw.strip()]
                        all_keywords.update(keywords)

            except Exception as e:
                # Skip this lang file if error
                continue

        # Add common trigger words
        all_keywords.update(common_words)

        return all_keywords

    def detect_db_intent(self, text: str) -> Tuple[bool, List[str]]:
        """
        Quick check: Does text contain ANY database-related keyword?

        Args:
            text: User input message

        Returns:
            Tuple of (detected, matched_keywords)
            - detected: True if any keyword found
            - matched_keywords: List of keywords that matched
        """
        text_lower = text.lower()
        matched = []

        # Check all keywords (loaded from lang files)
        for keyword in self.keywords:
            if keyword in text_lower:
                matched.append(keyword)

        return (len(matched) > 0, matched)



# For testing
if __name__ == '__main__':
    detector = LocalStorageDetector()

    test_cases = [
        # Should trigger
        ("merke dir meine Email ist test@test.com", True),
        ("wie ist meine Telefonnummer?", False),  # No keyword!
        ("zeig mir was in der db gespeichert ist", True),
        ("hole meine Daten aus der Datenbank", True),
        ("save this locally", True),
        ("what's stored in the database?", True),

        # Should NOT trigger
        ("Wie ist das Wetter heute?", False),
        ("Was ist 2+2?", False),
        ("Tell me a joke", False),

        # Potential false positives (Phi-3 will filter)
        ("Was ist eine Datenbank?", True),  # Contains 'datenbank' but educational
        ("Ich habe das gestern in der DB gespeichert", True),  # Past tense
    ]

    print("🧪 Testing Minimal Keyword Detector (v9.0.0)\n")
    print("Note: False positives OK - Phi-3 will filter them!\n")

    for text, should_trigger in test_cases:
        detected, keywords = detector.detect_db_intent(text)
        status = "✅" if detected == should_trigger else "⚠️"

        print(f"{status} '{text}'")
        print(f"   Detected: {detected}, Keywords: {keywords}")

        if detected and not should_trigger:
            print(f"   ⚠️  False positive (Phi-3 will handle)")

        print()

    # Count total keywords
    total = sum(len(kw) for kw in DB_INTENT_KEYWORDS.values())
    print(f"\n📊 Total keywords: {total} ({len(DB_INTENT_KEYWORDS)} languages × ~8 keywords)")
    print(f"🚀 Speedup vs v8.x: ~7.5× faster ({total} checks vs 1140 checks)")
