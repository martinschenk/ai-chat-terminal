# AI-Powered Todo System für GitHub Issues

Ein intelligentes Command-Line Tool, das deine Ideen automatisch in professionelle GitHub Issues verwandelt.

## 🚀 Features

- **🤖 AI-Powered**: OpenAI analysiert deine Eingabe automatisch
- **🌍 Multilingual**: Eingabe auf Deutsch, Output auf Englisch
- **🏷️ Smart Labels**: AI erkennt Bug vs Feature vs Enhancement automatisch
- **⚡ Priority Detection**: Automatische Prioritätserkennung (low/medium/high/critical)
- **💬 Natural Input**: Keine Anführungszeichen, alle Sonderzeichen erlaubt
- **🎯 Project-Aware**: Funktioniert nur im richtigen Git-Repository

## 📋 Installation

### 1. Script erstellen

Erstelle eine Datei `todo` in deinem Projektverzeichnis:

```bash
#!/bin/bash
# AI-Powered GitHub Issue Creator
# Creates GitHub issues from German/English input with AI analysis

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RESET='\033[0m'

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo -e "${RED}Error: Must be run inside a git repository${RESET}"
    exit 1
fi

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed${RESET}"
    echo "Install with: brew install gh"
    exit 1
fi

# Check if authenticated with GitHub
if ! gh auth status >/dev/null 2>&1; then
    echo -e "${RED}Error: Not authenticated with GitHub${RESET}"
    echo "Run: gh auth login"
    exit 1
fi

# Get user input (everything after 'todo')
USER_INPUT="$*"

if [ -z "$USER_INPUT" ]; then
    echo -e "${RED}Error: Please provide an idea or bug report${RESET}"
    echo "Usage: todo Your idea or bug description here"
    exit 1
fi

# Get OpenAI API key from AI Chat Terminal config
AICHAT_DIR="$HOME/.aichat"
ENV_FILE="$AICHAT_DIR/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}Error: OpenAI API key not found${RESET}"
    echo "Please set up AI Chat Terminal first with: chat"
    exit 1
fi

# Source the .env file to get OPENAI_API_KEY
source "$ENV_FILE"

if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}Error: OPENAI_API_KEY not found in $ENV_FILE${RESET}"
    exit 1
fi

echo -e "${BLUE}🤖 Analyzing your input with AI...${RESET}"

# Create AI prompt for analysis
AI_PROMPT="You are a GitHub issue assistant. Analyze the following user input and create a professional GitHub issue.

Instructions:
1. If the input is in German, translate to English
2. Determine the issue type: bug, enhancement, documentation, or question
3. Assess priority: low, medium, high, or critical
4. Create a clear, professional title (max 50 chars)
5. Write a detailed body with Description, Use Case, and Technical Details if applicable
6. Suggest appropriate labels from: bug, enhancement, documentation, question, priority-high, priority-medium, priority-low, priority-critical, memory-system, ui-ux, performance, security

User input: \"$USER_INPUT\"

Respond ONLY with valid JSON in this exact format:
{
  \"title\": \"Clear issue title\",
  \"body\": \"## Description\\n\\nDetailed description here\\n\\n## Use Case\\n\\nWhy this matters\\n\\n## Technical Details\\n\\nImplementation notes if applicable\",
  \"labels\": [\"label1\", \"label2\", \"label3\"],
  \"type\": \"bug|enhancement|documentation|question\",
  \"priority\": \"low|medium|high|critical\"
}"

# Call OpenAI API
RESPONSE=$(curl -s -X POST "https://api.openai.com/v1/chat/completions" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"gpt-4o-mini\",
    \"messages\": [
      {
        \"role\": \"system\",
        \"content\": \"You are a helpful assistant that creates GitHub issues. Always respond with valid JSON only.\"
      },
      {
        \"role\": \"user\",
        \"content\": $(echo "$AI_PROMPT" | jq -R -s .)
      }
    ],
    \"temperature\": 0.3,
    \"max_tokens\": 800
  }")

# Check if API call was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to call OpenAI API${RESET}"
    exit 1
fi

# Extract the content from the API response
AI_CONTENT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content // empty')

if [ -z "$AI_CONTENT" ]; then
    echo -e "${RED}Error: No response from OpenAI API${RESET}"
    echo "API Response: $RESPONSE"
    exit 1
fi

# Parse the AI response JSON
TITLE=$(echo "$AI_CONTENT" | jq -r '.title // empty')
BODY=$(echo "$AI_CONTENT" | jq -r '.body // empty')
LABELS=$(echo "$AI_CONTENT" | jq -r '.labels[]? // empty' | tr '\n' ',' | sed 's/,$//')
TYPE=$(echo "$AI_CONTENT" | jq -r '.type // "enhancement"')
PRIORITY=$(echo "$AI_CONTENT" | jq -r '.priority // "medium"')

# Validate required fields
if [ -z "$TITLE" ] || [ -z "$BODY" ]; then
    echo -e "${RED}Error: AI failed to generate proper issue format${RESET}"
    echo "AI Response: $AI_CONTENT"
    exit 1
fi

# Display what will be created
echo -e "${YELLOW}📝 Creating GitHub issue:${RESET}"
echo -e "${GREEN}Title:${RESET} $TITLE"
echo -e "${GREEN}Type:${RESET} $TYPE"
echo -e "${GREEN}Priority:${RESET} $PRIORITY"
echo -e "${GREEN}Labels:${RESET} $LABELS"
echo ""

# Create the GitHub issue
if [ -n "$LABELS" ]; then
    ISSUE_URL=$(gh issue create --title "$TITLE" --body "$BODY" --label "$LABELS")
else
    ISSUE_URL=$(gh issue create --title "$TITLE" --body "$BODY")
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Issue created successfully!${RESET}"
    echo -e "${BLUE}🔗 $ISSUE_URL${RESET}"

    # Extract issue number from URL
    ISSUE_NUMBER=$(echo "$ISSUE_URL" | grep -o '[0-9]\+$')
    echo -e "${YELLOW}💡 You can view it with: gh issue view $ISSUE_NUMBER${RESET}"
else
    echo -e "${RED}❌ Failed to create GitHub issue${RESET}"
    exit 1
fi
```

