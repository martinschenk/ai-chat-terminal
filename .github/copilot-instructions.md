# AI Chat Terminal - Copilot Instructions

> **⚠️ Active Development Notice (October 2025)**
> This project is currently being actively developed with Claude Code. Architecture and implementation details may change frequently. Always verify current code structure before making assumptions.

## 🧠 KISS SQL Architecture (v11.3.0)

This project uses **keyword-based routing + Qwen 2.5 Coder** for local data operations:

1. **Keyword Detection** (`local_storage_detector.py`): Pattern-based matching with `verb {x}` syntax
2. **SQL Generation** (`qwen_sql_generator.py`): Qwen 2.5 Coder 7B via Ollama for natural language → SQL
3. **OpenAI Integration** (`chat_system.py`): Routes non-DB queries to GPT-4o with conversation history

**Key Pattern**: Keywords (save/show/delete + 30+ synonyms) route to local SQLite database, everything else goes to OpenAI with context history.

## 📁 Core Architecture

- **`aichat.zsh`**: Main entry point, loads modular components from `modules/`
- **`chat_system.py`**: Core Python orchestrator with OpenAI API integration + context history
- **`local_storage_detector.py`**: Pattern-based keyword detection from `lang/*.conf` files
- **`qwen_sql_generator.py`**: Qwen 2.5 Coder for natural language → SQL generation
- **`memory_system.py`**: Simple SQLite database with `mydata` and `chat_history` tables
- **`response_generator.py`**: Phi-3 via Ollama for natural DB responses (optional, template fallback)
- **`modules/`**: Modular zsh components (functions, config, language utils)
- **`lang/`**: 3 language configurations (EN/DE/ES) with ultra-flexible pattern keywords

## 🔑 Keyword-Based Routing System

```python
# Core routing logic in local_storage_detector.py
if self._matches_keywords(user_input, save_keywords):
    return 'SAVE'
elif self._matches_keywords(user_input, retrieve_keywords):
    return 'RETRIEVE'
elif self._matches_keywords(user_input, delete_keywords):
    return 'DELETE'
else:
    return None  # Route to OpenAI
```

**Critical**: Ultra-flexible pattern keywords using `verb {x}` syntax:
- `save {x}` matches "save my email", "save the email", "save email" identically
- 30+ verb synonyms per language (save/note/record/add/log/write/register/put/set...)
- NO possessive requirements - works with ANY possessive or none at all

## 🛠️ Development Workflows

### Testing SQL Generation
```bash
# Test Qwen SQL generation with multilingual examples
python3 qwen_sql_generator.py

# Test keyword detection
python3 local_storage_detector.py

# Check database contents
sqlite3 ~/.aichat/memory.db "SELECT * FROM mydata;"
sqlite3 ~/.aichat/memory.db "SELECT COUNT(*) FROM chat_history;"
```

### Running the System
```bash
# Install and configure (requires Ollama + Qwen 2.5 Coder)
./install.sh
# Start chat (after adding to shell profile)
ai
```

### Configuration Menu
Access via `/config` in chat or `ai config` command. Handles OpenAI API keys, language selection, and model settings.

## 🌍 Multilingual Architecture

- **Language configs**: `lang/en.conf`, `lang/de.conf`, `lang/es.conf`
- **Pattern keywords per language**: 30+ verb synonyms for each action (SAVE/RETRIEVE/DELETE)
- **Language detection**: Qwen auto-detects language from verb (guarda→ES, save→EN, speichere→DE)
- **Mixed languages supported**: "guarda mi email" (ES verb + EN noun) extracts "email" as meta

## 📦 Dependencies & Installation

### Core Dependencies
- **Ollama**: Local AI runtime (required)
- **Qwen 2.5 Coder 7B**: SQL generation model via Ollama
- **requests**: OpenAI API calls
- **SQLite**: Database for mydata + chat_history

### Optional Dependencies
- **Phi-3 via Ollama**: Natural response generation (user choice, template fallback)
- **SQLCipher**: Database encryption (optional)

### Installation Pattern
```bash
# Install script checks for Ollama and Qwen 2.5 Coder
./install.sh
# Prompts user to install missing dependencies
# No Python ML models needed - uses Ollama for everything
```

## 🔒 Privacy-First Patterns

### Local DB Flow (Never Sent to OpenAI!)
```python
# Pattern for keyword-detected data
action = detector.detect_action(user_input)  # Returns SAVE/RETRIEVE/DELETE or None
if action:
    # Generate SQL with Qwen (local Ollama)
    result = qwen_generator.generate_sql(user_input, action)
    # Execute locally
    cursor.execute(result['sql'])
    # Generate response with Phi-3 or template (never sends to OpenAI)
    response = response_generator.generate(action, data)
```

