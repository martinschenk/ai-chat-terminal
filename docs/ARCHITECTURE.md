# AI Chat Terminal - Architecture Documentation

## Overview

Privacy-focused AI terminal that routes sensitive data locally while using OpenAI for general queries.

**Version:** 11.6.0
**Repository:** https://github.com/martinschenk/ai-chat-terminal

---

## Core Architecture

### Two-Database System

The system uses **TWO separate databases** with completely different purposes:

#### 1. `mydata` Table - Private Data Storage 🔒

**Purpose:** Store user's private data (email, name, birthday, etc.)
**Location:** `~/.aichat/memory.db` (same file, different table)
**Never sent to OpenAI!**

```sql
CREATE TABLE mydata (
    id INTEGER PRIMARY KEY,
    content TEXT NOT NULL,          -- The actual data (e.g., "mschenk.pda@gmail.com")
    meta TEXT,                       -- Label (e.g., "email")
    lang TEXT DEFAULT 'en',          -- Language: en, de, es
    timestamp INTEGER,               -- Unix timestamp
    UNIQUE(content, meta)            -- v11.0.3: Prevent duplicates
);
```

**Example data:**
- content: "mschenk.pda@gmail.com", meta: "email", lang: "en"
- content: "Martin", meta: "name", lang: "en"
- content: "15.03.1990", meta: "Geburtstag", lang: "de"

**Usage:**
- SAVE: "save my email test@test.com" → INSERT into `mydata`
- RETRIEVE: "show my email" → SELECT from `mydata`
- DELETE: "delete my email" → DELETE from `mydata`

---

#### 2. `chat_history` Table - OpenAI Context 💬

**Purpose:** Store conversation history for OpenAI context
**Location:** `~/.aichat/memory.db` (same file, different table)
**IS sent to OpenAI for context!**

```sql
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,              -- "user" or "assistant"
    content TEXT NOT NULL,           -- The message
    timestamp INTEGER NOT NULL,      -- Unix timestamp
    metadata TEXT                    -- Optional JSON metadata
);
```

**Example data:**
- role: "user", content: "capital of france?"
- role: "assistant", content: "The capital of France is Paris."
- role: "user", content: "best place to visit there?"  ← "there" = Paris (context!)

**Usage:**
- After every OpenAI request → Save user + assistant messages
- Before every OpenAI request → Load last 20 messages as context
- Cleanup on startup → Keep only last 100 messages total

---

### Key Difference: mydata vs chat_history

| Feature | `mydata` | `chat_history` |
|---------|----------|----------------|
| **Purpose** | Private data storage | Conversation context |
| **Sent to OpenAI?** | ❌ NEVER | ✅ YES (for context) |
| **Triggered by** | Keywords (save, show, delete) | Every OpenAI chat |
| **Size limit** | Unlimited (user data) | 100 messages max |
| **Example** | Email, phone, birthday | "capital of france?" |
| **Cleanup** | Never (permanent storage) | On startup (keep 100) |

---

## System Flow

### 1. Local DB Operations (mydata)

```
User Input: "save my email test@test.com"
    ↓
Keyword Detection (local_storage_detector.py)
    ↓ Keywords: ['save', 'my', 'email']
Qwen SQL Generation (qwen_sql_generator.py)
    ↓ SQL: INSERT OR REPLACE INTO mydata (content, meta, lang) VALUES ('test@test.com', 'email', 'en')
Execute SQL → mydata table
    ↓
Response: "🗄️ Stored 🔒"
```

**NO OpenAI involved!** Private data stays local.

---

### 2. OpenAI Operations (chat_history)

```
User Input: "capital of france?"
    ↓
NO keywords detected → Route to OpenAI
    ↓
Load last 20 messages from chat_history
    ↓
Send to OpenAI API with context:
    [
        {"role": "user", "content": "capital of france?"}
    ]
    ↓
OpenAI Response: "The capital of France is Paris."
    ↓
Save to chat_history:
    - User message
    - Assistant response
    ↓
Next request: "best place to visit there?"
    ↓
Load context from chat_history:
    [
        {"role": "user", "content": "capital of france?"},
        {"role": "assistant", "content": "The capital of France is Paris."},
        {"role": "user", "content": "best place to visit there?"}
    ]
    ↓
OpenAI understands "there" = Paris! ✅
```

---

## Key Components

### 1. Keyword Detection

**File:** `local_storage_detector.py`

**Purpose:** Fast keyword matching to detect DB intent
**Keywords loaded from:** `~/.aichat/lang/*.conf` files

**Ultra-flexible pattern keywords (v11.3.0):**
- Keywords use `verb {x}` pattern where `{x}` matches ANY text
- No possessive requirements - works with my/the/his/meine/die/mi/la OR without any possessive
- 30+ verb synonyms per language per action