### 2. Executable machen

```bash
chmod +x todo
```

### 3. Alias erstellen (optional)

Füge zu deiner `~/.zshrc` oder `~/.bashrc` hinzu:

```bash
# Für AI Chat Terminal Projekt
alias todo='noglob /Users/martin/Development/ai-chat-terminal/todo'

# Für andere Projekte - passe den Pfad an:
alias todo='noglob ./todo'
```

### 4. GitHub Labels erstellen

```bash
# Benötigte Labels für das AI-System erstellen
gh label create "priority-high" --color "ff0000" --description "High priority issue"
gh label create "priority-medium" --color "ffaa00" --description "Medium priority issue"
gh label create "priority-low" --color "00ff00" --description "Low priority issue"
gh label create "priority-critical" --color "800000" --description "Critical priority issue"
gh label create "memory-system" --color "6f42c1" --description "Related to AI memory system"
gh label create "ui-ux" --color "ff7f00" --description "User interface improvements"
gh label create "performance" --color "ffeb3b" --description "Performance related issues"
gh label create "security" --color "e91e63" --description "Security related issues"
```

## 🎯 Verwendung

### Basic Usage

```bash
# Einfach lostippen - keine Anführungszeichen nötig!
todo Memory sollte alte Nachrichten zusammenfassen
todo Bug: Umlaute werden nicht richtig gespeichert
todo Voice Input wäre cool mit Hotkey
todo Performance bei 1000+ Messages optimieren
```

### Alle Sonderzeichen erlaubt

```bash
todo Können wir Auto-Backup machen? Google Drive oder so!
todo Memory Export: CSV/JSON Format wäre praktisch {wichtig}
todo API-Fehler bei speziellen Zeichen: @#$%^&*()
todo Hotkey Ctrl+M für Memory-Search? Das wär' super!
```

