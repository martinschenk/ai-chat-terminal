# Contributing to AI Chat Terminal

Thank you for your interest in contributing to AI Chat Terminal! This document provides guidelines for contributing to the project.

## Code of Conduct

This project follows a professional code of conduct. Be respectful, constructive, and collaborative.

## How to Contribute

### Reporting Bugs

Before creating a bug report, please check existing issues to avoid duplicates.

**When filing an issue, include:**
- AI Chat Terminal version (`cat ~/.aichat/VERSION` or check VERSION file)
- macOS version (`sw_vers`)
- Python version (`python3 --version`)
- Ollama version (`ollama --version`)
- Steps to reproduce
- Expected vs actual behavior
- Error messages (if any)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:
- Use case description
- Why this enhancement would be useful
- Proposed implementation (if you have ideas)

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Test your changes** thoroughly
3. **Update documentation** if you're changing functionality
4. **Follow the code style** (see below)
5. **Write clear commit messages**

#### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

#### Commit Messages

Follow conventional commits:
```
feat: add Spanish keyword support
fix: resolve duplicate entries in mydata table
docs: update installation instructions
refactor: simplify SQL generation logic
```

## Development Setup

### Prerequisites

- macOS 12.0+ (Monterey or later)
- Python 3.9+
- Ollama
- Qwen 2.5 Coder model

### Local Development

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ai-chat-terminal.git
cd ai-chat-terminal

# Install dependencies (local testing)
pip3 install openai requests rich sqlcipher3

# Pull Qwen model
ollama pull qwen2.5-coder:7b

# Test changes locally
cp src/aichat/*.py ~/.aichat/
cp -r src/aichat/lang ~/.aichat/
cp -r src/aichat/lang_manager ~/.aichat/
pkill -9 -f chat_daemon.py  # Restart daemon
```

### Testing

Before submitting a PR, test:

1. **Keyword detection** - Try save/show/delete commands in EN/DE/ES
2. **SQL generation** - Verify Qwen generates correct SQL
3. **Database operations** - Check mydata table integrity
4. **OpenAI integration** - Test general queries maintain context
5. **Edge cases** - Empty inputs, special characters, long text

```bash
# Test SQL generation
python3 src/aichat/qwen_sql_generator.py

# Test keyword detection
python3 src/aichat/local_storage_detector.py

# Check database
sqlite3 ~/.aichat/memory.db "SELECT * FROM mydata;"
```

## Code Style

### Python

- Follow PEP 8 guidelines
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Add docstrings to functions/classes
- Use type hints where appropriate

Example:
```python
def process_query(user_input: str, language: str = "en") -> str:
    """
    Process user input and route to appropriate handler.

    Args:
        user_input: User's chat message
        language: Language code (en, de, es)

    Returns:
        AI response string
    """
    # Implementation
```

### Shell Scripts

- Use `#!/usr/bin/env zsh` shebang
- Add error handling with `set -e`
- Comment non-obvious logic
- Test on clean macOS installation (if possible)

## Project Structure

```
ai-chat-terminal/
├── README.md              # User documentation
├── LICENSE                # MIT License
├── CONTRIBUTING.md        # This file
├── SECURITY.md            # Security policy
├── VERSION                # Current version
├── .gitignore             # Git ignore rules
├── install.sh             # Installation script
├── uninstall.sh           # Uninstallation script
├── aichat.zsh             # Zsh integration
├── config.example         # Example configuration
├── docs/                  # Documentation
│   ├── ARCHITECTURE.md    # Technical deep-dive
│   └── DEVELOPMENT.md     # Development notes
└── src/
    └── aichat/            # Main Python package
        ├── chat_system.py
        ├── qwen_sql_generator.py
        ├── memory_system.py
        ├── local_storage_detector.py
        ├── encryption_manager.py
        ├── response_generator.py
        ├── daemon_manager.py
        ├── chat_daemon.py
        ├── ollama_manager.py
        ├── get_user_history.py
        ├── db_migration*.py
        ├── lang/              # Language configs
        └── lang_manager/      # Language management
```

## Adding New Features

### Adding a New Language

1. Create `src/aichat/lang/[language_code].conf`
2. Add keywords (SAVE, RETRIEVE, DELETE)
3. Add response messages (msg_stored, msg_no_results, etc.)
4. Test with various input patterns
5. Update README.md language list

### Modifying SQL Generation

1. Edit `src/aichat/qwen_sql_generator.py`
2. Update `_build_prompt()` method with examples
3. Test with edge cases (special chars, long text, mixed languages)
4. Verify mydata table integrity after changes

### Changing Database Schema

1. Create migration script `db_migration_v[X].py`
2. Handle both encrypted and non-encrypted databases
3. Test migration on test database first
4. Update `docs/ARCHITECTURE.md` with schema changes

## Release Process

Maintainers only:

1. Update VERSION file
2. Update version in README.md badge
3. Update ARCHITECTURE.md "Last Updated"
4. Create git tag: `git tag v11.X.X`
5. Push tag: `git push origin v11.X.X`
6. Create GitHub release with changelog

## Questions?

- Open an issue for questions
- Check `docs/ARCHITECTURE.md` for technical details
- Review existing issues/PRs for context

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