**Example keywords:**
- EN SAVE: `save {x}, note {x}, record {x}, add {x}, log {x}, write {x}, register {x}, put {x}, set {x}` (12 verbs)
- DE SAVE: `speichere {x}, merke {x}, notiere {x}, trag {x} ein, schreib {x} auf` (10 verbs)
- ES SAVE: `guarda {x}, recuerda {x}, anota {x}, registra {x}, apunta {x}, graba {x}` (10 verbs)

**All variations work identically:**
```bash
save my email test@test.com     ✅
save the email test@test.com    ✅
save email test@test.com        ✅
note phone 123456               ✅
```

**Word boundary matching (v11.0.2):**
- Short keywords (≤2 chars) use regex `\b` to avoid false positives
- Example: "es" matches in "mi correo es", NOT in "test@ejemplo.es"

---

### 2. SQL Generation

**File:** `qwen_sql_generator.py`

**Model:** Qwen 2.5 Coder 7B via Ollama
**Purpose:** Generate SQL from natural language

**Pattern-based examples (v11.3.0):**
- Prompt uses `<TEXT>` placeholder instead of rigid structure
- Shows flexible possessive handling: "mi email test@test.com", "email test@test.com", "the email test@test.com"
- Extracts TWO things: content (VALUE) and meta (LABEL) from flexible input

**Language-agnostic (v11.0.3):**
- Receives ALL language examples (EN/DE/ES) in prompt
- Auto-detects language from verb (guarda→ES, save→EN, speichere→DE)
- Mixed languages work: "guarda mi email" (ES verb + EN noun) → extracts "email" as meta

**Duplicate prevention:**
- Uses `INSERT OR REPLACE`
- Same content+meta → updates timestamp, doesn't create duplicate

---

### 3. Chat History Management (v11.6.0 - Privacy First!)

**File:** `chat_system.py`

**Context window:** 20 messages (hardcoded)
**Auto-delete:** On exit OR after 30 min inactivity

**Lifecycle:**
1. **On startup:** Check last activity time
2. **Before OpenAI:** Load last 20 messages for context
3. **After OpenAI:** Save user + assistant messages to `chat_history`
4. **On exit OR 30 min inactive:** DELETE ALL chat_history

**WHY auto-delete instead of cleanup at 100?**
- **Privacy First:** No long-term storage of potentially sensitive conversations
- **Transparency:** User knows exactly when history is deleted (exit or timeout)
- **Simple:** No need to track limits, just delete everything on session end

**What gets stored in `chat_history`:**
- ✅ OpenAI conversations (general questions, NOT private data)
- ❌ Qwen/SQL operations (NEVER stored in chat_history)
- ❌ Data saved with keywords ("save my email..." → only in `mydata` table)

**Code location:**
- Save: `chat_system.py:1145-1146` (ONLY in OpenAI path!)
- Delete: `chat_system.py:217-256` (`delete_all_chat_history()` method)
- Exit handler: `chat_system.py:99-117` (`__del__()` destructor)
- Inactivity check: `chat_system.py:789-804` (in `send_message()`)

---

## Configuration

### Privacy Config Parameters (v11.6.0)

- `AI_CHAT_HISTORY_AUTO_DELETE` - Delete chat history on exit (default: true)
  - **WHY:** Privacy by default
  - **REASON:** Prevents long-term storage of conversations
- `AI_CHAT_HISTORY_TIMEOUT_MINUTES` - Auto-delete after X min inactive (default: 30)
  - **WHY:** User might forget terminal open
  - **REASON:** Automatic cleanup prevents data accumulation

### Current Config Parameters

- `AI_CHAT_MODEL` - OpenAI model (default: gpt-4o-mini)
- `AI_CHAT_LANGUAGE` - User language (en, de, es, etc.)
- `AI_CHAT_MARKDOWN_RENDER` - Rich markdown rendering (true/false)
- `AI_CHAT_CONTEXT_WINDOW` - Hardcoded to 20 (not configurable)

---

## Database Maintenance

### chat_history Auto-Delete (v11.6.0 - Privacy First!)

**When:**
- User exits chat (explicit command)
- After 30 minutes of inactivity (automatic)
- Daemon shutdown (graceful cleanup)

**What:** Delete ALL chat_history

**Why:** Privacy by default - no long-term conversation storage

**Implementation:**
```python
def delete_all_chat_history(self):
    """Delete ALL chat_history - Privacy First!"""
    cursor.execute("DELETE FROM chat_history")
    conn.commit()
    print("🧹 Chat history deleted (privacy mode)")

# Called from:
# 1. __del__() destructor (exit/shutdown)
# 2. send_message() after 30 min inactivity
```

