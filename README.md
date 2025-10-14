# AI Chat Terminal

**Privacy-first terminal chat: OpenAI for general queries, local Qwen 2.5 Coder for private data with direct SQL generation.**

[![Version](https://img.shields.io/badge/version-11.0.9-blue.svg)](https://github.com/martinschenk/ai-chat-terminal)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://github.com/martinschenk/ai-chat-terminal)
[![Encryption](https://img.shields.io/badge/encryption-AES--256-green.svg)](https://github.com/martinschenk/ai-chat-terminal#encryption)
[![AI](https://img.shields.io/badge/AI-Qwen--2.5--Coder-orange.svg)](https://github.com/martinschenk/ai-chat-terminal)

## What is AI Chat Terminal?

A terminal-based chat system that **intelligently routes** your queries:

- **General questions** → OpenAI (GPT-4o) with conversation context
- **Private data** (save/retrieve/delete) → **Local Qwen 2.5 Coder** generates SQL → **Encrypted SQLite**

Your sensitive data **NEVER** leaves your Mac. **96% faster** than v10!

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

**Notice:** All save operations processed by **local Qwen 2.5 Coder**, generates SQL, stores in **encrypted SQLite**. Zero network calls.

### List Your Data (Local DB Query)

```bash
👤 You ▶ list all my data
🤖 AI    🔍 Found 3 items:
           1. test@example.com
           2. 02 July 1998
           3. 1234244332
```

### Retrieve Specific Data (Local DB Search)

```bash
👤 You ▶ show my email
🤖 AI    🔍 test@example.com

👤 You ▶ show my sisters birthday
🤖 AI    🔍 02 July 1998
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

- **Local data keywords** (save/show/delete) → Processed by **Qwen 2.5 Coder** on your Mac
- **SQL generation** → Local Qwen creates SQL queries directly
- **Storage** → Encrypted SQLite (AES-256) in `~/.aichat/memory.db`
- **Zero network calls** for private data operations

### 🧠 Smart Context

- OpenAI maintains conversation history
- Ask follow-up questions naturally
- Context-aware responses

### 🌍 Multilingual

- **Supported:** English, German, Spanish
- Keywords work in all 3 languages:
  - EN: `save`, `show`, `delete`
  - DE: `speichere`, `zeig`, `lösche`
  - ES: `guarda`, `muestra`, `borra`

### 🎯 Smart Pattern Matching (v11.0.9)

**Problem Solved:** Ambiguity between questions and statements
- ❌ OLD: "what is my email?" vs "my email is test@test.com" → both had "is" + "my"
- ✅ NEW: Pattern `{x}` = any word → precise matching for ANY data type

**Pattern Examples:**
```bash
# Pattern: "my {x} is" → Matches SAVE for ANY data type
✅ "my email is test@test.com"        → SAVE
✅ "my API key is sk-123"             → SAVE
✅ "my crypto wallet is 0x123..."     → SAVE
✅ "my birthday is March 15, 1990"    → SAVE

# Pattern: "what is my {x}" → Matches RETRIEVE for ANY data type
✅ "what is my email?"                → RETRIEVE
✅ "what is my API key?"              → RETRIEVE
✅ "what is my crypto wallet?"        → RETRIEVE

# Single words still work!
✅ "save test@test.com"               → SAVE
✅ "show data"                        → RETRIEVE
✅ "delete everything"                → DELETE
```

**Benefits:**
- 🚀 **Future-proof:** New data types automatically supported without keyword updates
- 🎯 **Precise:** Solves ambiguity - "what is my X?" vs "my X is Y"
- 🌍 **Multilingual:** Patterns work in EN/DE/ES
- 💪 **Flexible:** Mix of patterns + good generic single words

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

## Version History

### v11.0.9 (Current) - Smart Pattern Keywords

**🎯 Intelligent keyword matching with {x} placeholders!**

**What's New:**
- ✅ **Pattern keywords:** `my {x} is`, `what is my {x}`, `delete my {x}` → works for ANY data type
- ✅ **Solves ambiguity:** "what is my email?" vs "my email is test@test.com" now correctly identified
- ✅ **Future-proof:** New data types (API keys, crypto wallets, etc.) automatically supported
- ✅ **Maintains single words:** Good generic keywords (save, show, delete) still work
- ✅ **Multilingual patterns:** EN/DE/ES all use same flexible system

**Examples:**
```
"my API key is sk-123"        → SAVE (pattern: my {x} is)
"what is my crypto wallet?"   → RETRIEVE (pattern: what is my {x})
"delete my password"          → DELETE (pattern: delete my {x})
```

### v11.0.0 - KISS SQL Architecture

**🚀 RADICAL SIMPLIFICATION - 1528 lines removed!**

**Major Changes:**
- ✅ **Qwen 2.5 Coder** replaces Llama 3.2 - generates SQL directly!
- ✅ **96% faster queries** - Direct SQL vs vector search
- ✅ **90-95% SQL accuracy** - Up from 70% in v10
- ✅ **1528 lines removed** - Much simpler codebase
- ✅ **No vector DB** - Removed sentence-transformers, sqlite-vec
- ✅ **Simple schema** - 5 fields instead of complex metadata

**Performance:**
- **SAVE:** 1500ms → 800ms (47% faster)
- **RETRIEVE:** 1200ms → 50ms (96% faster!)
- **DELETE:** 1000ms → 80ms (92% faster)

**Removed:**
- ❌ Vector database (sentence-transformers, E5 embeddings)
- ❌ PII classification system (~400 lines)
- ❌ Llama data extraction (~340 lines)
- ❌ Complex action handlers (~300 lines)

### v10.3.0 - KISS Architecture Simplification
- Merged LIST into RETRIEVE
- Extended keywords (3x more variations)
- FALSE_POSITIVE routing to OpenAI

### v10.1.0 - Llama 3.2 Migration
- Migrated from Phi-3 to Llama 3.2 (3B)
- Simplified to 3 languages (EN, DE, ES)
- Context-aware prompts

---

**Questions?** Open an issue on [GitHub](https://github.com/martinschenk/ai-chat-terminal/issues)

**Ready to try v11.0.0?**
```bash
curl -fsSL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | zsh
```
