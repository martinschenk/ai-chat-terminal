# AI Chat Terminal - Architecture Documentation

## Overview

Privacy-focused AI terminal that routes sensitive data locally while using OpenAI for general queries.

**Version:** 11.0.4
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

**Example keywords:**
- EN: save, remember, store, my, is, show, delete
- DE: speichere, merke, mein, ist, zeig, lösche
- ES: guarda, recuerda, mi, es, muestra, borra

**Word boundary matching (v11.0.2):**
- Short keywords (≤2 chars) use regex `\b` to avoid false positives
- Example: "es" matches in "mi correo es", NOT in "test@ejemplo.es"

---

### 2. SQL Generation

**File:** `qwen_sql_generator.py`

**Model:** Qwen 2.5 Coder 7B via Ollama
**Purpose:** Generate SQL from natural language

**Language-agnostic (v11.0.3):**
- Receives ALL language examples (EN/DE/ES) in prompt
- Auto-detects language from input
- Mixed languages work: "my email ist..." → extracts "email" (not "email ist")

**Duplicate prevention:**
- Uses `INSERT OR REPLACE`
- Same content+meta → updates timestamp, doesn't create duplicate

---

### 3. Chat History Management

**File:** `chat_system.py`

**Context window:** 20 messages (hardcoded)
**Cleanup limit:** 100 messages (hardcoded)

**Lifecycle:**
1. **On startup:** Cleanup chat_history (keep last 100)
2. **Before OpenAI:** Load last 20 messages
3. **After OpenAI:** Save user + assistant messages

**Why cleanup at 100?**
- Prevents endless DB growth
- 100 messages = ~50 conversation pairs
- Still plenty of context for multi-day conversations

---

## Configuration

### Removed Config Parameters (v11.0.4)

- ❌ `AI_CHAT_CONTEXT_WINDOW` - Now hardcoded to 20

### Current Config Parameters

- `AI_CHAT_MODEL` - OpenAI model (default: gpt-4o-mini)
- `AI_CHAT_LANGUAGE` - User language (en, de, es, etc.)
- `AI_CHAT_MARKDOWN_RENDER` - Rich markdown rendering (true/false)

---

## Database Maintenance

### chat_history Cleanup

**When:** On every ChatSystem initialization (when terminal starts)
**What:** Keep only last 100 messages
**Why:** Prevent endless growth

**Implementation:**
```python
def _cleanup_chat_history(self):
    # Count total messages
    total = cursor.execute("SELECT COUNT(*) FROM chat_history").fetchone()[0]

    if total > 100:
        # Delete old, keep last 100
        cursor.execute("""
            DELETE FROM chat_history
            WHERE id NOT IN (
                SELECT id FROM chat_history
                ORDER BY timestamp DESC
                LIMIT 100
            )
        """)
```

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

### v11.0.4 (Current) - OpenAI Context History
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

**Last Updated:** 2025-10-13
**Maintainer:** Martin Schenk
