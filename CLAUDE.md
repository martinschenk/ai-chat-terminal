# Claude Code - Projekt-Instruktionen für AI Chat Terminal

## 🚨 KRITISCHE REGEL: KEINE GROßEN LÖSCHUNGEN OHNE EXPLIZITE GENEHMIGUNG

**WICHTIG:** Bevor du Code löschst oder große Umbauten machst:

1. ⚠️ **STOPP** - Informiere Martin GENAU was du vorhast
2. 📊 **ZEIGE** die Konsequenzen (was geht kaputt? was funktioniert nicht mehr?)
3. 📈 **STATISTIK** - Wieviele Zeilen werden gelöscht? Welche Funktionen?
4. ⏸️ **WARTE** auf explizites OK von Martin
5. ✅ Erst DANN ausführen

### Beispiele für "große Änderungen" die OK brauchen:
- ❌ Prompts um >30% kürzen
- ❌ Funktionen entfernen ohne zu fragen
- ❌ "KISS Approach" der viel löscht
- ❌ "Aufräumen" von angeblich unnötigem Code
- ❌ Refactoring das >50 Zeilen löscht

### Warum?
Wir haben oft Stunden an Optimierungen investiert. Ein "schneller Fix"
kann diese Arbeit in Sekunden zerstören. Besser langsam und sicher!

## Projekt-Details

- **Python 3.9+**
- **Lokale KI:** Qwen 2.5 Coder 7B via Ollama
- **Hauptfeature:** Lokale Datenspeicherung für sensitive Daten
- **Architektur:** Keyword-basierte Vorselektion → Qwen SQL Generation
- **Sprachen:** Deutsch, Englisch, Spanisch

## Entwicklung

- Entwicklung in: `/Users/martin/Development/ai-chat-terminal/`
- Production läuft aus: `/Users/martin/.aichat/`
- Nach Änderungen immer nach `.aichat` kopieren!
- Daemon neustarten: `killall -9 Python` oder spezifische PID