**Old behavior (v11.0.4):** Kept last 100 messages, cleaned on startup
**New behavior (v11.6.0):** Delete ALL on exit/timeout

**WHY this change:**
- Privacy First philosophy
- User might forget about old conversations
- No need for long-term history (only needed during active session)

---

## Privacy & Security

### What's Sent to OpenAI?

✅ **YES - Sent to OpenAI:**
- General questions ("capital of france?")
- Conversation history from `chat_history` table
- Last 20 messages for context

❌ **NO - Never sent to OpenAI:**
- Private data from `mydata` table
- Keywords that triggered local DB
- SQL queries generated by Qwen

### PII Filtering

`chat_history` loader filters out messages with `privacy_category` metadata:

```python
if metadata.get('privacy_category'):
    continue  # Skip - don't send to OpenAI!
```

---

## Version History

### v11.6.0 (Current) - Privacy First: Auto-Delete Chat History
- ✅ Chat history deleted on exit (explicit command or ESC key)
- ✅ Auto-delete after 30 min inactivity
- ✅ No exceptions - Privacy by default
- ✅ Comprehensive documentation with WHY/REASON comments
- ✅ `cleanup_history` action in daemon
- ✅ Exit handlers in shell functions
- ✅ Localized messages (EN/DE/ES)

### v11.3.0 - Ultra-Flexible Keywords
- ✅ Pattern-based keywords: `verb {x}` matches ANY text
- ✅ No possessive requirements: "my/the/his/meine/die/mi/la" all work OR omit entirely
- ✅ 30+ verb synonyms per language (12 SAVE, 14 RETRIEVE, 12 DELETE for EN)
- ✅ Simplified Qwen prompt with `<TEXT>` placeholder
- ✅ Flexible text extraction from any possessive structure
- ✅ Fixed ChatSystem regex bug (^ anchor + re.MULTILINE)

### v11.0.4 - OpenAI Context History
- ✅ Save messages to `chat_history` after OpenAI
- ✅ Load last 20 messages before OpenAI
- ✅ Cleanup on startup (keep 100 messages)
- ✅ Hardcoded context window (removed config param)

### v11.0.3 - Multilingual & Duplicate Prevention
- ✅ Language-agnostic Qwen (mixed languages work)
- ✅ UNIQUE(content, meta) constraint
- ✅ INSERT OR REPLACE prevents duplicates

### v11.0.2 - Word Boundary Matching
- ✅ Smart regex for short keywords (≤2 chars)
- ✅ Fixed false positives (e.g., "es" in "test")

### v11.0.1 - Dynamic Keyword Loading
- ✅ Load keywords from lang/*.conf files
- ✅ No hardcoded keywords

### v11.0.0 - KISS SQL Architecture
- ✅ Qwen 2.5 Coder for direct SQL generation
- ✅ Simple mydata table (no vector embeddings)

---

## Troubleshooting

### "OpenAI doesn't remember context"
**Symptom:** "best place to visit there?" → OpenAI asks "where?"
**Cause:** `chat_history` not being saved
**Solution:** Check that `save_message_to_db()` is called after OpenAI response

### "Duplicate entries in mydata"
**Symptom:** "my name is Martin" saved twice
**Cause:** Missing UNIQUE constraint or not using INSERT OR REPLACE
**Solution:** Check mydata table has `UNIQUE(content, meta)` and Qwen uses `INSERT OR REPLACE`

### "Short keywords cause false positives"
**Symptom:** "test" triggers because of "es"
**Cause:** Substring matching for short keywords
**Solution:** Use word boundary regex `\b` for keywords ≤2 chars (implemented in v11.0.2)

---

## Development

### Testing

```bash
# Test Qwen SQL generation
python3 qwen_sql_generator.py

# Test keyword detection
python3 local_storage_detector.py

# Check database
sqlite3 ~/.aichat/memory.db "SELECT * FROM mydata;"
sqlite3 ~/.aichat/memory.db "SELECT COUNT(*) FROM chat_history;"
```

### Files

- `chat_system.py` - Main orchestration, OpenAI integration
- `qwen_sql_generator.py` - SQL generation with Qwen 2.5 Coder
- `local_storage_detector.py` - Keyword detection
- `memory_system.py` - Database operations
- `lang/*.conf` - Language-specific keywords

---

## Future Improvements

- [ ] Add 🗄️ symbol to all DB responses (for transparency)
- [ ] Session-based history (currently all sessions mixed)
- [ ] Export/import mydata for backup
- [ ] Encryption for mydata (already supported via SQLCipher)

---

**Last Updated:** 2025-10-21
**Maintainer:** Martin Schenk
