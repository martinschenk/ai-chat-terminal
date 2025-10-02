#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local Storage Detector - Minimal Keyword System (v9.0.0)
Fast keyword detection to trigger Phi-3 intent analysis
Only 8 keywords per language - Phi-3 does the intelligent work
"""

from typing import Tuple, List

# Minimal keywords for "database intent" - just 8 per language
# Phi-3 will do the intelligent classification and false-positive detection
DB_INTENT_KEYWORDS = {
    'de': [
        'db', 'datenbank', 'lokal', 'speicher', 'speichern', 'merke', 'hole', 'gespeichert'
    ],
    'en': [
        'db', 'database', 'local', 'storage', 'save', 'remember', 'get', 'stored'
    ],
    'es': [
        'db', 'base de datos', 'local', 'guarda', 'guardar', 'recuerda', 'muestra', 'guardado'
    ],
    'fr': [
        'db', 'base de données', 'local', 'stockage', 'sauvegarde', 'souviens', 'récupère', 'enregistré'
    ],
    'it': [
        'db', 'database', 'locale', 'archivio', 'salva', 'ricorda', 'mostra', 'salvato'
    ],
    'pt': [
        'db', 'base de dados', 'local', 'armazenamento', 'salvar', 'lembrar', 'mostrar', 'salvo'
    ],
    'nl': [
        'db', 'database', 'lokaal', 'opslag', 'opslaan', 'onthoud', 'haal', 'opgeslagen'
    ],
    'pl': [
        'db', 'baza danych', 'lokalnie', 'pamięć', 'zapisz', 'zapamiętaj', 'pokaż', 'zapisane'
    ],
    'ru': [
        'бд', 'база данных', 'локально', 'хранилище', 'сохрани', 'запомни', 'покажи', 'сохранено'
    ],
    'ja': [
        'db', 'データベース', 'ローカル', 'ストレージ', '保存', '覚えて', '取得', '保存した'
    ],
    'zh': [
        'db', '数据库', '本地', '存储', '保存', '记住', '显示', '已保存'
    ],
    'ko': [
        'db', '데이터베이스', '로컬', '저장소', '저장', '기억해', '보여줘', '저장된'
    ],
    'ar': [
        'db', 'قاعدة بيانات', 'محلي', 'تخزين', 'احفظ', 'تذكر', 'أظهر', 'محفوظ'
    ],
    'hi': [
        'db', 'डेटाबेस', 'स्थानीय', 'संग्रहण', 'सहेजें', 'याद रखें', 'दिखाएं', 'सहेजा'
    ],
    'tr': [
        'db', 'veritabanı', 'yerel', 'depolama', 'kaydet', 'hatırla', 'göster', 'kaydedildi'
    ],
    'sv': [
        'db', 'databas', 'lokal', 'lagring', 'spara', 'kom ihåg', 'visa', 'sparat'
    ],
    'da': [
        'db', 'database', 'lokal', 'lagring', 'gem', 'husk', 'vis', 'gemt'
    ],
    'fi': [
        'db', 'tietokanta', 'paikallinen', 'tallennus', 'tallenna', 'muista', 'näytä', 'tallennettu'
    ],
    'no': [
        'db', 'database', 'lokal', 'lagring', 'lagre', 'husk', 'vis', 'lagret'
    ]
}


class LocalStorageDetector:
    """Fast keyword detector to trigger Phi-3 intent analysis"""

    def __init__(self):
        """Initialize detector with minimal keyword dictionary"""
        self.keywords = DB_INTENT_KEYWORDS

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

        # Check all languages
        for lang, keywords in self.keywords.items():
            for keyword in keywords:
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
