# AI Chat Terminal

**Privacy-first terminal chat: OpenAI for general queries, local Llama 3.2 for private data.**

[![Version](https://img.shields.io/badge/version-10.3.0-blue.svg)](https://github.com/martinschenk/ai-chat-terminal)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://github.com/martinschenk/ai-chat-terminal)
[![Encryption](https://img.shields.io/badge/encryption-AES--256-green.svg)](https://github.com/martinschenk/ai-chat-terminal#encryption)
[![AI](https://img.shields.io/badge/AI-Llama--3.2-orange.svg)](https://github.com/martinschenk/ai-chat-terminal)

## What is AI Chat Terminal?

A terminal-based chat system that **intelligently routes** your queries:

- **General questions** → OpenAI (GPT-4o) with conversation context
- **Private data** (save/retrieve/list/delete) → **Local Llama 3.2** + **Encrypted SQLite**

Your sensitive data **NEVER** leaves your Mac.

## How It Works

```
┌─────────────────────────────────────────────┐
│ User Input                                  │
└────────────┬────────────────────────────────┘
             ↓
   ┌─────────────────────┐
   │ Keyword Detection   │  ← Fast (<1ms)
   │ save/show/retrieve/ │
   │ delete keywords     │
   └─────────┬───────────┘
             ↓
      ┌──────────────┐
      │  Detected?   │
      └──┬────────┬──┘
         │        │
    YES  │        │  NO
         ↓        └──────────────┐
  ┌──────────┐                   │
  │ Llama 3.2│                   │
  │ (LOCAL)  │                   │
  │ ~1000ms  │                   │
  └─────┬────┘                   │
        ↓                        │
  ┌─────────────────┐            │
  │ FALSE_POSITIVE? │            │
  └──┬──────────┬───┘            │
     │          │                │
   YES│          │NO              │
     │          ↓                ↓
     │    ┌─────────────┐  ┌──────────────┐
     │    │ Encrypted   │  │   OpenAI     │
     │    │ SQLite DB   │  │  (CLOUD)     │
     │    │ (AES-256)   │  │   5-7s       │
     │    └─────────────┘  └──────┬───────┘
     │                             │
     └─────────────────────────────┤
                                   ↓
                          ┌──────────────┐
                          │  Response    │
                          │ with Context │
                          └──────────────┘
```

**3-Phase System:**
1. **Keyword Check** (<1ms) - Detects SAVE/RETRIEVE/DELETE from lang/*.conf
2. **Llama Classification** (~1000ms) - Validates action + detects false positives
3. **Routing:**
   - Valid action → **Encrypted SQLite** (local)
   - False positive → **OpenAI** (cloud)
   - No keywords → **OpenAI** (cloud)

## Quick Start

**Install (one command):**
```bash
curl -fsSL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | zsh
```

**Reload shell:**
```bash
source ~/.zshrc
```

**Start chatting:**
```bash
chat
```

## Examples from Real Usage

### Save Private Data (Local Only - Never to OpenAI)

```bash
chat
👤 You ▶ save my email address test@example.com
🤖 AI    ✅ Stored 🔒

👤 You ▶ save my sisters birthday 02 July 1998
🤖 AI    ✅ Stored 🔒

👤 You ▶ save my phone 1234244332
🤖 AI    ✅ Stored 🔒
```

**Notice:** All save operations processed by **local Llama 3.2**, stored in **encrypted SQLite**. Zero network calls.

### List Your Data (Local DB Query)

```bash
👤 You ▶ list all my data
🤖 AI    📦 Your data (3):
           1. sisters birthday: 02 July 1998
           2. phone: 1234244332
           3. email: test@example.com
```

### Retrieve Specific Data (Local DB Search)

```bash
👤 You ▶ show my email
🤖 AI    🔍 email: test@example.com

👤 You ▶ show my sisters birthday
🤖 AI    🔍 sisters birthday: 02 July 1998
```

### Delete Data (Local DB)

```bash
👤 You ▶ delete my phone
🤖 AI    🗑️ Deleted (1)
```

### OpenAI Queries with Context (Cloud)

```bash
👤 You ▶ what is the capital of Germany?
🤖 AI    The capital of Germany is Berlin.

👤 You ▶ best dish of this country
🤖 AI    One of the most iconic German dishes is Sauerbraten,
         a pot roast marinated for days in a mixture of wine,
         vinegar, and spices...
```

**Notice:** OpenAI maintains conversation context ("this country" = Germany from previous message).

## Key Features

### 🔒 Privacy by Design

- **Local data keywords** (save/show/list/delete) → Processed by **Llama 3.2** on your Mac
- **Data extraction** → Local Llama parsing (no cloud)
- **Storage** → Encrypted SQLite (AES-256) in `~/.aichat/memory.db`
- **Zero network calls** for private data operations

### 🧠 Smart Context

- OpenAI maintains conversation history
- Ask follow-up questions naturally
- Context-aware responses

### 🌍 Multilingual

- **Supported:** English, German, Spanish
- Keywords work in all 3 languages:
  - EN: `save`, `show`, `list`, `delete`
  - DE: `speichere`, `zeig`, `liste`, `lösche`
  - ES: `guarda`, `muestra`, `lista`, `borra`

### ⚡ Fast & Transparent

- **Local operations:** <2s (Llama + SQLite)
- **OpenAI queries:** 5-7s (API streaming)
- **DB indicators:** Every local operation shows 🔍/💾/🗑️/📦 icon

### 🔐 Encryption

- **Algorithm:** SQLCipher with AES-256-CBC
- **Key storage:** macOS Keychain (automatic)
- **Key derivation:** PBKDF2-HMAC-SHA512, 64,000 iterations
- **Zero configuration** required

## System Requirements

- macOS 12.0+ (Monterey or later)
- Zsh shell
- Python 3.9+
- **Ollama** (auto-installed)
- **Llama 3.2 (3B)** model (auto-downloaded via Ollama)
- ~4GB disk space (3.5GB for Llama 3.2 model)
- 8GB RAM minimum (16GB recommended)
- OpenAI API key

## Configuration

### API Key

**Option A - Automatic (during installation):**
```bash
# Installer checks macOS Keychain for OpenAI API key
# Service: "OpenAI API", Account: "openai"
```

**Option B - Manual:**
```bash
echo 'OPENAI_API_KEY=sk-...' > ~/.aichat/.env
```

### Change Language

```bash
chat
Type: /config → [2] Change language → Select: EN/DE/ES
```

### Change AI Model

```bash
chat
Type: /config → [5] Change AI model
# Options: GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-3.5-turbo
```

## Architecture

### Dual AI System

**Component 1: Local Llama 3.2 (Privacy)**
- Model: `llama3.2:3b` via Ollama
- Purpose: Data extraction for SAVE/RETRIEVE/DELETE/LIST
- Location: Runs on your Mac (no network)
- Performance: ~500-1500ms per operation

**Component 2: OpenAI GPT-4o (General Queries)**
- Model: `gpt-4o` or `gpt-4o-mini` (configurable)
- Purpose: Conversation, general knowledge, context-aware responses
- Location: OpenAI API (cloud)
- Performance: 5-7s streaming response

**Component 3: Encrypted SQLite**
- Storage: `~/.aichat/memory.db` (AES-256)
- Structure: Simple 3-field table (id, timestamp, content)
- Search: LIKE-based matching (fast, simple)

### Message Flow

**Local Data Operations:**
```
User: "save my email test@example.com"
  ↓
Keyword detected: "save"
  ↓
Llama 3.2 extracts: "email: test@example.com"
  ↓
Saved to encrypted SQLite
  ↓
Response: "✅ Gespeichert 🔒"
```

**OpenAI Queries:**
```
User: "what is the capital of Germany?"
  ↓
No keywords detected
  ↓
Send to OpenAI API (with conversation history)
  ↓
Response: "The capital of Germany is Berlin."
  ↓
Context stored for follow-up questions
```

## Llama 3.2 Implementation

### Prompt Structure

All Llama prompts follow this context-aware format:

```
Example 1:
User wants to: SAVE
User said: save my email address test@example.com
Extract: email address: test@example.com

Example 2:
User wants to: SAVE
User said: speichere meine Email test@test.de
Extract: Email: test@test.de

Example 3:
User wants to: SAVE
User said: guarda mi correo test@ejemplo.es
Extract: correo: test@ejemplo.es

... (7 examples total per action)

Now extract:
User wants to: SAVE
User said: {user_input}
Extract:
```

### Data Extraction

Llama 3.2 extracts data in format: `description: value`

**Examples:**
- `save my email test@example.com` → `email: test@example.com`
- `speichere Omas Geburtstag 15.03.1950` → `Omas Geburtstag: 15.03.1950`
- `guarda mi teléfono 669686832` → `teléfono: 669686832`

### Multilingual Examples

Each Llama prompt contains **7 examples** mixing EN/DE/ES:
- Examples 1-3: English
- Examples 4-5: German
- Examples 6-7: Spanish

This ensures robust multilingual support.

### Method Tracking

Handlers track extraction method:
- `[via llama]` - Llama 3.2 extracted data successfully
- `[via regex]` - Fallback regex extraction used
- `[via fallback]` - No extraction, using raw input

## Security

### What's Protected ✅

- **Physical theft:** Database file is useless without Keychain key
- **File-level access:** Other users can't read your data
- **Backup theft:** Copied DB files remain encrypted
- **Disk forensics:** Data is encrypted at rest

### What's NOT Protected ⚠️

- **Malware as user:** Apps running as your user can access Keychain
- **Root/admin access:** System administrators can extract keys
- **Memory dumps:** Data is decrypted in RAM during use

### Recommendations

1. **Enable FileVault:** Full-disk encryption adds another layer
2. **Use strong Mac password:** Keychain security depends on your login
3. **Keep software updated:** Security patches are critical
4. **Don't sync DB unencrypted:** Be cautious with cloud sync

## File Structure

```
~/.aichat/
├── chat_system.py              # Main orchestrator
├── action_detector.py          # Keyword detection (SAVE/RETRIEVE/LIST/DELETE)
├── llama_data_extractor.py     # Llama 3.2 data extraction (NEW in v10)
├── memory_system.py            # Encrypted SQLite interface
├── response_generator.py       # Response formatting
│
├── db_actions/                 # Action handlers
│   ├── save_handler_v10.py     # SAVE operations
│   ├── retrieve_handler_v10.py # RETRIEVE operations
│   ├── delete_handler_v10.py   # DELETE operations
│   └── list_handler_v10.py     # LIST operations
│
├── lang_manager/               # Language management
│   └── __init__.py             # Centralized string handling
│
├── lang/                       # Language configs
│   ├── en.conf                 # English keywords
│   ├── de.conf                 # German keywords
│   └── es.conf                 # Spanish keywords
│
└── memory.db                   # Encrypted SQLite (AES-256)
```

## Troubleshooting

### "Keyword not detected"

Use exact keywords for your language:

```bash
✅ EN: "save my email test@example.com"
✅ DE: "speichere meine Email test@test.de"
✅ ES: "guarda mi correo test@ejemplo.es"

❌ "store my email test@example.com"  # Wrong keyword
```

### "No data found in DB"

Data must be saved first:

```bash
# Step 1: Save
👤 You ▶ save my email test@example.com
🤖 AI    ✅ Stored 🔒

# Step 2: Retrieve
👤 You ▶ show my email
🤖 AI    🔍 email: test@example.com
```

### "Llama 3.2 not working"

Check Ollama installation:

```bash
which ollama           # Should show: /opt/homebrew/bin/ollama
ollama list            # Should show: llama3.2:3b
ollama run llama3.2:3b # Test it
```

## Development

### Testing

```bash
cd ~/.aichat
python3 test_v10_handlers.py
```

### Update from Git

```bash
cd ~/Development/ai-chat-terminal
git pull origin main
./install.sh
source ~/.zshrc
```

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Credits

- **Llama 3.2 (3B):** Meta AI via Ollama
- **Memory System:** `intfloat/multilingual-e5-base` (legacy, not used in v10)
- **Vector Database:** SQLite with encryption (SQLCipher)
- **OpenAI:** GPT-4o/GPT-4o-mini for general queries

## Version

**Current:** v10.3.0 - KISS Architecture Simplification

**Changes in v10.3.0:**
- ✅ **Merged LIST into RETRIEVE** - One handler for all retrieval (1 item or all items)
- ✅ **Removed hardcoded limit=10** - Shows ALL matching results
- ✅ **4 Actions instead of 5** - SAVE, RETRIEVE, DELETE, FALSE_POSITIVE
- ✅ **Extended keywords** - 3x more keyword variations per language
  - EN: Added `record`, `memorize`, `log`, `track`, `add`, `put`, `tell me`, `give me`, `search`, `fetch`, etc.
  - DE: Added `protokolliere`, `füge hinzu`, `sag mir`, `gib mir`, `such`, etc.
  - ES: Added `registra`, `memoriza`, `añade`, `dime`, `busca`, etc.
- ✅ **FALSE_POSITIVE routing** - Llama validates actions, routes false positives to OpenAI
- ✅ **Smart result formatting** - Single result inline, multiple results as numbered list
- ✅ **Updated architecture diagram** - Shows complete flow with false-positive feedback loop

**Changes in v10.1.0:**
- ✅ Migrated from Phi-3 to **Llama 3.2 (3B)**
- ✅ Simplified to **3 languages** (EN, DE, ES)
- ✅ Context-aware prompts: "User wants to: ACTION / User said: ... / Extract: ..."
- ✅ Multilingual examples (7 per action, mixed EN/DE/ES)
- ✅ Method tracking (`[via llama]`, `[via regex]`, `[via fallback]`)
- ✅ Output cleaning (removes Llama's explanatory text)
- ✅ Tuple returns for extraction tracking
- ✅ KISS principle: Simple, reliable, maintainable

---

**Questions?** Open an issue on [GitHub](https://github.com/martinschenk/ai-chat-terminal/issues)

**Ready to try it?**
```bash
curl -fsSL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | zsh
```
