# AI Chat Terminal - Architecture Documentation

Privacy-focused AI terminal that routes sensitive data locally while using OpenAI for general queries.

**Version:** 11.6.0
**Repository:** https://github.com/martinschenk/ai-chat-terminal

---

## Core Architecture

### Two-Path Routing System

1. **Keywords detected** (save/show/delete) → Local Qwen 2.5 Coder → Encrypted SQLite
2. **No keywords** → OpenAI API (cloud) for general queries

**Keyword Detection:** <1ms using pattern matching from `lang/*.conf` files
**SQL Generation:** Qwen 2.5 Coder 7B via Ollama (local, no network)
**Storage:** SQLite with AES-256 encryption (SQLCipher)

---

## Two-Database System

### 1. `mydata` Table - Private Data Storage 🔒

**Purpose:** User's sensitive data (email, name, password, etc.)
**Location:** `~/.aichat/memory.db`
**Privacy:** ❌ NEVER sent to OpenAI

```sql
CREATE TABLE mydata (
    id INTEGER PRIMARY KEY,
    content TEXT NOT NULL,          -- Actual data: "mschenk.pda@gmail.com"
    meta TEXT,                       -- Label: "email"
    lang TEXT DEFAULT 'en',          -- Language: en, de, es
    timestamp INTEGER,               -- Unix timestamp
    UNIQUE(content, meta)            -- Prevent duplicates
);
```

**Usage:**
- `"save my email test@test.com"` → INSERT into `mydata`
- `"show my email"` → SELECT from `mydata`
- `"delete my email"` → DELETE from `mydata`

---

### 2. `chat_history` Table - OpenAI Context 💬

**Purpose:** Conversation history for context
**Location:** `~/.aichat/memory.db` (same file, different table)
**Privacy:** ✅ Sent to OpenAI for context

```sql
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,              -- "user" or "assistant"
    content TEXT NOT NULL,           -- The message
    timestamp INTEGER NOT NULL,
    metadata TEXT                    -- Optional JSON
);
```

**Context Window:** Last 20 messages
**Auto-Delete:** On exit OR after 30min inactivity (v11.6.0)

---

### Key Differences

| Feature | `mydata` | `chat_history` |
|---------|----------|----------------|
| **Sent to OpenAI?** | ❌ NEVER | ✅ YES |
| **Triggered by** | Keywords | Every OpenAI chat |
| **Size limit** | Unlimited | Auto-delete |
| **Example** | Email, phone, API key | "capital of france?" |
| **Cleanup** | Manual only | Exit/timeout |

---

## System Flow

### Local DB Operation (mydata)

```
User: "save my email test@test.com"
  ↓
Keyword Detection (<1ms)
  ↓ Match: ['save {x}', 'my']
Qwen SQL Generation (~1s)
  ↓ SQL: INSERT OR REPLACE INTO mydata (content, meta, lang)
         VALUES ('test@test.com', 'email', 'en')
Execute → mydata table
  ↓
Response: "🗄️ Stored 🔒"
```

**No OpenAI involved!** Private data stays local.

---

### OpenAI Operation (chat_history)

```
User: "capital of france?"
  ↓
No keywords → Route to OpenAI
  ↓
Load last 20 messages from chat_history
  ↓
Send to OpenAI with context
  ↓
Response: "The capital of France is Paris."
  ↓
Save to chat_history (user + assistant messages)
  ↓
Next: "best place to visit there?"
  → OpenAI understands "there" = Paris ✅
```

---

## Key Components

### 1. Keyword Detection

**File:** `local_storage_detector.py`
**Purpose:** Fast pattern matching to detect DB intent

**Pattern-based keywords (v11.3.0):**
- `verb {x}` where {x} matches ANY text
- No possessive requirement: works with/without my/the/his/meine/mi
- 30+ verb synonyms per language

**Examples:**
```bash
save my email test@test.com     ✅
save the email test@test.com    ✅
save email test@test.com        ✅
guarda mi correo test@test.es   ✅ (Spanish)
speichere meine Email test.de   ✅ (German)
```

**Keywords loaded from:** `~/.aichat/lang/*.conf` (dynamic, not hardcoded)

---

### 2. SQL Generation

**File:** `qwen_sql_generator.py`
**Model:** Qwen 2.5 Coder 7B via Ollama
**Purpose:** Generate SQL from natural language

**Three specialized prompts:**
1. **SAVE:** Extract VALUE + LABEL → `INSERT OR REPLACE INTO mydata`
2. **RETRIEVE:** Search term → `SELECT FROM mydata WHERE ...`
3. **DELETE:** VALUE vs LABEL detection → `DELETE FROM mydata WHERE ...`

