#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local Storage Detector - Multilingual Keyword System
Detects user intent to save data locally or retrieve from local DB
Simple keyword matching without hardcoded PII types
"""

from typing import Tuple, Optional
import re

# Multilingual keywords for "save locally" intent
SAVE_KEYWORDS = {
    'de': [
        'speichere lokal', 'speicher lokal', 'auf meinem computer',
        'lokal speichern', 'in meiner datenbank', 'in meine db',
        'speichere das', 'merke dir das', 'behalte das'
    ],
    'en': [
        'save locally', 'store locally', 'on my computer',
        'save local', 'in my database', 'in my db',
        'remember this', 'keep this', 'store this'
    ],
    'es': [
        'guarda localmente', 'guardar localmente', 'en mi ordenador',
        'en mi computadora', 'en mi base de datos', 'en mi db',
        'recuerda esto', 'guarda esto'
    ],
    'fr': [
        'enregistre localement', 'enregistrer localement', 'sur mon ordinateur',
        'dans ma base de données', 'dans ma db',
        'souviens-toi de ça', 'garde ça'
    ],
    'it': [
        'salva localmente', 'salvare localmente', 'sul mio computer',
        'nel mio database', 'nel mio db',
        'ricorda questo', 'conserva questo'
    ],
    'pt': [
        'salvar localmente', 'guardar localmente', 'no meu computador',
        'na minha base de dados', 'no meu db',
        'lembre-se disso', 'guarde isso'
    ],
    'nl': [
        'lokaal opslaan', 'bewaar lokaal', 'op mijn computer',
        'in mijn database', 'in mijn db',
        'onthoud dit', 'bewaar dit'
    ],
    'pl': [
        'zapisz lokalnie', 'przechowuj lokalnie', 'na moim komputerze',
        'w mojej bazie danych', 'w moim db',
        'zapamiętaj to', 'zachowaj to'
    ],
    'ru': [
        'сохрани локально', 'сохранить локально', 'на моём компьютере',
        'в моей базе данных', 'в моей бд',
        'запомни это', 'сохрани это'
    ],
    'ja': [
        'ローカルに保存', 'ローカル保存', '私のコンピューター',
        'データベースに保存', 'dbに保存',
        'これを覚えて', 'これを保存'
    ],
    'zh': [
        '本地保存', '保存到本地', '在我的电脑',
        '在我的数据库', '在我的db',
        '记住这个', '保存这个'
    ],
    'ko': [
        '로컬에 저장', '로컬 저장', '내 컴퓨터에',
        '내 데이터베이스에', '내 db에',
        '이것을 기억해', '이것을 저장해'
    ],
    'ar': [
        'احفظ محليا', 'تخزين محلي', 'على جهازي',
        'في قاعدة بياناتي', 'في db الخاص بي',
        'تذكر هذا', 'احتفظ بهذا'
    ],
    'hi': [
        'स्थानीय रूप से सहेजें', 'मेरे कंप्यूटर पर',
        'मेरे डेटाबेस में', 'मेरे db में',
        'इसे याद रखें', 'इसे सहेजें'
    ],
    'tr': [
        'yerel olarak kaydet', 'bilgisayarımda',
        'veri tabanımda', 'db\'mde',
        'bunu hatırla', 'bunu kaydet'
    ],
    'sv': [
        'spara lokalt', 'på min dator',
        'i min databas', 'i min db',
        'kom ihåg detta', 'spara detta'
    ],
    'da': [
        'gem lokalt', 'på min computer',
        'i min database', 'i min db',
        'husk dette', 'gem dette'
    ],
    'fi': [
        'tallenna paikallisesti', 'tietokoneellani',
        'tietokannassani', 'db:ssäni',
        'muista tämä', 'tallenna tämä'
    ],
    'no': [
        'lagre lokalt', 'på min datamaskin',
        'i min database', 'i min db',
        'husk dette', 'lagre dette'
    ]
}

# Multilingual keywords for "retrieve from DB" intent
RETRIEVE_KEYWORDS = {
    'de': [
        'aus meiner db', 'aus der datenbank', 'aus meiner datenbank',
        'lokale daten', 'meine gespeicherten daten', 'was habe ich gespeichert',
        'zeige mir meine daten', 'meine lokalen daten'
    ],
    'en': [
        'from my db', 'from database', 'from my database',
        'local data', 'my stored data', 'what did i save',
        'show my data', 'my local data'
    ],
    'es': [
        'de mi db', 'de la base de datos', 'de mi base de datos',
        'datos locales', 'mis datos guardados', 'qué guardé',
        'muestra mis datos', 'mis datos locales'
    ],
    'fr': [
        'de ma db', 'de la base de données', 'de ma base de données',
        'données locales', 'mes données enregistrées', 'qu\'ai-je sauvegardé',
        'montre mes données', 'mes données locales'
    ],
    'it': [
        'dal mio db', 'dal database', 'dal mio database',
        'dati locali', 'i miei dati salvati', 'cosa ho salvato',
        'mostra i miei dati', 'i miei dati locali'
    ],
    'pt': [
        'do meu db', 'do banco de dados', 'da minha base de dados',
        'dados locais', 'meus dados salvos', 'o que eu salvei',
        'mostre meus dados', 'meus dados locais'
    ],
    'nl': [
        'uit mijn db', 'uit database', 'uit mijn database',
        'lokale gegevens', 'mijn opgeslagen gegevens', 'wat heb ik opgeslagen',
        'toon mijn gegevens', 'mijn lokale gegevens'
    ],
    'pl': [
        'z mojej db', 'z bazy danych', 'z mojej bazy danych',
        'dane lokalne', 'moje zapisane dane', 'co zapisałem',
        'pokaż moje dane', 'moje lokalne dane'
    ],
    'ru': [
        'из моей бд', 'из базы данных', 'из моей базы данных',
        'локальные данные', 'мои сохраненные данные', 'что я сохранил',
        'покажи мои данные', 'мои локальные данные'
    ],
    'ja': [
        '私のdbから', 'データベースから', '私のデータベースから',
        'ローカルデータ', '保存したデータ', '何を保存したか',
        '私のデータを表示', 'ローカルに保存したデータ'
    ],
    'zh': [
        '从我的db', '从数据库', '从我的数据库',
        '本地数据', '我保存的数据', '我保存了什么',
        '显示我的数据', '我的本地数据'
    ],
    'ko': [
        '내 db에서', '데이터베이스에서', '내 데이터베이스에서',
        '로컬 데이터', '내가 저장한 데이터', '내가 저장한 것',
        '내 데이터 표시', '내 로컬 데이터'
    ],
    'ar': [
        'من db الخاص بي', 'من قاعدة البيانات', 'من قاعدة بياناتي',
        'البيانات المحلية', 'بياناتي المحفوظة', 'ماذا حفظت',
        'أظهر بياناتي', 'بياناتي المحلية'
    ],
    'hi': [
        'मेरे db से', 'डेटाबेस से', 'मेरे डेटाबेस से',
        'स्थानीय डेटा', 'मेरा सहेजा डेटा', 'मैंने क्या सहेजा',
        'मेरा डेटा दिखाएं', 'मेरा स्थानीय डेटा'
    ],
    'tr': [
        'db\'mden', 'veri tabanından', 'veri tabanımdan',
        'yerel veriler', 'kaydettiğim veriler', 'ne kaydettim',
        'verilerimi göster', 'yerel verilerim'
    ],
    'sv': [
        'från min db', 'från databasen', 'från min databas',
        'lokal data', 'mina sparade data', 'vad har jag sparat',
        'visa min data', 'min lokala data'
    ],
    'da': [
        'fra min db', 'fra databasen', 'fra min database',
        'lokal data', 'mine gemte data', 'hvad har jeg gemt',
        'vis mine data', 'min lokale data'
    ],
    'fi': [
        'omasta db:stä', 'tietokannasta', 'omasta tietokannasta',
        'paikallinen data', 'tallennetut tiedot', 'mitä tallensin',
        'näytä tietoni', 'paikalliset tiedot'
    ],
    'no': [
        'fra min db', 'fra databasen', 'fra min database',
        'lokal data', 'mine lagrede data', 'hva har jeg lagret',
        'vis mine data', 'min lokale data'
    ]
}


class LocalStorageDetector:
    """Detects user intent for local storage operations via keywords"""

    def __init__(self):
        """Initialize detector with all keyword dictionaries"""
        self.save_keywords = SAVE_KEYWORDS
        self.retrieve_keywords = RETRIEVE_KEYWORDS

    def detect_save_locally(self, text: str) -> bool:
        """
        Detect if user wants to save data locally

        Args:
            text: User input message

        Returns:
            True if save intent detected, False otherwise
        """
        text_lower = text.lower()

        # Check all languages
        for lang, keywords in self.save_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return True

        return False

    def detect_retrieve_from_db(self, text: str) -> bool:
        """
        Detect if user wants to retrieve data from local DB

        Args:
            text: User input message

        Returns:
            True if retrieve intent detected, False otherwise
        """
        text_lower = text.lower()

        # Check all languages
        for lang, keywords in self.retrieve_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return True

        return False

    def get_intent(self, text: str) -> Tuple[str, bool]:
        """
        Detect user intent from text

        Args:
            text: User input message

        Returns:
            Tuple of (intent_type, detected)
            intent_type: 'save_local', 'retrieve_local', or 'normal'
            detected: True if keyword detected, False otherwise
        """
        if self.detect_save_locally(text):
            return ('save_local', True)
        elif self.detect_retrieve_from_db(text):
            return ('retrieve_local', True)
        else:
            return ('normal', False)


# For testing
if __name__ == '__main__':
    detector = LocalStorageDetector()

    # Test cases
    test_cases = [
        # German
        ("speichere lokal: mein API Key ist abc123", True, 'save'),
        ("was ist aus meiner db über Python?", True, 'retrieve'),
        ("wie geht es dir?", False, None),

        # English
        ("save locally: my password is secret123", True, 'save'),
        ("what do I have from my database?", True, 'retrieve'),
        ("tell me a joke", False, None),

        # Spanish
        ("guarda localmente: mi correo es test@example.com", True, 'save'),
        ("qué guardé de mi db?", True, 'retrieve'),

        # Mixed
        ("Ich möchte das lokal speichern: wichtige Info", True, 'save'),
        ("Zeige mir meine lokalen daten über API", True, 'retrieve'),
    ]

    print("🧪 Testing Local Storage Detector\n")

    for text, should_detect, intent_type in test_cases:
        intent, detected = detector.get_intent(text)

        if intent_type == 'save':
            expected_intent = 'save_local'
        elif intent_type == 'retrieve':
            expected_intent = 'retrieve_local'
        else:
            expected_intent = 'normal'

        status = "✅" if (detected == should_detect and intent == expected_intent) else "❌"
        print(f"{status} '{text[:50]}...'")
        print(f"   Expected: {expected_intent}, Got: {intent}\n")
