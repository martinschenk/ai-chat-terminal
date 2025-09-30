# AI Chat Terminal - Copilot Instructions

> **⚠️ Active Development Notice (September 2025)**  
> This project is currently being actively developed with Claude Code. Architecture and implementation details may change frequently. Always verify current code structure before making assumptions.

## 🧠 Dual AI Architecture (Critical Understanding)

This project uses **two separate AI models** for different purposes:

1. **Privacy Classifier** (`privacy_classifier_fast.py`): `all-MiniLM-L6-v2` for ultra-fast privacy detection (40% faster)
2. **Memory System** (`memory_system.py`): `multilingual-e5-small` for semantic search in local SQLite database

**Key Pattern**: Privacy-sensitive data (SENSITIVE/PROPRIETARY/PERSONAL) routes to local processing, while PUBLIC queries go to OpenAI.

## 📁 Core Architecture

- **`aichat.zsh`**: Main entry point, loads modular components from `modules/`
- **`chat_system.py`**: Core Python orchestrator with OpenAI API integration
- **`privacy_classifier_fast.py`**: AI-based privacy classification using sentence transformers
- **`memory_system.py`**: Vector embeddings + SQLite for semantic memory
- **`response_generator.py`**: Template-based responses with optional Phi-3 support
- **`modules/`**: Modular zsh components (functions, config, language utils)
- **`lang/`**: 19 language configurations with UI strings and templates

## 🔑 Privacy Routing System

```python
# Core routing logic in privacy_classifier_fast.py
route_locally = category in ['SENSITIVE', 'PROPRIETARY', 'PERSONAL']
# Categories determined by AI classification, not hardcoded keywords
```

**Critical**: No hardcoded keyword matching. The system uses semantic similarity with 160+ training examples across 4 categories.

## 🛠️ Development Workflows

### Testing Privacy Classification
```bash
# Test PII detection with comprehensive examples
python3 test_pii.py
```

### Running the System
```bash
# Install and configure
./install.sh
# Start chat (after adding to shell profile)
ai
```

### Configuration Menu
Access via `/config` in chat or `ai config` command. Handles OpenAI API keys, language selection, and privacy settings.

## 🌍 Multilingual Architecture

- **Language configs**: `lang/{code}.conf` (en, de, es, fr, etc.)
- **Regional variants**: `lang/de-bayerisch.conf`, `lang/es-mexicano.conf`
- **Cross-language memory**: Query in German, find English content seamlessly
- **E5 prefixes**: Use "query:" and "passage:" prefixes for optimal multilingual embeddings

## 📦 Dependencies & Installation

### Core Dependencies
- `sentence-transformers`: For both AI models
- `sqlite-vec`: Vector similarity search
- `requests`: OpenAI API calls

### Optional Dependencies
- **Presidio**: Enhanced PII detection (graceful fallback to regex)
- **Phi-3**: Natural response generation (2GB model, user choice)
- **spaCy models**: Multilingual NER support

### Installation Pattern
```bash
# Smart dependency installation in install.sh
# Checks for existing installations, offers reinstall/fresh install
# Downloads models only if needed, caches for performance
```

## 🔒 Privacy-First Patterns

### Local Processing Flow
```python
# Pattern for sensitive data handling
if privacy_category in ['SENSITIVE', 'PROPRIETARY', 'PERSONAL']:
    # Store in local SQLite with vector embeddings
    memory_system.store_private_data(text, metadata)
    # Generate template response (never sends to OpenAI)
    response = response_generator.generate_local_response(intent, category)
```

### Memory Storage Schema
```sql
-- Enhanced schema with privacy categories and vector embeddings
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    content TEXT,
    metadata JSON  -- Includes privacy_category, language, importance
);
```

## 🚀 Performance Considerations

- **Model caching**: AI models lazy-load and cache embeddings in `~/.aichat/`
- **Fast classification**: MiniLM model processes queries in ~31ms
- **Vector search**: Uses sqlite-vec extension for efficient similarity search
- **Graceful degradation**: Falls back to keyword-based classification if AI models unavailable

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
# lang/en.conf pattern - shell variables for UI strings
LANG_LABEL_YOU="You"
LANG_LABEL_AI="AI"
LANG_DB_SOURCE="🗄️ Source: Local database"
```

## 🧪 Testing Patterns

- **`test_pii.py`**: Comprehensive test suite for privacy classification
- **Multilingual test cases**: Credit cards, passwords, business data across languages
- **Performance benchmarks**: <200ms targets for all operations
- **Fallback testing**: Ensures graceful degradation without AI models

## ⚠️ Common Pitfalls

1. **Model Paths**: Always use `Path.home() / '.aichat'` for consistent config directory
2. **E5 Prefixes**: Memory system requires "query:"/"passage:" prefixes for optimal results
3. **Privacy Categories**: Use exact strings: `['SENSITIVE', 'PROPRIETARY', 'PERSONAL', 'PUBLIC']`
4. **Zsh Integration**: Main function must be `ai_chat_function` in global scope
5. **Error Handling**: Always provide fallback mechanisms for missing AI models

## 🔄 Migration Patterns

When upgrading models or schemas, provide migration scripts (see `migrate_to_e5_base.py`) that:
- Preserve existing user data
- Re-encode embeddings with new models
- Update database schema incrementally
- Provide progress indicators for large migrations

## 🚧 Development Status & Future Changes

**Current Development Environment**: Claude Code (September 2025)

**Expected Changes**:
- Architecture modifications may be in progress
- New features and components may be added
- Performance optimizations and refactoring ongoing

**Before Making Changes**:
1. Check current file structure with `ls -la` and `find . -name "*.py"`
2. Verify imports and dependencies are up to date
3. Run `python3 test_pii.py` to ensure privacy classification still works
4. Test installation flow with `./install.sh` if modifying core components

**Integration Notes**:
- Always maintain backward compatibility for existing user configurations
- Preserve the dual AI model architecture principle
- Keep privacy-first routing as the core design pattern