# AI Chat Terminal - Claude Code Instructions

## Project Overview
AI Chat Terminal is a native Python CLI tool with direct OpenAI API integration that brings ChatGPT + Web Search + AI Vector Database to the terminal with 19 language support and regional dialects.

**GitHub**: https://github.com/martinschenk/ai-chat-terminal
**Current Version**: 5.4.0 (Native OpenAI API Integration - Sept 2025)

**🎯 Major Features (v5.4.0):**
- **Native OpenAI Integration**: Direct API calls without shell-gpt dependency
- **Dual-Layer Memory**: Short-term context (5-50 msgs) + Long-term SQLite database
- **AI Vector Search**: Semantic search with sentence-transformers (384D embeddings)
- **Cost Optimization**: Configurable context windows with cost indicators
- **Graceful Degradation**: Falls back to text search if AI unavailable
- **Zero Setup**: Database auto-created, works on any macOS/Linux system

## 📁 Project Structure & Installation Locations

### Development Project Location
```
📁 /Users/martin/Development/ai-chat-terminal/
├── install.sh          # Main installer (downloads all files)
├── aichat.zsh          # Core shell script
├── modules/            # Modular components
│   ├── functions.zsh   # Helper functions
│   └── config-menu.zsh # Configuration interface with loop
├── lang/               # 19 language files with dialects
│   ├── en.conf
│   ├── de.conf         # German with Schwäbisch, Bayerisch, Sächsisch
│   ├── es.conf         # Spanish with Mexican, Argentinian, etc.
│   └── ...
├── memory_system.py    # AI Vector Database (v5.3.0)
├── chat_system.py      # Native OpenAI API Integration (NEW v5.4.0)
├── CLAUDE.md           # This file
├── README.md           # Marketing/docs
└── VERSION             # Current version number (5.4.0)
```

### User Installation Location (when installed from GitHub)
```
📁 ~/.aichat/                    # Main installation directory
├── aichat.zsh                  # Core script (copied from GitHub)
├── modules/                    # Function modules
│   ├── functions.zsh           # Helper functions
│   └── config-menu.zsh         # Config interface with UX improvements
├── lang/                       # All 19 language files
│   ├── en.conf                 # English
│   ├── de.conf                 # German + dialects
│   ├── es.conf                 # Spanish + variants
│   ├── fr.conf, it.conf, ...   # Other languages
│   └── zh.conf, hi.conf        # Chinese, Hindi
├── memory_system.py            # AI Vector Database
├── chat_system.py              # Native OpenAI API Integration (NEW v5.4.0)
├── memory.db                   # SQLite database (auto-created)
├── config                      # User configuration
└── .env                        # API keys (secure)
```

### Shell Integration (User's Shell Config)
Location: `~/.zshrc` or `~/.bashrc`
```bash
# AI Chat Terminal
source /Users/martin/.aichat/aichat.zsh
alias chat='noglob ai_chat_function'    # with noglob for special characters
```

## IMPORTANT: Date/Year Handling

⚠️ **CRITICAL REMINDER**: When adding dates or years to ANY code, docs, or comments:
1. **NEVER assume the current year**
2. **ALWAYS check the current date first** (Today is 2025-09-26)
3. **Use 2025 for all new copyright notices**
4. **Search existing files for old years** and update them
5. **Check system date if unsure**: use `date` command or ask user

**Common mistake**: Using 2024 when it's actually 2025! Always verify!

## Development Workflow

### Testing Installation Process
**CRITICAL**: Always test as clean user before releases:

```bash
# 1. Clean environment (improved uninstall detection)
Start ai, then type /config → [9] Uninstall → "LÖSCHEN"  # or use old method:
rm -rf ~/.aichat ~/.config/ai-chat ~/shell-scripts* 2>/dev/null

# 2. Reload shell (if aliases were changed)
source ~/.zshrc

# 3. Test installer
curl -sL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | bash

# 4. Test dialect selection (NEW)
# Select [2] Deutsch → Should prompt for dialects
# Select [5] Español → Should prompt for variants
```

### Git Workflow
```bash
# Development is done in: /Users/martin/Development/ai-chat-terminal/
cd /Users/martin/Development/ai-chat-terminal

# Standard development flow
git add -A
git commit -m "type: description"
git push origin main

# Version releases
echo "x.x.x" > VERSION
git add VERSION && git commit -m "release: vx.x.x" && git push
```