## 🤖 AI-Features

### Automatische Erkennung

Die AI erkennt automatisch:

- **Sprache**: Deutsch → Englisch Übersetzung
- **Issue-Typ**: Bug, Feature, Enhancement, Documentation, Question
- **Priorität**: Low, Medium, High, Critical
- **Labels**: Passende GitHub Labels basierend auf Inhalt
- **Formatierung**: Professionelle GitHub Issue Struktur

### Beispiel-Transformation

**Input:**
```bash
todo Memory wird langsam bei vielen Nachrichten!
```

**AI Output:**
```
Title: Performance degradation with large message count
Type: bug
Priority: high
Labels: bug, performance, memory-system

Body:
## Description
The memory system experiences performance degradation when handling large numbers of messages.

## Use Case
Users with extensive chat histories need consistent performance regardless of message count.

## Technical Details
Performance optimization needed for memory database queries and vector operations.
```

## 🔧 Anpassung für andere Projekte

### 1. Script kopieren

```bash
# Kopiere das todo script in dein neues Projekt
cp /path/to/ai-chat-terminal/todo /path/to/new-project/todo
```

### 2. API Key Pfad anpassen

Ändere in der Datei den Pfad zur OpenAI API Key:

```bash
# Statt AI Chat Terminal config:
ENV_FILE="$AICHAT_DIR/.env"

# Nutze eigene .env Datei:
ENV_FILE="./.env"
# oder
ENV_FILE="$HOME/.openai_api_key"
```

### 3. Labels an Projekt anpassen

Passe die AI-Prompt Labels an dein Projekt an:

```bash
# Beispiel für Web-Projekt:
"Suggest appropriate labels from: bug, enhancement, frontend, backend, api, database, security, ui-ux, performance"

# Beispiel für Mobile App:
"Suggest appropriate labels from: bug, enhancement, ios, android, ui-ux, performance, crash, feature-request"
```

## 📊 GitHub Integration

### Issues verwalten

```bash
# Alle offenen Issues anzeigen
gh issue list

# Issue details anzeigen
gh issue view 42

# Issue schließen
gh issue close 42 --comment "Fixed in v2.1.0"

# Issues filtern
gh issue list --label bug
gh issue list --label priority-high
```

### Workflow-Tipps

1. **Regelmäßig prüfen**: `gh issue list`
2. **Prioritäten setzen**: Labels nutzen
3. **Issues verknüpfen**: In Commits erwähnen `fixes #42`
4. **Templates nutzen**: Konsistente Issue-Struktur durch AI

## 🛠️ Voraussetzungen

- **GitHub CLI**: `brew install gh`
- **GitHub Auth**: `gh auth login`
- **OpenAI API Key**: In `.env` oder `~/.aichat/.env`
- **jq**: JSON parsing (`brew install jq`)
- **curl**: HTTP requests
- **Git Repository**: Muss im Projektverzeichnis ausgeführt werden

## 🎉 Vorteile

- **⚡ Schnell**: Von Idee zu GitHub Issue in Sekunden
- **🎯 Präzise**: AI erstellt professionelle, strukturierte Issues
- **🌍 Multilingual**: Deutsche Ideen, englische Issues
- **🏷️ Organisiert**: Automatische Labels und Prioritäten
- **📱 Überall**: Terminal, aber Issues überall sichtbar
- **👥 Team-Ready**: Andere können Issues sehen und bearbeiten

## 🔧 Troubleshooting

### Häufige Probleme

```bash
# Fehler: Not in git repository
cd /path/to/your/project

# Fehler: GitHub not authenticated
gh auth login

# Fehler: OpenAI API key not found
echo "OPENAI_API_KEY=sk-..." > ~/.aichat/.env

# Fehler: Label not found
gh label create "priority-high" --color "ff0000" --description "High priority"
```

---

**🎯 Entwickelt für AI Chat Terminal - Adaptierbar für jedes Git-Projekt!**

*Erstellt mit Claude Code 🤖*