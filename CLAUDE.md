# AI Chat Terminal - Claude Code Instructions

## Project Overview
AI Chat Terminal is a Shell-GPT based CLI tool that brings ChatGPT + Web Search to the terminal with 19 language support and regional dialects.

**GitHub**: https://github.com/martinschenk/ai-chat-terminal
**Current Version**: 5.2.0 (Major UX improvements - Sept 2024)

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
├── CLAUDE.md           # This file
├── README.md           # Marketing/docs
└── VERSION             # Current version number
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
├── config                      # User configuration
└── .env                        # API keys (secure)
```

### Shell Integration (User's Shell Config)
Location: `~/.zshrc` or `~/.bashrc`
```bash
# AI Chat Terminal
source /Users/martin/.aichat/aichat.zsh
alias ai='ai_chat_function'    # or user's chosen command
```

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
- **shell-gpt**: Auto-installed via pip3
- **Python 3**: Usually pre-installed on macOS/Linux
- **curl**: For downloads
- **OpenAI API key**: User must provide

### Optional
- **Perplexity API**: For web search features

## 🆕 Recent Major Improvements (Sept 2024)

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

### ✅ Perplexity Model Selection in Config
**Problem**: Config menu only asked for OpenAI model, not Perplexity
**Solution**: Added Perplexity model selection after OpenAI model selection
- Only shows if Perplexity API key is configured
- Models: pplx-7b-online, pplx-70b-online, sonar-small-online, sonar-medium-online

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
alias ai='ai_chat_function'    # or user's chosen command (ask, chat, etc.)
```

## Uninstall Process (Enhanced)
The improved uninstall function (start ai, then type /config → [9]):
1. **Smart Detection**: Finds ANY alias pointing to `ai_chat_function`
2. **Shell Cleanup**: Removes from `.zshrc`, `.bashrc`, `.profile`
3. **Directory Removal**: Deletes entire `~/.aichat/` directory
4. **Deferred Cleanup**: Uses background script to avoid self-deletion issues

## Attribution
**Built on Shell-GPT** - Always credit TheR1D/shell_gpt in README and docs.

## Maintenance Tasks
- Monitor GitHub issues for user feedback
- Keep language files updated with cultural context
- Test installer on fresh macOS/Linux systems monthly
- Update OpenAI model options as new models release
- **NEW**: Test dialect selection flows regularly
- **NEW**: Verify multi-alias prevention works
- **NEW**: Ensure config menu UX remains smooth

## Development Philosophy
- **Honest marketing** - No inflated user numbers
- **Cost transparency** - Always explain API costs upfront
- **User choice** - Never force expensive models
- **Quality UX** - Smooth installation and configuration flow
- **Robust cleanup** - No leftover aliases or config fragments
- **Cultural sensitivity** - Proper dialect and language support