**Language-agnostic:**
- Mixed languages work: "guarda mi email" (ES verb + EN noun) ✅
- Auto-detects language from verb: guarda→es, save→en, speichere→de

**Duplicate prevention:** Uses `INSERT OR REPLACE` with UNIQUE constraint

---

### 3. Chat History (v11.6.0 - Privacy First)

**File:** `chat_system.py`
**Context:** Last 20 messages
**Auto-delete:** Exit OR 30min inactivity

**Why auto-delete?**
- Privacy by default
- No long-term conversation storage
- User transparency (knows when history is deleted)

**What's stored:**
- ✅ OpenAI conversations (general questions)
- ❌ Qwen/SQL operations (never in chat_history)
- ❌ Data saved with keywords ("save my email..." → only in mydata)

---

## Configuration

**File:** `~/.aichat/config`

**Key parameters:**
- `AI_CHAT_MODEL` - OpenAI model (default: gpt-4o-mini)
- `AI_CHAT_LANGUAGE` - UI language (en, de, es)
- `AI_CHAT_HISTORY_AUTO_DELETE` - Delete on exit (default: true)
- `AI_CHAT_HISTORY_TIMEOUT_MINUTES` - Auto-delete timeout (default: 30)
- `AI_CHAT_CONTEXT_WINDOW` - Fixed at 20 messages

---

## Development

### Testing

```bash
# Test SQL generation
python3 qwen_sql_generator.py

# Test keyword detection
python3 local_storage_detector.py

# Check database
sqlite3 ~/.aichat/memory.db "SELECT * FROM mydata;"
sqlite3 ~/.aichat/memory.db "SELECT COUNT(*) FROM chat_history;"
```

### Adding New Keywords

1. Edit `lang/[language].conf` (en/de/es)
2. Add to `KEYWORDS_SAVE`, `KEYWORDS_RETRIEVE`, or `KEYWORDS_DELETE`
3. Use pattern: `verb {x}` for flexibility
4. Copy to `~/.aichat/lang/` and restart daemon

Example:
```bash
KEYWORDS_SAVE="save {x},note {x},record {x},remember {x}"
```

### Modifying SQL Generation

1. Edit `qwen_sql_generator.py`
2. Update `_build_prompt_save()`, `_build_prompt_retrieve()`, or `_build_prompt_delete()`
3. Keep emphasized reminder: `🎯 CRITICAL: Table name is 'mydata'`
4. Test with multilingual inputs

### Critical Requirements

1. **DB Visibility (MANDATORY!)** - User must ALWAYS see DB operations:
   - SAVE: `🗄️ Stored 🔒`
   - RETRIEVE: `🗄️🔍 [data] ([label])`
   - DELETE: Preview + `🗑️ Deleted (count)`

2. **No Hardcoded Keywords** - Load from `lang/*.conf` dynamically

3. **Multilingual Support** - EN/DE/ES must stay in sync

---

## Troubleshooting

### "OpenAI doesn't remember context"
**Cause:** chat_history not being saved
**Solution:** Check `save_message_to_db()` called after OpenAI response

### "Duplicate entries in mydata"
**Cause:** Missing UNIQUE constraint or not using INSERT OR REPLACE
**Solution:** Verify mydata has `UNIQUE(content, meta)` and Qwen uses `INSERT OR REPLACE`

### "Spanish commands go to OpenAI"
**Cause:** Regex matching `LANG_KEYWORDS_*` instead of `KEYWORDS_*`
**Solution:** Use `^KEYWORDS_` with `re.MULTILINE` flag in `_load_action_keywords()`

### "Qwen generates wrong table name"
**Cause:** Missing emphasized reminder in prompts
**Solution:** Add `🎯 CRITICAL: Table name is 'mydata'` to all 3 prompts

---

## Version History

### v11.6.0 (Current) - Privacy First
- ✅ Auto-delete chat history on exit
- ✅ Auto-delete after 30min inactivity
- ✅ Localized messages (EN/DE/ES)

### v11.3.0 - Ultra-Flexible Keywords
- ✅ Pattern-based: `verb {x}` matches ANY text
- ✅ No possessive requirement
- ✅ 30+ verb synonyms per language

### v11.0.3 - Multilingual & Duplicates
- ✅ Language-agnostic Qwen
- ✅ `UNIQUE(content, meta)` constraint
- ✅ `INSERT OR REPLACE` prevents duplicates

---

**Last Updated:** 2025-10-27
**Maintainer:** Martin Schenk
