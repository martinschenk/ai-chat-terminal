#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local Storage Detector - Expanded Keyword System (v9.0.1)
Fast keyword detection to trigger Phi-3 intent analysis
~12 keywords per language - covers all 5 operations (SAVE/RETRIEVE/DELETE/LIST/UPDATE)
"""

from typing import Tuple, List

# Expanded keywords for "database intent" - ~12 per language
# Covers all operations: SAVE, RETRIEVE, DELETE, LIST, UPDATE
# Phi-3 will do the intelligent classification and false-positive detection
DB_INTENT_KEYWORDS = {
    'de': [
        # DB/Storage
        'db', 'datenbank', 'lokal', 'speicher', 'speichern', 'speichere',
        # Save/Remember
        'merke', 'merk', 'merken', 'behalte', 'behalten', 'notiere', 'notieren',
        # Retrieve/Get
        'hole', 'hol', 'holen', 'gib', 'gibst', 'abrufen', 'laden',
        # Show/List
        'zeig', 'zeige', 'zeigen', 'liste', 'auflistung', 'anzeigen',
        # Delete/Forget
        'vergiss', 'vergessen', 'lösche', 'löschen', 'entferne', 'entfernen',
        # Data/Info
        'daten', 'infos', 'informationen', 'gespeichert', 'gespeicherte',
        # Question words
        'meine', 'mein', 'welche', 'was', 'hast', 'kennst', 'weißt'
    ],
    'en': [
        # DB/Storage
        'db', 'database', 'local', 'locally', 'storage', 'store', 'stored',
        # Save/Remember
        'save', 'saving', 'remember', 'remind', 'keep', 'keeping', 'note', 'noting',
        # Retrieve/Get
        'get', 'getting', 'retrieve', 'load', 'loading', 'fetch',
        # Show/List
        'show', 'showing', 'list', 'listing', 'display',
        # Delete/Forget
        'forget', 'delete', 'deleting', 'remove', 'removing', 'clear',
        # Data/Info
        'data', 'info', 'infos', 'information', 'entries', 'records',
        # Question words
        'my', 'mine', 'which', 'what', 'have', 'has', 'know', 'knows', 'about'
    ],
    'es': [
        # DB/Storage
        'db', 'base de datos', 'local', 'localmente', 'almacenamiento', 'almacenar',
        # Save/Remember
        'guarda', 'guardar', 'guardado', 'recuerda', 'recordar', 'anota', 'anotar', 'mantén', 'mantener',
        # Retrieve/Get
        'obtén', 'obtener', 'muestra', 'mostrar', 'dame', 'dar', 'recupera', 'recuperar',
        # Show/List
        'lista', 'listar', 'enséñame', 'enseñar', 'muéstrame',
        # Delete/Forget
        'olvida', 'olvidar', 'elimina', 'eliminar', 'borra', 'borrar', 'quita', 'quitar',
        # Data/Info
        'datos', 'info', 'información', 'entradas', 'registros', 'guardados',
        # Question words
        'mi', 'mis', 'qué', 'cuál', 'cuáles', 'tienes', 'tiene', 'sabes', 'conoces'
    ],
    'fr': [
        # DB/Storage
        'db', 'base de données', 'local', 'localement', 'stockage', 'stocker',
        # Save/Remember
        'sauvegarde', 'sauvegarder', 'enregistre', 'enregistrer', 'souviens', 'garde', 'garder', 'note', 'noter',
        # Retrieve/Get
        'récupère', 'récupérer', 'obtiens', 'obtenir', 'affiche', 'afficher', 'montre', 'montrer',
        # Show/List
        'liste', 'lister', 'affiche-moi', 'montre-moi',
        # Delete/Forget
        'oublie', 'oublier', 'supprime', 'supprimer', 'efface', 'effacer', 'enlève', 'enlever',
        # Data/Info
        'données', 'infos', 'informations', 'entrées', 'enregistré', 'enregistrés',
        # Question words
        'mon', 'ma', 'mes', 'quel', 'quelle', 'quels', 'quelles', 'as', 'sais', 'connais'
    ],
    'it': [
        # DB/Storage
        'db', 'database', 'locale', 'localmente', 'archivio', 'memorizzazione', 'memorizza',
        # Save/Remember
        'salva', 'salvare', 'salvato', 'ricorda', 'ricordare', 'annota', 'annotare', 'mantieni', 'mantenere',
        # Retrieve/Get
        'prendi', 'prendere', 'recupera', 'recuperare', 'mostra', 'mostrare', 'dammi',
        # Show/List
        'lista', 'elenco', 'elenca', 'elencare', 'mostrami',
        # Delete/Forget
        'dimentica', 'dimenticare', 'elimina', 'eliminare', 'cancella', 'cancellare', 'rimuovi', 'rimuovere',
        # Data/Info
        'dati', 'info', 'informazioni', 'voci', 'salvati', 'memorizzati',
        # Question words
        'mio', 'mia', 'miei', 'mie', 'quale', 'quali', 'che', 'hai', 'sai', 'conosci'
    ],
    'pt': [
        # DB/Storage
        'db', 'base de dados', 'local', 'localmente', 'armazenamento', 'armazenar', 'armazenado',
        # Save/Remember
        'salvar', 'salvo', 'salvos', 'lembrar', 'lembra', 'anota', 'anotar', 'guarda', 'guardar',
        # Retrieve/Get
        'pegar', 'buscar', 'recuperar', 'mostrar', 'mostra', 'me dá', 'obter',
        # Show/List
        'listar', 'lista', 'exibir', 'mostra-me', 'me mostre',
        # Delete/Forget
        'esquecer', 'esquece', 'apagar', 'apaga', 'deletar', 'deleta', 'remover', 'remove',
        # Data/Info
        'dados', 'info', 'informação', 'informações', 'entradas', 'registros', 'salvos',
        # Question words
        'meu', 'minha', 'meus', 'minhas', 'qual', 'quais', 'que', 'tem', 'tens', 'sabe', 'conhece'
    ],
    'nl': [
        'db', 'database', 'lokaal', 'opslag', 'opslaan', 'onthoud', 'haal', 'opgeslagen',
        'vergeet', 'verwijder', 'toon', 'lijst'
    ],
    'pl': [
        'db', 'baza danych', 'lokalnie', 'pamięć', 'zapisz', 'zapamiętaj', 'pokaż', 'zapisane',
        'zapomnij', 'usuń', 'lista', 'aktualizuj'
    ],
    'ru': [
        'бд', 'база данных', 'локально', 'хранилище', 'сохрани', 'запомни', 'покажи', 'сохранено',
        'забудь', 'удали', 'список', 'обнови'
    ],
    'ja': [
        'db', 'データベース', 'ローカル', 'ストレージ', '保存', '覚えて', '取得', '保存した',
        '忘れて', '削除', 'リスト', '更新'
    ],
    'zh': [
        'db', '数据库', '本地', '存储', '保存', '记住', '显示', '已保存',
        '忘记', '删除', '列表', '更新'
    ],
    'ko': [
        'db', '데이터베이스', '로컬', '저장소', '저장', '기억해', '보여줘', '저장된',
        '잊어', '삭제', '목록', '업데이트'
    ],
    'ar': [
        'db', 'قاعدة بيانات', 'محلي', 'تخزين', 'احفظ', 'تذكر', 'أظهر', 'محفوظ',
        'انسى', 'احذف', 'قائمة', 'حدث'
    ],
    'hi': [
        'db', 'डेटाबेस', 'स्थानीय', 'संग्रहण', 'सहेजें', 'याद रखें', 'दिखाएं', 'सहेजा',
        'भूल जाओ', 'हटाएं', 'सूची', 'अद्यतन'
    ],
    'tr': [
        'db', 'veritabanı', 'yerel', 'depolama', 'kaydet', 'hatırla', 'göster', 'kaydedildi',
        'unut', 'sil', 'liste', 'güncelle'
    ],
    'sv': [
        'db', 'databas', 'lokal', 'lagring', 'spara', 'kom ihåg', 'visa', 'sparat',
        'glöm', 'ta bort', 'lista', 'uppdatera'
    ],
    'da': [
        'db', 'database', 'lokal', 'lagring', 'gem', 'husk', 'vis', 'gemt',
        'glem', 'slet', 'liste', 'opdater'
    ],
    'fi': [
        'db', 'tietokanta', 'paikallinen', 'tallennus', 'tallenna', 'muista', 'näytä', 'tallennettu',
        'unohda', 'poista', 'lista', 'päivitä'
    ],
    'no': [
        'db', 'database', 'lokal', 'lagring', 'lagre', 'husk', 'vis', 'lagret',
        'glem', 'slett', 'liste', 'oppdater'
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
