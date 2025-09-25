# AI Chat Terminal - Claude Code Instructions

## Project Overview
AI Chat Terminal is a Shell-GPT based CLI tool that brings ChatGPT + Web Search to the terminal with 19 language support.

**GitHub**: https://github.com/martinschenk/ai-chat-terminal
**Current Version**: 5.2.0

## Development Workflow

### Testing Installation Process
**CRITICAL**: Always test as clean user before releases:

```bash
# 1. Clean environment
rm -rf ~/.aichat ~/.config/ai-chat ~/shell-scripts* 2>/dev/null

# 2. Reload shell (if aliases were changed)
source ~/.zshrc

# 3. Test installer
curl -sL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | bash
```

### Git Workflow
```bash
# Standard development flow
git add -A
git commit -m "type: description"
git push origin main

# Version releases
echo "x.x.x" > VERSION
git add VERSION && git commit -m "release: vx.x.x" && git push
```

### File Structure
```
.
├── install.sh          # Main installer (downloads all files)
├── aichat.zsh          # Core shell script
├── modules/            # Modular components
│   ├── functions.zsh   # Helper functions
│   └── config-menu.zsh # Configuration interface
├── lang/               # 19 language files
│   ├── en.conf
│   ├── de.conf
│   └── ...
└── README.md           # Marketing/docs
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

## Installation Directory Structure
```
~/.aichat/              # Main installation
├── aichat.zsh         # Core script
├── modules/           # Function modules
├── lang/              # Language files
└── config             # User configuration
```

## Language Support
19 languages with regional dialects:
- German: Standard + Schwäbisch, Bayerisch, Sächsisch
- Spanish: Standard + Mexican, Argentinian, Colombian, Venezuelan, Chilean, Andaluz
- Plus: English, French, Italian, Catalan, Basque, Galician, Chinese, Hindi

## Command Conflict Handling
Installer intelligently detects existing `ai` command and offers alternatives:
- `aic` (AI Chat)
- `ask`
- `chat`
- Custom user choice

## Shell Integration
Adds to shell profile (`~/.zshrc` or `~/.bashrc`):
```bash
# AI Chat Terminal
[[ -f ~/.aichat/aichat.zsh ]] && source ~/.aichat/aichat.zsh
```

## Attribution
**Built on Shell-GPT** - Always credit TheR1D/shell_gpt in README and docs.

## Maintenance Tasks
- Monitor GitHub issues for user feedback
- Keep language files updated with cultural context
- Test installer on fresh macOS/Linux systems monthly
- Update OpenAI model options as new models release

## Development Philosophy
- **Honest marketing** - No inflated user numbers
- **Cost transparency** - Always explain API costs upfront
- **User choice** - Never force expensive models
- **Quality UX** - Smooth installation and configuration flow