# AI Chat Terminal

Lokaler Chat im Terminal mit automatischem Datenschutz für sensible Daten.

[![Version](https://img.shields.io/badge/version-6.2.0-blue.svg)](https://github.com/martinschenk/ai-chat-terminal)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://github.com/martinschenk/ai-chat-terminal)

## Was ist AI Chat Terminal?

Ein Chat-System das im Terminal läuft und automatisch entscheidet: Sensible Eingaben bleiben lokal in einer Vektordatenbank, öffentliche Fragen gehen an OpenAI.

**Funktionsweise:**
- Eingabe mit privaten Daten (API Keys, Passwörter) → Lokale Speicherung
- Öffentliche Fragen (z.B. "Hauptstadt Frankreich?") → OpenAI
- Abfrage privater Daten → Lokale Datenbank (nie Cloud)

### Datenfluss: Eingabe & Speicherung

```
┌───────────────────────────────────────────────┐
│ Eingabe: "Meine API Key ist sk-abc123..."    │
└────────────────────┬──────────────────────────┘
                     ↓
          ┌──────────────────────┐
          │ Privacy Classifier   │ ← KI entscheidet automatisch
          │   (lokal auf Mac)    │
          └──────────┬───────────┘
                     ↓
         ┌───────────┴───────────┐
         ↓                       ↓
   🔒 SENSIBEL              🌐 ÖFFENTLICH
   (lokal speichern)        (→ OpenAI)
         ↓                       ↓
   [Vektordatenbank]        [OpenAI GPT-4]
   ~/.aichat/memory.db
```

### Datenfluss: Abruf privater Daten

```
┌────────────────────────────────────┐
│ Frage: "Was ist meine API Key?"   │
└─────────────┬──────────────────────┘
              ↓
    ┌─────────────────────┐
    │ Erkennt: Private     │
    │ Daten-Abfrage       │
    └─────────┬───────────┘
              ↓
       🔒 Lokale DB
       ├─ Semantische Suche in Vektordatenbank
       └─ Gibt zurück: "sk-abc123..."

    ❌ Nie an OpenAI gesendet!
```

---

## Quick Start

**Schritt 1: Installation**
```bash
curl -fsSL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | zsh
```

**Schritt 2: Shell neu laden**
```bash
source ~/.zshrc
```

**Schritt 3: Starten**
```bash
chat
```

---

## Requirements

| | Minimum | Empfohlen |
|---|---|---|
| **macOS** | Catalina 10.15+ | Monterey 12+ |
| **RAM** | 8 GB | 16 GB |
| **Speicher** | 5 GB frei | 10 GB frei |
| **Prozessor** | Intel 2015+ | Apple Silicon M1+ |

### Kompatibilität

- ✅ **M1/M2/M3 Mac mit 16+ GB RAM** → Alle Modelle empfohlen
- ✅ **Intel Mac mit 16 GB RAM** → Alle Modelle funktionieren
- ⚠️ **8 GB RAM** → Basis-Modelle (ohne Phi-3)
- ❌ **< macOS Catalina** → Nicht unterstützt (Linux/Windows: Coming soon)

---

## Beispiele

### Sensible Daten (bleiben lokal)

```bash
Du: Meine Kreditkarte ist 4532-1234-5678-9012
AI: [Gespeichert in lokaler DB] 🔒

Du: API Key ist sk-proj-abc123def456
AI: [Gespeichert] 🔒

Du: Was war meine Kreditkarte?
AI: 4532-1234-5678-9012 [Aus lokaler DB] 🔒
```

### Öffentliche Fragen (an OpenAI)

```bash
Du: Hauptstadt von Frankreich?
AI: Paris [OpenAI GPT-4] 🌐

Du: Erkläre Quantenphysik
AI: [Antwort von OpenAI] 🌐
```

---

## Features

- **Automatischer Datenschutz**: KI-basierte Klassifizierung
- **19 Sprachen**: DE, EN, ES, FR, IT, CA, ZH, HI, etc.
- **Vektordatenbank**: SQLite mit semantischer Suche
- **Konfigurierbar**: `/config` Menü für alle Einstellungen
- **OpenAI Integration**: GPT-4, GPT-4o, GPT-4o-mini

---

## Installation Details

### Was wird wo installiert?

**Lokal (~/.aichat/)**
- Scripts, Config, Chat-Historie
- Deine privaten Daten in Vektordatenbank
- Nur von diesem Tool genutzt

**Global (shared)**
- AI-Modelle (HuggingFace Cache)
- Python-Pakete (pip --user)
- Kann von anderen Apps genutzt werden

### Intelligente Model-Auswahl

Das Installer-Script analysiert deinen Mac und empfiehlt:

| Dein Mac | Empfehlung |
|----------|-----------|
| 16+ GB RAM | Presidio ✅ + Phi-3 ✅ |
| 8-16 GB RAM | Presidio ✅, Phi-3 optional |
| <8 GB RAM | Nur Basis-Modelle |

**Beispiel-Output bei 16 GB RAM:**
```
💬 Warum empfohlen für dich?
   Dein Mac hat 16 GB RAM - perfekt für Presidio!
   Schützt Kreditkarten, API-Keys, Passwörter.
```

---

## Technische Details

### Komponenten

| Komponente | Modell | Größe | Zweck |
|------------|--------|-------|-------|
| Privacy Classifier | all-MiniLM-L6-v2 | 22 MB | Routing-Entscheidung |
| Memory System | multilingual-e5-base | 278 MB | Semantische Suche |
| PII Detection | Microsoft Presidio | 350 MB | Erkennung sensibler Daten |
| Response Generator | Phi-3 via Ollama | 2.3 GB | Natürliche Antworten |

### Privacy Layers

1. **PII Detector**: Erkennt konkrete Datentypen (Kreditkarten, API-Keys)
2. **Semantic Classifier**: Versteht Kontext (SENSITIVE/PUBLIC)
3. **Vector Database**: Lokale Speicherung mit Embeddings

---

## Konfiguration

```bash
chat           # Starten
/config        # Einstellungen
```

**Verfügbare Optionen:**
- Sprache wählen (19 verfügbar)
- OpenAI Modell ändern
- Privacy-Level anpassen
- Modelle nachträglich installieren/entfernen
- Context-Window konfigurieren

---

## Deinstallation

**Im Chat:**
```bash
chat
/config
→ [12] Vollständig deinstallieren
```

**Manuell:**
```bash
rm -rf ~/.aichat
```

*Hinweis: Globale Modelle bleiben erhalten (können von anderen Apps genutzt werden)*

---

## FAQ

**Q: Sind meine Daten wirklich privat?**
A: Ja. Sensible Daten werden nie an OpenAI gesendet. Prüfe den Indikator: 🔒 = lokal, 🌐 = OpenAI

**Q: Funktioniert es offline?**
A: Lokale Features ja. OpenAI-Abfragen benötigen Internet.

**Q: Wie funktioniert die Erkennung?**
A: Dreistufig: PII-Detector → Semantic Classifier → Routing

**Q: Kann ich andere Modelle nutzen?**
A: Aktuell nur OpenAI. Support für Claude/Gemini: In Planung

**Q: Linux/Windows Support?**
A: Aktuell nur macOS. Linux: Geplant für v7.0

---

## Lizenz

MIT License - siehe [LICENSE](LICENSE)

**Built with ❤️ for Privacy**