## 🧠 Smart Memory System (v5.3.0)

### Technical Implementation
```bash
📁 ~/.aichat/memory.db               # SQLite database (auto-created)
├── chat_history                     # All messages with metadata
├── chat_embeddings (if AI available) # 384D vector embeddings
└── memory_summaries                 # Future: conversation summaries
```

### Key Components
- **memory_system.py**: Core AI vector database logic
- **multilingual-e5-small**: Converts text → 384-dimensional embeddings (100 languages)
- **sqlite-vec**: Vector similarity search in SQLite
- **Language Detection**: Automatic detection and storage per message
- **Cross-Language Search**: Query in any language, find content in any other
- **Graceful Degradation**: Text search fallback if AI unavailable

### What "Graceful Degradation" Means:
```bash
# Scenario 1: Full AI System (optimal)
✅ sqlite-vec extension loads → Vector search with semantic understanding
Search: "Docker problems" → Finds: "container won't start", "image issues"

# Scenario 2: Fallback Mode (still functional)
❌ sqlite-vec fails to load → Falls back to basic text search
Search: "Docker" → Finds: any message containing "Docker" (LIKE queries)

# System NEVER breaks - always provides some search functionality
```

### What "No Dependencies on System SQLite" Means:
```bash
# Problem: macOS ships with SQLite compiled WITHOUT extension support
# Solution: Our system detects this and adapts automatically

# System A (Full features): Linux with extension support
✅ Vector search + Text search

# System B (Reduced features): macOS with limited SQLite
✅ Text search only (still very useful)

# User sees no difference in installation - everything "just works"
```

### Language-Aware Features (NEW v5.3.0):
```bash
# Cross-Language Search Magic
User sets UI to English, but chats in German:
Query: "Docker problems" → Finds: "Docker Container Probleme"

# Language Detection per Message
- Automatically detects language for each message
- Stores language metadata in database
- Uses keywords from ALL language files for importance scoring

# Universal Human Memory Keywords
- Personal info: "my name", "mein Name", "mi nombre", "我的名字"
- Preferences: "I prefer", "ich bevorzuge", "prefiero", "我喜欢"
- Context: "as I mentioned", "wie ich sagte", "como dije", "正如我提到的"
- 150+ keywords per language covering identity, preferences, life events
```

### Memory System Integration:
- **Auto-save**: Every chat message saved in background (non-blocking)
- **Config Menu**: [6] Memory system → Search, stats, smart cleanup
- **Search Examples**: "Docker issues", "Python debugging", "API problems"
- **Smart Scoring**: Important messages (errors, TODOs) get higher scores
- **Multilingual Support**: Works seamlessly across all 19 supported languages

### Smart Cleanup System (v5.3.0):
```bash
# Automatic triggers:
- 5000+ messages OR 50MB+ database size
- Target: 90% (reduces to 4500 messages)

# Deletion priority (KISS approach):
1. importance < 1.5 + oldest first
2. NEVER delete: names, important keywords
3. Protected: "name", "heißt", "bin", "remember"

# Result: Important conversations kept forever, performance optimal
```

## Critical Requirements

### 🚨 NEVER Lie in Marketing
- NO false user counts ("15,000+ developers" was WRONG)
- Honest cost transparency ($5 minimum OpenAI credit)
- Clear about Shell-GPT dependency

### 🧪 Pre-Release Checklist
- [ ] Test clean installation
- [ ] Verify no conflicting aliases (`ai`, `q` commands)
- [ ] Check all 19 language files download
- [ ] Test OpenAI + Perplexity setup flow
- [ ] Verify command conflict detection works
- [ ] **NEW**: Test German dialect selection (Hochdeutsch, Schwäbisch, Bayerisch, Sächsisch)
- [ ] **NEW**: Test Spanish variant selection (Standard, Mexican, Argentinian, etc.)
- [ ] **NEW**: Test config menu loops back properly (not to chat)
- [ ] **NEW**: Test multi-alias prevention (changing commands)
- [ ] **NEW**: Test improved uninstall function with smart alias detection

