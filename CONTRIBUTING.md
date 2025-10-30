# Contributing to AI Chat Terminal

Thank you for your interest in contributing! This is an open-source project and we welcome improvements.

---

## Reporting Bugs

Before creating a bug report, please check existing issues to avoid duplicates.

**Include:**
- AI Chat Terminal version
- macOS version (`sw_vers`)
- Python version (`python3 --version`)
- Ollama version (`ollama --version`)
- Steps to reproduce
- Expected vs actual behavior

---

## Suggesting Enhancements

Enhancement suggestions are welcome! Please include:
- Use case description
- Why this would be useful
- Proposed implementation (if you have ideas)

---

## Pull Requests

### Process

1. **Fork** the repository and create your branch from `main`
2. **Test** your changes thoroughly
3. **Update** documentation if changing functionality
4. **Follow** the commit message format below
5. **Submit** a pull request

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates

### Commit Messages

Follow conventional commits:
```
feat: add Spanish keyword support
fix: resolve duplicate entries in mydata table
docs: update installation instructions
```

---

## Development Setup

### Prerequisites

- macOS 12.0+ (Monterey or later)
- Python 3.9+
- Ollama with Qwen 2.5 Coder 7B model

### Quick Start

```bash
# Clone
git clone https://github.com/martinschenk/ai-chat-terminal.git
cd ai-chat-terminal

# Install Ollama model
ollama pull qwen2.5-coder:7b

# Test
python3 qwen_sql_generator.py
```

### Testing Changes

```bash
# Copy to test environment
cp *.py ~/.aichat/
cp lang/*.conf ~/.aichat/lang/

# Restart daemon
pkill -f chat_daemon.py

# Test
chat "save my email test@test.com"
```

---

## Code Guidelines

1. **No hardcoded keywords** - Use `lang/*.conf` files
2. **DB visibility required** - Always show 🗄️ icons for DB operations
3. **Multilingual support** - Test with EN/DE/ES
4. **Documentation** - Update CLAUDE.md and ARCHITECTURE.md

---

## Questions?

Open an issue or email: contact@martin-schenk.es

---

**Thank you for contributing!** 🙏