### Database Schema (Two Tables, One File)
```sql
-- Table 1: Private data storage (NEVER sent to OpenAI)
CREATE TABLE mydata (
    id INTEGER PRIMARY KEY,
    content TEXT NOT NULL,      -- Actual data (email, phone, etc.)
    meta TEXT,                   -- Label (email, phone, birthday, etc.)
    lang TEXT,                   -- Language: en, de, es
    timestamp INTEGER,           -- Unix timestamp
    UNIQUE(content, meta)        -- Prevent duplicates
);

-- Table 2: OpenAI conversation history (IS sent for context)
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,          -- "user" or "assistant"
    content TEXT NOT NULL,       -- The message
    timestamp INTEGER NOT NULL,
    metadata TEXT                -- Optional JSON metadata
);
```

## 🚀 Performance Considerations

- **Fast keyword matching**: Regex-based detection with `\b` word boundaries for short keywords
- **Qwen SQL generation**: ~15s timeout (Qwen 2.5 Coder is specialized for SQL/code)
- **Context window**: Last 20 messages from chat_history (hardcoded)
- **Cleanup**: Keep only last 100 messages total (runs on startup)

## 🔧 Configuration Management

### Config File Pattern
```bash
# ~/.aichat/config format (shell-style variables)
AI_CHAT_LANGUAGE="en"
AI_CHAT_COMMAND="ai"
OPENAI_API_KEY="sk-..."
```

### Language Configuration
```bash
# lang/en.conf pattern - shell variables for UI strings + pattern keywords
LANG_LABEL_YOU="You"
LANG_LABEL_AI="AI"
LANG_DB_SOURCE="🗄️ Source: Local database"

# Ultra-flexible pattern keywords (v11.3.0)
KEYWORDS_SAVE="save {x},note {x},record {x},add {x},log {x},write {x}..."
KEYWORDS_RETRIEVE="show {x},get {x},find {x},display {x},tell {x}..."
KEYWORDS_DELETE="delete {x},remove {x},forget {x},clear {x},erase {x}..."
```

## 🧪 Testing Patterns

- **`qwen_sql_generator.py`**: Run standalone to test SQL generation with multilingual examples
- **`local_storage_detector.py`**: Test keyword detection and pattern matching
- **Database inspection**: `sqlite3 ~/.aichat/memory.db` to verify data storage
- **Multilingual tests**: EN/DE/ES examples with flexible possessive structures

## ⚠️ Common Pitfalls

1. **Keyword Loading Bug**: Use `^KEYWORDS_SAVE` (line-start anchor) not just `KEYWORDS_SAVE` in regex to avoid matching `LANG_KEYWORDS_SAVE` first
2. **Pattern Syntax**: Keywords use `verb {x}` where `{x}` is regex placeholder, not literal `{x}` string
3. **Database Tables**: `mydata` (private) vs `chat_history` (OpenAI context) - completely different purposes!
4. **Ollama Required**: System won't work without Ollama + Qwen 2.5 Coder installed
5. **DB Visibility**: MUST always show 🗄️ icon when data comes from/goes to local DB (transparency requirement!)

## 🔄 Version History

### v11.3.0 (Current) - Ultra-Flexible Keywords
- Pattern-based keywords: `verb {x}` matches ANY text
- No possessive requirements (my/the/his/meine/die/mi/la all work OR omit entirely)
- 30+ verb synonyms per language
- Fixed ChatSystem regex bug (^ anchor + re.MULTILINE)

### v11.0.4 - OpenAI Context History
- Save messages to chat_history after OpenAI
- Load last 20 messages for context
- Cleanup on startup (keep 100 messages)

### v11.0.0 - KISS SQL Architecture
- Qwen 2.5 Coder for direct SQL generation
- Simple mydata table (no vector embeddings)
- Keyword-based routing (no ML classifier)

## 🚧 Development Status & Future Changes

**Current Development Environment**: Claude Code (October 2025)

**Known Issues**:
- DELETE prompt ambiguity - Qwen may hallucinate content values when user only provides label
- Need to separate DELETE by label vs DELETE by value in prompt examples

**Before Making Changes**:
1. Test SQL generation: `python3 qwen_sql_generator.py`
2. Test keyword detection: `python3 local_storage_detector.py`
3. Verify both databases: `sqlite3 ~/.aichat/memory.db "SELECT * FROM mydata; SELECT COUNT(*) FROM chat_history;"`
4. Copy to test environment: `cp *.py ~/.aichat/ && pkill -f "python.*chat_daemon"`

**Integration Notes**:
- Always maintain keyword-based routing (no ML models!)
- Preserve two-table architecture (mydata vs chat_history)
- Keep DB visibility requirement (🗄️ icon mandatory for transparency)