### 💰 API Cost Transparency
Always clearly explain in installer:
- OpenAI requires $5 minimum credit
- gpt-3.5-turbo is cheapest option (10x cheaper than GPT-4)
- Average cost: $0.01-0.10 per conversation
- Perplexity has free tier available

## Dependencies

### Required
- **OpenAI Python SDK**: Auto-installed via pip3
- **Python 3**: Usually pre-installed on macOS/Linux
- **curl**: For downloads
- **OpenAI API key**: User must provide

### Optional
- **Perplexity API**: For web search features

## 🆕 Recent Major Improvements (Sept 2025)

### ✅ Native OpenAI Integration - v5.4.0 (NEW!)
**Feature**: Replaced shell-gpt with direct OpenAI Python SDK integration
**Implementation**:
- **chat_system.py**: New Python module for direct API calls
- **No Dependencies**: Removed shell-gpt, sgpt commands entirely
- **Better Error Handling**: Native Python error management
- **Background Job Fix**: Eliminated `[4] 25734 done` notifications
- **Chat Role Fix**: No more "Could not determine chat role" errors
- **Memory Integration**: Automatic saving to memory.db
- **Cost Tracking**: Token counting and usage statistics
- **Streaming Support**: Real-time response display

### ✅ Smart Memory System - v5.3.0
**Feature**: Revolutionary AI-powered vector database for semantic search
**Implementation**:
- **SQLite + Vector Embeddings**: sentence-transformers (384D) + sqlite-vec
- **Dual-Layer Architecture**: Short-term context + long-term memory
- **Graceful Degradation**: Falls back to text search if AI unavailable
- **Zero Setup**: Database auto-created, works on any system
- **Search Intelligence**: "Docker problems" finds "container issues"
- **Config Integration**: Menu [6] → Memory system with search/stats/cleanup

### ✅ Cost-Optimized Context Windows - v5.2.0
**Problem**: Chat history grows infinitely → Each API call sends ALL previous messages → Exponential cost growth
**Solution**: Configurable message limits (5-50) that truncate old history before each API call
**Implementation**:
- **Cost Protection**: Automatically limits tokens sent to API
- **User Control**: Choose between ultra-low cost (5 msgs) vs. memory (50 msgs)
- **Default Sweet Spot**: 20 messages = ~$0.01 per request (instead of exponentially growing)
- **Transparent Limits**: Clear cost indicators show token impact

### ✅ Fixed Language & Dialect Selection
**Problem**: German and Spanish dialect selection wasn't working in setup
**Solution**: Added proper function calls to `handle_german_selection()` and `handle_spanish_selection()`
- **German**: Hochdeutsch, Schwäbisch, Bayerisch, Sächsisch
- **Spanish**: Standard, Mexican, Argentinian, Colombian, Venezuelan, Chilean, Andaluz, Catalan, Basque, Galician

### ✅ Enhanced Config Menu UX
**Problem**: Config menu returned to chat after each action (frustrating!)
**Solution**: Added `while(true)` loop - menu shows again after each config change
- Users can change multiple settings in one session
- Only [6] "Back to chat" exits the menu
- Config values refresh on each loop iteration

### ✅ Bulletproof Multi-Alias Prevention
**Problem**: Users could end up with multiple aliases (ai + chat + ask simultaneously)
**Solution**: Smart alias detection and cleanup
- `update_shell_config()` removes ALL `ai_chat_function` aliases before adding new one
- Uninstall function finds ANY alias pointing to `ai_chat_function` (regardless of name)
- No more duplicate aliases when users change commands

### ✅ Shell Globbing Prevention (NEW)
**Problem**: Commands with special characters (?, *, []) caused shell globbing errors
**Solution**: Added `noglob` prefix to all aliases
- Prevents zsh/bash from expanding special characters before script execution
- Enables natural CLI usage: `chat What is the weather today?` (no quotes needed)
- Fixed "zsh: no matches found" errors for questions ending with '?'

### ✅ Chat Session Role Bug Fix (NEW)
**Problem**: When command was "chat", shell-gpt got role "chat_chat" and failed
**Solution**: Changed chat session naming from `${COMMAND_CHAR}_chat` to `${COMMAND_CHAR}_session`
- Prevents duplicate "chat" in role names
- Fixes "Could not determine chat role" errors
- Ensures proper shell-gpt integration

