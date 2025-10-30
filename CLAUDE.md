# Claude Code - Project Instructions for AI Chat Terminal

## 🚨 CRITICAL RULE: NO LARGE DELETIONS WITHOUT EXPLICIT APPROVAL

**IMPORTANT:** Before deleting code or making major refactors:

1. ⚠️ **STOP** - Inform Martin EXACTLY what you plan to do
2. 📊 **SHOW** the consequences (what breaks? what stops working?)
3. 📈 **STATISTICS** - How many lines deleted? Which functions?
4. ⏸️ **WAIT** for explicit OK from Martin
5. ✅ Only THEN execute

### Examples of "major changes" requiring approval:
- ❌ Shortening prompts by >30%
- ❌ Removing functions without asking
- ❌ "KISS Approach" that deletes a lot
- ❌ "Cleanup" of supposedly unnecessary code
- ❌ Refactoring that deletes >50 lines

### Why?
We've often invested hours in optimizations. A "quick fix" can destroy this work in seconds. Better slow and safe!

---

## 📦 Tech Stack

- **Python 3.9+** - Main language
- **Qwen 2.5 Coder 7B** - Local AI via Ollama (5GB model)
- **SQLite** - Encrypted local storage (AES-256)
- **OpenAI GPT-4o** - Cloud AI for general queries
- **Languages:** English, German, Spanish

---

## 🏗️ Architecture Overview

### Two-Path System:
1. **Keywords detected** (save/show/delete) → Local Qwen → Encrypted SQLite
2. **No keywords** → OpenAI API (cloud)

### Two-Database System:
1. **`mydata` table** - User's private data (NEVER sent to OpenAI)
   ```sql
   CREATE TABLE mydata (
       id INTEGER PRIMARY KEY,
       content TEXT NOT NULL,  -- Actual data (email, phone, etc.)
       meta TEXT,              -- Label ("email", "phone", etc.)
       lang TEXT,              -- Language: en, de, es
       timestamp INTEGER
   );
   ```

2. **`chat_history` table** - Conversation context (sent to OpenAI)
   - Last 20 messages for context
   - Auto-cleanup keeps last 100 messages

---

## 📁 Key Files & Their Purposes

### Core System:
- **`chat_system.py`** - Main orchestrator, keyword routing, OpenAI integration
- **`qwen_sql_generator.py`** - SQL generation via Qwen 2.5 Coder (3 specialized prompts)
- **`memory_system.py`** - SQLite interface with AES-256 encryption
- **`local_storage_detector.py`** - Fast keyword detection (<1ms) with pattern matching

### Language Support:
- **`lang/*.conf`** - Language-specific keywords and UI messages (EN/DE/ES)
- **`lang_manager/`** - Language manager for multilingual UI

### Configuration:
- **`~/.aichat/config`** - User settings (language, model, timeout, etc.)
- **`~/.aichat/.env`** - OpenAI API key
- **`~/.aichat/memory.db`** - Encrypted SQLite database

---

## 🔄 Development Workflow

### Directory Structure:
- **Development:** `/Users/martin/Development/ai-chat-terminal/` (git repo)
- **Production:** `/Users/martin/.aichat/` (where daemon runs from)

### After Code Changes:
```bash
# 1. Copy ALL Python files to production
cp /Users/martin/Development/ai-chat-terminal/*.py /Users/martin/.aichat/

# 2. Clear Python cache (important!)
find /Users/martin/.aichat -name "*.pyc" -delete
find /Users/martin/.aichat -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# 3. Stop daemon (if running)
pkill -f "python.*chat_system.py" || true

# 4. Daemon auto-restarts on next `chat` command
```

### Testing:
```bash
# Test in production environment
cd /Users/martin/.aichat
python3 chat_system.py  # Manual test

# Or use actual command
chat "save my email test@test.com"
```

---

## 🎯 Critical Features

### 1. Keyword-Based Routing (v11.0.9)
Pattern-based keywords with `{x}` placeholder:
- `save {x}` matches: "save my email", "save the phone", "save email"
- `guarda {x}` matches: "guarda mi email", "guarda el teléfono"
- `zeig {x}` matches: "zeig meine Email", "zeig das Passwort"

30+ verb synonyms per language (SAVE/RETRIEVE/DELETE).

### 2. Qwen SQL Generation (v11.5.1)
Three specialized prompts with emphasized table name:
```
🎯 CRITICAL: Table name is 'mydata' (NOT my_table, NOT data)!
```
- **SAVE:** Extract VALUE + LABEL → `INSERT OR REPLACE INTO mydata`
- **RETRIEVE:** Search term → `SELECT FROM mydata WHERE ...`
- **DELETE:** VALUE vs LABEL detection → `DELETE FROM mydata WHERE ...`

### 3. Privacy First (v11.6.0)
- Auto-delete chat history after 30min inactivity
- User always sees DB operations: 🗄️ icons
- Encrypted storage (AES-256)

---

## 🐛 Common Issues

### "Spanish commands go to OpenAI"
→ Check regex in `chat_system.py:_load_action_keywords()` uses `^KEYWORDS_` (not matching `LANG_KEYWORDS_`)

### "Qwen generates wrong table name"
→ Check emphasized reminder in `qwen_sql_generator.py` prompts

### "Daemon uses old code"
→ Kill daemon: `pkill -f "python.*chat_system.py"` and restart

---

## 📝 Git Workflow

### Commits:
```bash
git add <files>
git commit -m "type: description

Details here...

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Branches:
- `main` - Stable production code
- Work directly on main for small fixes
- Create feature branches for major changes

---

## 🔍 Where to Find Things

- **Keywords:** `lang/*.conf` (KEYWORDS_SAVE, KEYWORDS_RETRIEVE, KEYWORDS_DELETE)
- **Prompts:** `qwen_sql_generator.py` (_build_prompt_save/retrieve/delete)
- **DB Schema:** `memory_system.py` (ChatMemorySystem class)
- **UI Messages:** `lang/*.conf` (msg_stored, msg_deleted, etc.)
- **Tests:** Manual testing in production (`~/.aichat/`)
