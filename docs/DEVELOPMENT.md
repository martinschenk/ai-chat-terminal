# AI Chat Terminal - Project Context for Claude Code

## Project Purpose

Privacy-first terminal chat that intelligently routes queries:
- **General questions** → OpenAI (GPT-4o)
- **Private data** (detected by keywords) → Local Qwen 2.5 Coder → Encrypted SQLite

User's sensitive data NEVER leaves their Mac.

## Current Version

v11.6.0 - Privacy First: Auto-delete chat history on exit and after inactivity

## Key Architecture

### Routing System
1. **Keyword Detection** (<1ms) - Checks for save/show/delete verbs in EN/DE/ES
2. **Match** → Local Qwen 2.5 Coder generates SQL → Encrypted SQLite
3. **No match** → OpenAI (cloud) for general queries

### Core Files
- `chat_system.py` - Main orchestrator with keyword routing
- `qwen_sql_generator.py` - SQL generation via Qwen 2.5 Coder (7B)
- `memory_system.py` - SQLite interface with AES-256 encryption
- `local_storage_detector.py` - Keyword detection with pattern matching
- `lang/*.conf` - Language-specific keywords (EN/DE/ES)

### Database Schema
```sql
CREATE TABLE mydata (
    id INTEGER PRIMARY KEY,
    content TEXT NOT NULL,  -- The actual data
    meta TEXT,              -- Label: "email", "password", etc.
    lang TEXT,              -- Language: en, de, es
    timestamp INTEGER       -- Unix timestamp
);
```

## Critical Requirements

### 1. DB Visibility (MANDATORY!)
User MUST ALWAYS see when data comes from/goes to local DB:
- **SAVE:** Show icon "🗄️ Stored 🔒"
- **RETRIEVE:** Show icon "🗄️🔍 [data] ([label])"
- **DELETE:** Show preview + "🗑️ Deleted (count)"
- Icons ensure transparency: local vs cloud data

### 2. Keyword Flexibility (v11.3.0)
Keywords use pattern `verb {x}` where {x} matches ANY text:
```bash
# All work identically:
save my email test@test.com      ✅
save the email test@test.com     ✅
save email test@test.com         ✅
```

**30+ verb synonyms per language:**
- SAVE: save/note/record/add/log/write/register (EN)
- RETRIEVE: show/get/find/check/tell/lookup (EN)
- DELETE: delete/remove/forget/erase/clear (EN)
- Similar coverage in DE/ES

### 3. No Hardcoded Keywords
ALL keywords loaded from `lang/*.conf` files dynamically.

## Development Workflow

### Testing Changes
```bash
# Copy to test environment
cp *.py /Users/martin/.aichat/
cp lang/*.conf /Users/martin/.aichat/lang/

# Restart daemon
pkill -9 -f chat_daemon.py
```

### Running Tests
```bash
# Test Qwen SQL generation
python3 qwen_sql_generator.py

# Test keyword detection
python3 local_storage_detector.py
```

## Common Tasks

### Adding New Keywords
1. Edit `lang/en.conf`, `lang/de.conf`, `lang/es.conf`
2. Add to `KEYWORDS_SAVE`, `KEYWORDS_RETRIEVE`, or `KEYWORDS_DELETE`
3. Use pattern: `verb {x}` for flexibility
4. Copy to `.aichat/lang/` and restart daemon

### Modifying SQL Generation
1. Edit `qwen_sql_generator.py` `_build_prompt()` method
2. Update pattern examples to teach Qwen new behaviors
3. Keep examples generic with placeholders like `<TEXT>`
4. Test with various inputs before committing

### Updating Language Strings
1. Edit lang files: `lang/[language].conf`
2. Keys like `msg_stored`, `msg_no_results`, etc.
3. Icons are mandatory in responses!

## Important Notes

- Keywords are checked BEFORE any cloud API call
- Qwen runs locally via Ollama (no network)
- SQLite is encrypted with AES-256 via SQLCipher
- All 3 languages (EN/DE/ES) must stay in sync
- Never remove DB visibility icons from responses

## Marketing & Privacy Policy

**CRITICAL: Separation of Concerns**

### Public Repo (ai-chat-terminal)
✅ **Allowed:**
- Product code (Python, Shell scripts)
- Product documentation (ARCHITECTURE.md, DEVELOPMENT.md)
- Landing page (docs/index.html, docs/styles.css, docs/script.js)
- Installation instructions
- Technical README

❌ **NEVER Commit:**
- Marketing campaign materials (social media posts, launch plans)
- Personal accounts (Twitter usernames, Reddit accounts)
- Campaign tracking (STATUS.md for launches)
- Marketing strategies or templates

### Private Repo (ai-chat-terminal-marketing)
**Location:** `/Users/martin/Development/ai-chat-terminal-marketing/`

✅ **Store here:**
- Social media content (TWITTER_THREAD.txt, REDDIT_POSTS.txt)
- Campaign tracking (STATUS.md)
- Marketing templates (MARKETING.md)
- Launch strategies
- Analytics and metrics

### Credentials Policy
🔐 **ALWAYS store sensitive data in macOS Keychain:**
- Twitter credentials
- Reddit API keys
- Any personal account passwords
- API tokens

**NEVER hardcode credentials in:**
- Python scripts
- Shell scripts
- Markdown files
- Git commits

**Use Keychain Helper:**
```python
from keychain_helper import get_api_key
twitter_pass = get_api_key("Twitter Password", "ma8nk")
```

Or via command line:
```bash
security find-generic-password -s "Service Name" -a "account" -w
```
