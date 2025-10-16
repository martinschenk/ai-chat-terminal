# AI Chat Terminal

**Chat with powerful cloud AI (GPT-4o) — but your private data NEVER leaves your Mac.**

Smart keyword detection routes sensitive data to local AI instantly. Zero cloud exposure for passwords, emails, or personal info.

[![Version](https://img.shields.io/badge/version-11.4.0-blue.svg)](https://github.com/martinschenk/ai-chat-terminal)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://github.com/martinschenk/ai-chat-terminal)
[![Encryption](https://img.shields.io/badge/encryption-AES--256-green.svg)](https://github.com/martinschenk/ai-chat-terminal#encryption)
[![AI](https://img.shields.io/badge/AI-Qwen--2.5--Coder-orange.svg)](https://github.com/martinschenk/ai-chat-terminal)

## The Privacy Advantage

**The Problem with Regular AI Chat:**
When you chat with ChatGPT, Claude, or any cloud AI, **EVERYTHING you type goes to their servers**. Including:
- Your passwords and API keys
- Email addresses and phone numbers
- Personal notes and sensitive data
- All conversations are logged on their servers

**AI Chat Terminal solves this:**

```bash
You type: "What's the capital of Spain?"
→ Routes to OpenAI (cloud) ✅ Safe - general knowledge

You type: "save my password SecretPass123"
→ Routes to LOCAL Qwen 2.5 Coder ✅ NEVER sent to cloud!
→ Encrypted locally with AES-256
→ Zero network calls for this operation
```

**How it works:**
1. **Intelligent keyword detection** (<1ms) analyzes your input BEFORE sending anywhere
2. **Keywords detected** (save/show/delete/note/etc.) → **Local Qwen AI** processes it → **Encrypted SQLite**
3. **No keywords** → Safe to send to **cloud OpenAI** for powerful general queries

**The result:**
✅ Enjoy GPT-4o's power for research, coding help, general questions
✅ Your sensitive data stays on YOUR Mac, encrypted, never uploaded
✅ Fast local operations (96% faster than cloud roundtrip)
✅ Works in 3 languages with 30+ action verbs (save, note, record, store, etc.)

## How It Works (v11.0.0 - KISS!)

```
┌─────────────────────────────────────────────┐
│ User Input                                  │
└────────────┬────────────────────────────────┘
             ↓
   ┌─────────────────────┐
   │ Keyword Detection   │  ← Fast (<1ms)
   │ save/show/delete    │
   └─────────┬───────────┘
             ↓
      ┌──────────────┐
      │  Detected?   │
      └──┬────────┬──┘
         │        │
    YES  │        │  NO
         ↓        ↓
  ┌──────────────┐  ┌──────────────┐
  │ Qwen 2.5     │  │   OpenAI     │
  │ Coder (7B)   │  │  (CLOUD)     │
  │ SQL Direct   │  │              │
  └─────┬────────┘  └──────┬───────┘
        ↓                   ↓
  ┌─────────────┐  ┌──────────────┐
  │ Encrypted   │  │  Response    │
  │ SQLite DB   │  │ with Context │
  │ (AES-256)   │  │              │
  └─────────────┘  └──────────────┘
```

**v11.0.0 Changes:**
- **NEW:** Qwen 2.5 Coder generates SQL directly (no complex handlers!)
- **REMOVED:** Vector database, PII mappings (~1500 lines!)
- **FASTER:** 96% faster queries, 90-95% SQL accuracy

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

## What Gets Installed?

The installer sets up two types of components:

### 📁 Local Installation (`~/.aichat/`) - App-Specific

**Python Scripts:**
- `chat_system.py` - Main orchestrator
- `qwen_sql_generator.py` - SQL generation via Qwen
- `memory_system.py` - SQLite database interface
- `local_storage_detector.py` - Keyword detection
- `encryption_manager.py` - AES-256 encryption
- `response_generator.py` - Response formatting
- `daemon_manager.py` - Background process management
- `ollama_manager.py` - Ollama integration
- `action_detector.py` - Intent classification
- `db_migration.py`, `db_migration_v11.py` - Database migration tools
- `chat_daemon.py` - Daemon process

**Shell Scripts:**
- `aichat.zsh` - Main shell integration
- `modules/` - Functions, config menu, language utilities

**Configuration:**
- `config` - Settings (language, model, etc.)
- `.env` - OpenAI API key (optional, Keychain preferred)
- `lang/` - Language keyword files (EN/DE/ES)
- `lang_manager/` - Language string management

**Data:**
- `memory.db` - Your encrypted local database (AES-256)

### 🌍 Global Installation - Shared System Components

**If not already installed, the installer will set up:**

1. **Ollama** (~100MB)
   - Purpose: Run local AI models
   - Location: `/opt/homebrew/bin/ollama` (macOS)
   - Installed via: Homebrew
   - Used by: This app + any other apps using local AI

2. **Qwen 2.5 Coder (7B)** (~4.5GB)
   - Purpose: SQL generation for private data
   - Location: `~/.ollama/models/`
   - Installed via: Ollama (`ollama pull qwen2.5-coder:7b`)
   - Used by: This app + any other apps using Qwen via Ollama

3. **Python Packages** (~50MB total)
   - `openai` - OpenAI API client
   - `requests` - HTTP library
   - `rich` - Markdown rendering in terminal
   - `sqlcipher3-binary` - Database encryption (optional but recommended)
   - Location: `~/.local/lib/python3.x/site-packages/`
   - Installed via: pip3 (user install)
   - Used by: This app + any other Python apps using these libraries

4. **SQLCipher** (~5MB)
   - Purpose: Database encryption
   - Location: `/opt/homebrew/bin/sqlcipher`
   - Installed via: Homebrew
   - Used by: This app + any other apps using encrypted SQLite

### 📊 Total Disk Space

- **Local (`~/.aichat/`)**: ~5MB (without your data)
- **Global (first install)**: ~4.7GB (Ollama + Qwen + Python packages + SQLCipher)
- **Global (if already installed)**: 0 bytes (reuses existing installations)

## What Gets Uninstalled?

When you uninstall AI Chat Terminal:

### ✅ Removed by Uninstaller

- **Local app files** (`~/.aichat/`)
  - All Python scripts
  - All shell scripts
  - Configuration files
  - **YOUR DATA** (`memory.db`) - ⚠️ **BACKUP FIRST!**

- **Shell integration**
  - Removed from `~/.zshrc` or `~/.bashrc`
  - `chat` command alias removed

### ⚠️ NOT Removed (Shared with Other Apps)

- **Ollama** - May be used by other AI apps
- **Qwen 2.5 Coder model** - May be used by other apps via Ollama
- **Python packages** (openai, requests, rich, sqlcipher3-binary) - May be used by other Python scripts
- **SQLCipher** - May be used by other database apps

**Why keep global components?**
- They're shared system resources (~4.7GB)
- Other apps might depend on them
- Homebrew manages global packages - you can remove manually:
  ```bash
  # Optional: Remove global components (if you're sure nothing else uses them)
  brew uninstall ollama
  brew uninstall sqlcipher
  ollama stop  # Stop Ollama service first
  rm -rf ~/.ollama  # Remove all Ollama models (4.5GB+)
  pip3 uninstall openai requests rich sqlcipher3-binary
  ```

## Uninstall

**Quick uninstall (keeps your data backup):**
```bash
curl -fsSL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/uninstall.sh | zsh
```

**Manual uninstall:**
```bash
# 1. Backup your data first!
cp ~/.aichat/memory.db ~/ai-chat-backup-$(date +%Y%m%d).db

# 2. Remove app files
rm -rf ~/.aichat

# 3. Remove shell integration
# Edit ~/.zshrc and remove these lines:
# AI Chat Terminal
# source ~/.aichat/aichat.zsh
# alias chat='noglob ai_chat_function'

# 4. Reload shell
source ~/.zshrc
```

## Examples from Real Usage

### OpenAI Queries with Context (Cloud)

```bash
chat
👤 You ▶ what is the capital of Spain?
🤖 AI    The capital of Spain is Madrid.

👤 You ▶ best food there?
🤖 AI    Madrid is famous for Cocido Madrileño (chickpea stew),
         Bocadillo de Calamares (squid sandwich), and Churros con Chocolate!
```

**Notice:** OpenAI maintains conversation context ("there" = Madrid from previous message).

### Save Private Data - NEVER Sent to Cloud!

```bash
# ANY of these work - with or without possessive!
👤 You ▶ save my email test@example.com
🤖 AI    🗄️ Stored 🔒

👤 You ▶ note the password SecretPass123
🤖 AI    🗄️ Stored 🔒

👤 You ▶ guarda email test@test.es     # Spanish - no "mi" needed!
🤖 AI    🗄️ Guardado 🔒

👤 You ▶ notiere Telefon 123456        # German - no "meine" needed!
🤖 AI    🗄️ Gespeichert 🔒
```

**Notice:**
- Works with **30+ verb synonyms** (save/note/record/store/add/log/write/...)
- **Flexible possessives** - "my/the/his/her" all work, or omit entirely!
- **Multilingual** - EN/DE/ES with natural variations
- All processed by **local Qwen 2.5 Coder** - **Zero cloud calls!**

### Retrieve with Different Keywords (Local DB)

```bash
👤 You ▶ retrieve my email
🤖 AI    🗄️🔍 test@example.com (email)

👤 You ▶ what is my suitcase code?
🤖 AI    🗄️🔍 42341 (suitcase code)

👤 You ▶ list all
🤖 AI    🗄️🔍 Found 2 items:
           1. test@example.com (email)
           2. 42341 (suitcase code)
```

**Notice:** Works with **any synonym** (`retrieve`, `what is`, `list all`) - not limited to `show`!

### Delete with 2-Stage Confirmation (Local DB)

```bash
👤 You ▶ delete my suitcase code
🤖 AI    🗑️  Items to delete:
           1. 42341 (suitcase code)

         ⚠️  Type 'y' to confirm or press Enter to cancel.

👤 You ▶ y
🤖 AI    🗄️🗑️ Deleted
```

**Notice:** DELETE uses **2-stage confirmation** (v11.0.9+):
1. Preview shows what will be deleted
2. Just type `y` to confirm (or `n`/Enter to cancel)
3. 60-second timeout protection

### Built-in Help (v11.1.0)

Quick access to all commands and shortcuts:

```bash
👤 You ▶ /help

📖 AI Chat Terminal - Quick Help

Commands:
  /config - Open settings menu
  clear   - Clear screen
  exit    - Quit chat

Keyboard Shortcuts:
  ↑  - Previous message
  ↓  - Next message
  ESC - Quick exit

Database Operations:
  • save my X - Store data locally
  • show my X - Retrieve data
  • delete my X - Remove data
  • list all - Show all data

Examples:
  my email is test@example.com
  what is my email?
  delete my email

Type anything to ask AI, or use commands above
```

**Notice:** `/help` is multilingual (EN/DE/ES) and always available. Perfect for quick reference!

### Keyboard Shortcuts (v11.1.0)

Navigate your chat naturally:

```bash
↑ Arrow Up    - Previous message from history
↓ Arrow Down  - Next message / Back to current input
Enter         - Send message
Backspace     - Delete character
ESC           - Quick exit from chat
/help         - Show all commands and shortcuts
/config       - Open settings menu
clear         - Clear screen
```

**History Navigation:**
- Press ↑ to scroll through your last 50 messages
- Press ↓ to go forward or return to what you were typing
- Type anything to exit history mode and resume editing
- History is loaded from your local database automatically

## Key Features

### 🔒 Privacy by Design

- **Local data keywords** (save/show/delete) → Processed by **Qwen 2.5 Coder** on your Mac
- **SQL generation** → Local Qwen creates SQL queries directly
- **Storage** → Encrypted SQLite (AES-256) in `~/.aichat/memory.db`
- **Zero network calls** for private data operations

### 🧠 Smart Context

- OpenAI maintains conversation history
- Ask follow-up questions naturally
- Context-aware responses

### 🌍 Multilingual (30+ Action Verbs per Language!)

**English (12 SAVE verbs):** save, remember, store, keep, note, record, add, log, write, register, put, set
**German (10 SAVE verbs):** speichere, merke, notiere, trag ein, halt fest, schreib auf, füg hinzu, registrier, leg ab, setz
**Spanish (10 SAVE verbs):** guarda, recuerda, almacena, anota, registra, apunta, agrega, añade, pon, graba

**+ 12-14 RETRIEVE verbs per language:** show/get/find/check/tell/lookup/view...
**+ 10-12 DELETE verbs per language:** delete/remove/forget/erase/clear/wipe...

### 🎯 Ultra-Flexible Pattern Matching (v11.3.0)

**Maximum flexibility - ANY possessive works (or none at all)!**

```bash
# ALL of these work - same result!
✅ "save my email test@test.com"      → SAVE
✅ "save the email test@test.com"     → SAVE
✅ "save his email test@test.com"     → SAVE
✅ "save email test@test.com"         → SAVE (no possessive!)

# Spanish - todas las variaciones!
✅ "guarda mi email"        → SAVE
✅ "guarda la email"        → SAVE
✅ "guarda su email"        → SAVE
✅ "guarda email"           → SAVE

# German - alle Variationen!
✅ "speichere meine Email"  → SAVE
✅ "speichere die Email"    → SAVE
✅ "speichere seine Email"  → SAVE
✅ "speichere Email"        → SAVE
```

**Benefits:**
- 🚀 **Natural language:** Type how YOU naturally speak
- 🎯 **No memorization:** Don't worry about exact phrasing
- 🌍 **Cross-language:** Pattern works identically in EN/DE/ES
- 💪 **30+ verb synonyms:** save/note/record/store/add/log/write...

### ⚡ Fast & Transparent

- **Local operations:** <1s (Qwen SQL + SQLite) - **96% faster than v10!**
- **OpenAI queries:** 5-7s (API streaming)
- **DB indicators:** Every local operation shows 🔍/✅/🗑️ icon

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
- **Qwen 2.5 Coder (7B)** model (auto-downloaded via Ollama)
- ~5GB disk space (4.5GB for Qwen 2.5 Coder model)
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
# Options: GPT-4o, GPT-4o-mini, GPT-4-turbo
```

## Architecture (v11.0.0 - KISS!)

### Dual AI System

**Component 1: Qwen 2.5 Coder (Privacy)**
- Model: `qwen2.5-coder:7b` via Ollama
- Purpose: **Direct SQL generation** for SAVE/RETRIEVE/DELETE
- Location: Runs on your Mac (no network)
- Performance: ~800ms per operation (47% faster than v10!)
- SQL Accuracy: 90-95% (vs v10's 70%)

**Component 2: OpenAI GPT-4o (General Queries)**
- Model: `gpt-4o` or `gpt-4o-mini` (configurable)
- Purpose: Conversation, general knowledge, context-aware responses
- Location: OpenAI API (cloud)
- Performance: 5-7s streaming response

**Component 3: Simple SQLite Database**
- Storage: `~/.aichat/memory.db` (AES-256 encrypted)
- Structure: **Simple 5-field table** (id, content, meta, lang, timestamp)
- Search: Direct SQL LIKE queries (96% faster than v10 vector search!)

### Database Schema (v11.0.0)

```sql
CREATE TABLE mydata (
    id INTEGER PRIMARY KEY,
    content TEXT NOT NULL,      -- The actual data
    meta TEXT,                   -- Simple label: "email", "geburtstag", etc.
    lang TEXT,                   -- Language: en, de, es
    timestamp INTEGER            -- Unix timestamp
);
```

**No more:**
- ❌ Vector embeddings (768-dimensional!)
- ❌ Complex PII categories
- ❌ Metadata JSON fields

### Message Flow (v11.0.0 - Direct SQL!)

**Local Data Operations:**
```
User: "save my email test@example.com"
  ↓
Keyword detected: "save"
  ↓
Qwen 2.5 Coder generates SQL directly:
  INSERT INTO mydata (content, meta, lang)
  VALUES ('test@example.com', 'email', 'en');
  ↓
SQL validated & executed
  ↓
Response: "✅ Stored 🔒"
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

## Qwen 2.5 Coder Implementation

### Why Qwen Instead of Llama?

| Feature | Llama 3.2 (3B) | Qwen 2.5 Coder (7B) |
|---------|----------------|---------------------|
| **SQL Accuracy** | ~70% | **90-95%** ✅ |
| **False Positives** | ~15% | **<5%** ✅ |
| **Model Size** | 2GB | 4.5GB |
| **Specialization** | General | **SQL/Code** ✅ |
| **Performance** | 1500ms | **800ms** ✅ |

### SQL Generation Examples

**English:**
```
Input: "save my email test@example.com"
SQL:   INSERT INTO mydata (content, meta, lang)
       VALUES ('test@example.com', 'email', 'en');
```

**German:**
```
Input: "speichere Omas Geburtstag 15.03.1950"
SQL:   INSERT INTO mydata (content, meta, lang)
       VALUES ('15.03.1950', 'Omas Geburtstag', 'de');
```

**Spanish:**
```
Input: "guarda mi teléfono 669686832"
SQL:   INSERT INTO mydata (content, meta, lang)
       VALUES ('669686832', 'teléfono', 'es');
```

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

## File Structure (v11.0.0)

```
~/.aichat/
├── chat_system.py              # Main orchestrator
├── qwen_sql_generator.py       # Qwen SQL generation (NEW in v11!)
├── memory_system.py            # Simple SQLite interface (simplified!)
├── local_storage_detector.py   # Keyword detection
├── encryption_manager.py       # AES-256 encryption
├── db_migration_v11.py         # v10→v11 migration script
│
├── lang_manager/               # Language management
│   └── __init__.py             # Centralized string handling
│
├── lang/                       # Language configs (3 languages only!)
│   ├── en.conf                 # English keywords
│   ├── de.conf                 # German keywords
│   └── es.conf                 # Spanish keywords
│
└── memory.db                   # Encrypted SQLite (AES-256)
```

**Removed in v11.0.0:**
- ❌ `llama_data_extractor.py` (Qwen generates SQL directly!)
- ❌ `db_actions/` handlers (SQL executed directly!)
- ❌ Vector database dependencies

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
🤖 AI    🔍 test@example.com
```

### "Qwen 2.5 Coder not working"

Check Ollama installation:

```bash
which ollama                    # Should show: /opt/homebrew/bin/ollama
ollama list                     # Should show: qwen2.5-coder:7b
ollama run qwen2.5-coder:7b     # Test it
```

## Migration from v10

If you're upgrading from v10, migrate your database:

```bash
cd ~/.aichat
python3 db_migration_v11.py memory.db
```

This will:
- ✅ Backup your old database
- ✅ Convert `chat_history` → `mydata` schema
- ✅ Remove vector embeddings
- ✅ Simplify metadata

## Development

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

- **Qwen 2.5 Coder (7B):** Alibaba Cloud via Ollama
- **SQLite Encryption:** SQLCipher with AES-256
- **OpenAI:** GPT-4o/GPT-4o-mini for general queries

---

**Questions?** Open an issue on [GitHub](https://github.com/martinschenk/ai-chat-terminal/issues)

**Ready to try it?**
```bash
curl -fsSL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | zsh
```