### ✅ Session Timeout System Removal (NEW)
**Problem**: Confusing [Continue XXXs] display and unnecessary session expiration
**Solution**: Completely removed session timeout system
- No more session timeouts - chat persists indefinitely
- Removed TIMEOUT_FILE, SESSION_STATUS, and related logic
- Clean header display: '/config = settings | ESC/exit = quit'
- Simplified config menu (removed timeout option, renumbered [1-8])
- Users can chat as long as they want without interruption

### ✅ Enhanced Documentation with Examples (NEW)
**Problem**: README had verbose, unrealistic examples
**Solution**: Complete redesign with concise, engaging examples
- Memory Example: Shows conversation context across multiple questions
- DateTime Example: Demonstrates local time awareness and personality
- Fun Example: Shows AI humor and engaging responses
- Language Selection: Visual guide to dialect selection (German variants)
- All examples show actual terminal format with proper headers

## Language Support (Enhanced)
**19 languages with regional dialects (NOW WORKING!):**
- **German**: Hochdeutsch + Schwäbisch, Bayerisch, Sächsisch
- **Spanish**: Standard + Mexican, Argentinian, Colombian, Venezuelan, Chilean, Andaluz + Catalan, Basque, Galician
- **Others**: English, French, Italian, Chinese (Mandarin), Hindi

## Command Conflict Handling (Robust)
Installer intelligently detects existing `ai` command and offers alternatives:
- `aic` (AI Chat)
- `ask`
- `chat`
- Custom user choice
- **NEW**: Smart cleanup prevents multiple aliases

## 🔧 Technical Implementation Details

### Smart Alias Management
```bash
# OLD problematic approach:
grep -v "alias $command=" "$config"  # Only removed new command

# NEW bulletproof approach:
grep -v "alias.*=.*ai_chat_function" "$config"  # Removes ANY ai_chat_function alias
```

### Config Menu Loop Implementation
```bash
# NEW: Persistent config menu
show_config_menu() {
    while true; do
        # Display menu
        case $choice in
            1-5,7-9) # Execute action, then loop continues
            6) return  # Only way to exit
        esac
    done
}
```

### Language Selection Flow
```bash
# NEW: Proper dialect handling
case "$lang_choice" in
    2) # German
        language="de"
        handle_german_selection    # NEW: Actually calls this!
        language="$selected_lang"  # Uses result
        ;;
    5) # Spanish
        language="es"
        handle_spanish_selection   # NEW: Actually calls this!
        language="$selected_lang"  # Uses result
        ;;
esac
```

## Shell Integration (Updated)
Adds to shell profile (`~/.zshrc` or `~/.bashrc`):
```bash
# AI Chat Terminal
source /Users/martin/.aichat/aichat.zsh
alias chat='noglob ai_chat_function'    # with noglob for special characters (ask, chat, etc.)
```

## Uninstall Process (Enhanced)
The improved uninstall function (start ai, then type /config → [9]):
1. **Smart Detection**: Finds ANY alias pointing to `ai_chat_function`
2. **Shell Cleanup**: Removes from `.zshrc`, `.bashrc`, `.profile`
3. **Directory Removal**: Deletes entire `~/.aichat/` directory
4. **Deferred Cleanup**: Uses background script to avoid self-deletion issues

## Attribution
**Native Python Implementation** - Direct OpenAI API integration without external dependencies.

## Maintenance Tasks
- Monitor GitHub issues for user feedback
- Keep language files updated with cultural context
- Test installer on fresh macOS/Linux systems monthly
- Update OpenAI model options as new models release
- **NEW**: Test dialect selection flows regularly
- **NEW**: Verify multi-alias prevention works
- **NEW**: Ensure config menu UX remains smooth
- **NEW**: Test special character handling without quotes
- **NEW**: Verify chat session role naming works correctly
- **NEW**: Test persistent chat sessions (no timeout interruptions)
- **NEW**: Verify date/time context injection works in all modes
- **NEW**: Test documentation examples match actual terminal behavior


## Development Philosophy
- **Honest marketing** - No inflated user numbers
- **Cost transparency** - Always explain API costs upfront
- **User choice** - Never force expensive models
- **Quality UX** - Smooth installation and configuration flow
- **Robust cleanup** - No leftover aliases or config fragments
- **Cultural sensitivity** - Proper dialect and language support