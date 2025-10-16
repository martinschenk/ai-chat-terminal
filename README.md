# AI Chat Terminal

**Chat with powerful cloud AI (GPT-4o) — but your private data NEVER leaves your Mac.**

Smart keyword detection routes sensitive data to local AI instantly. Zero cloud exposure for passwords, emails, or personal info.

[![Version](https://img.shields.io/badge/version-11.5.1-blue.svg)](https://github.com/martinschenk/ai-chat-terminal)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://github.com/martinschenk/ai-chat-terminal)
[![Encryption](https://img.shields.io/badge/encryption-AES--256-green.svg)](https://github.com/martinschenk/ai-chat-terminal#encryption)
[![AI](https://img.shields.io/badge/AI-Qwen--2.5--Coder-orange.svg)](https://github.com/martinschenk/ai-chat-terminal)

## The Problem with Regular AI Chat

When you chat with ChatGPT, Claude, or any cloud AI, **EVERYTHING you type goes to their servers**. Including:
- Your passwords and API keys
- Email addresses and phone numbers
- Personal notes and sensitive data
- All conversations are logged on their servers

## The Solution

**AI Chat Terminal** intelligently routes your conversations:

```bash
You type: "What's the capital of Spain?"
→ Routes to OpenAI (cloud) ✅ Safe - general knowledge

You type: "save my password SecretPass123"
→ Routes to LOCAL Qwen 2.5 Coder ✅ NEVER sent to cloud!
→ Encrypted locally with AES-256
→ Zero network calls for this operation
```

**How it works:**
1. **Intelligent keyword detection** (<1ms) analyzes your input BEFORE sending anywhere
2. **Keywords detected** (save/show/delete/note/etc.) → **Local Qwen AI** → **Encrypted SQLite**
3. **No keywords** → Safe to send to **cloud OpenAI** for powerful general queries

## Quick Start

**Install (one command):**
```bash
curl -fsSL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | zsh
```

**Start chatting:**
```bash
source ~/.zshrc
chat
```

## Examples

### General Questions (Cloud)
```bash
👤 You ▶ capital of Spain?
🤖 AI    Madrid.

👤 You ▶ best food?
🤖 AI    Tapas.
```
*OpenAI maintains context ("best food" = Madrid from previous question)*

### Save Private Data (Local - NEVER Sent to Cloud!)
```bash
👤 You ▶ save my email test@example.com
🤖 AI    🗄️ Stored 🔒

👤 You ▶ save password SecretPass123
🤖 AI    🗄️ Stored 🔒

👤 You ▶ guarda mi dirección Calle Mayor 1
🤖 AI    🗄️ Guardado 🔒
```
*Works in English, German, and Spanish with 30+ verb synonyms*

### Retrieve Anywhere
```bash
👤 You ▶ show my email
🤖 AI    🗄️🔍 test@example.com (email)

👤 You ▶ list all
🤖 AI    🗄️🔍 Found 3 items:
           1. test@example.com (email)
           2. SecretPass123 (password)
           3. Calle Mayor 1 (dirección)
```

### Delete
```bash
👤 You ▶ delete my password
🤖 AI    🗄️🗑️ Deleted
```

## Key Features

🔒 **Privacy-First**
- Keywords (save/show/delete) → Local Qwen 2.5 Coder on your Mac
- AES-256 encrypted SQLite database
- Zero network calls for private data

🧠 **Smart Context**
- OpenAI maintains conversation history
- Ask follow-up questions naturally
- Understands "there", "it", "that" references

🌍 **Multilingual**
- English, German, Spanish
- 30+ action verbs per language
- Flexible phrasing (works with or without "my/the/his")

⚡ **Fast**
- Local operations: <1s
- OpenAI queries: 5-7s
- Always shows 🗄️ icon for local DB operations

🔐 **Encrypted**
- SQLCipher with AES-256-CBC
- Keys stored in macOS Keychain
- Zero configuration required

## What Gets Installed

**Requirements:**
- Ollama (~100MB) - Runs local AI models
- Qwen 2.5 Coder (7B) (~4.5GB) - SQL generation for private data
- Python packages (openai, requests, rich, sqlcipher3)

Installer handles everything automatically.

## Uninstall

```bash
curl -fsSL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/uninstall.sh | zsh
```
*Removes app files and shell integration. Global components (Ollama, Qwen) stay for other apps.*

## System Requirements

- macOS 12.0+ (Monterey or later)
- Zsh shell
- Python 3.9+
- ~5GB disk space (4.5GB for Qwen model)
- 8GB RAM minimum (16GB recommended)
- OpenAI API key

## How It Works

```
┌─────────────────────────────────────────────┐
│ User Input                                  │
└────────────┬────────────────────────────────┘
             ↓
   ┌─────────────────────┐
   │ Keyword Detection   │  ← Fast (<1ms)
   │ save/show/delete    │
   └─────────┬───────────┘
             ↓
      ┌──────────────┐
      │  Detected?   │
      └──┬────────┬──┘
         │        │
    YES  │        │  NO
         ↓        ↓
  ┌──────────────┐  ┌──────────────┐
  │ Qwen 2.5     │  │   OpenAI     │
  │ Coder (7B)   │  │  GPT-4o      │
  │ SQL Direct   │  │  (Cloud)     │
  └─────┬────────┘  └──────┬───────┘
        ↓                   ↓
  ┌─────────────┐  ┌──────────────┐
  │ Encrypted   │  │  Response    │
  │ SQLite DB   │  │ with Context │
  │ (AES-256)   │  │              │
  └─────────────┘  └──────────────┘
```

## Contributing

Contributions welcome! This project needs:
- Testing on different macOS versions
- More language support (French, Italian, Portuguese)
- Better error handling
- Performance optimizations

Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

**Found a bug?** [Open an issue](https://github.com/martinschenk/ai-chat-terminal/issues)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Credits

- **Qwen 2.5 Coder (7B):** Alibaba Cloud via Ollama
- **SQLite Encryption:** SQLCipher with AES-256
- **OpenAI:** GPT-4o/GPT-4o-mini for general queries

---

**Ready to try it?**
```bash
curl -fsSL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | zsh
```
