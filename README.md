# AI Chat Terminal

**Get the power of GPT-4o cloud AI — with a privacy escape hatch built right in.**

Use simple keywords like `save`, `store`, or `remember` to keep your sensitive data local, encrypted, and 100% private. No cloud exposure for passwords, emails, or personal info when you choose to protect them.

**Open source. Transparent. You're in control.**

[![Version](https://img.shields.io/badge/version-11.6.0-blue.svg)](https://github.com/martinschenk/ai-chat-terminal)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://github.com/martinschenk/ai-chat-terminal)
[![Encryption](https://img.shields.io/badge/encryption-AES--256-green.svg)](https://github.com/martinschenk/ai-chat-terminal#encryption)
[![AI](https://img.shields.io/badge/AI-Qwen--2.5--Coder-orange.svg)](https://github.com/martinschenk/ai-chat-terminal)

## Why AI Chat Terminal?

We love powerful cloud AI like GPT-4o. But sometimes you need privacy.

**The problem:** Traditional AI chat sends EVERYTHING to the cloud:
- Passwords and API keys
- Email addresses and phone numbers
- Personal notes and sensitive data
- All conversations logged on their servers

**The solution:** AI Chat Terminal gives you **both worlds**:
- 🌐 **Cloud AI** when you need power (GPT-4o for complex queries)
- 🔒 **Local AI** when you need privacy (5GB Qwen 2.5 Coder encrypts data locally)

## How Privacy Works (Be Informed!)

**⚠️ Important: This is NOT automatic protection!**

We don't try to guess what's sensitive (unreliable). Instead, **YOU decide** with simple keywords.

**Think of it like this:**
- Regular ChatGPT = Everything goes to cloud (no choice)
- AI Chat Terminal = **You get a choice** every time you type

**Without keywords** → OpenAI sees everything:
```bash
You: "My email is test@example.com"
→ ⚠️ Sent to OpenAI! They see your email.

You: "My birthday is 1990-03-15"
→ ⚠️ Sent to OpenAI! They see your birthday.
```

**With keywords** → Stays local (encrypted):
```bash
You: "save my email test@example.com"
→ ✅ Processed locally by Qwen 2.5 Coder
→ ✅ Stored in encrypted SQLite on your Mac
→ ✅ OpenAI NEVER sees this!

You: "save my birthday 1990-03-15"
→ ✅ Local storage only, zero cloud exposure
```

**How it works - The 2-Stage Intent Detection System:**

```
Step 1: You type your message
  ↓
Step 2: FAST Keyword Scan (<1ms)
  ↓
  ├─ Keywords found? (save/remember/guarda/merke/show/delete)
  │   ↓
  │   YES → Go to Step 3 (Local AI Analysis)
  │
  └─ NO keywords found?
      ↓
      ❌ Skip Step 3 → Directly to OpenAI ☁️
      ⚠️ OpenAI sees your entire message

Step 3: INTELLIGENT Intent Analysis (Qwen 2.5 Coder - 5GB local AI)
  ↓
  Qwen AI analyzes: "Does the user REALLY want to save/retrieve/delete?"
  ↓
  ├─ Intent = SAVE/RETRIEVE/DELETE locally?
  │   ↓
  │   ✅ YES → Generate SQL → Encrypted local database
  │   ✅ OpenAI NEVER contacted
  │
  └─ Intent = Just a QUESTION (no save intent)?
      ↓
      Example: "how safe is 4 digit pin?"
      ⚠️ Contains "safe" keyword BUT no save intent!
      → Qwen forwards to OpenAI ☁️
      → OpenAI answers the question
```

**🔑 The 2-Stage Protection:**

**Stage 1: Keyword Scan (Fast Filter)**
- Keywords found → Activate Qwen AI for analysis
- No keywords → Skip Qwen, go directly to OpenAI

**Stage 2: Qwen AI Intent Analysis (5GB Intelligent AI)**
- Qwen reads your full message
- Analyzes: "Does user want to SAVE data locally?"
- **Intent = Save** → Local database (encrypted)
- **Intent = Question** → Forward to OpenAI (for better answer)

**Example of Stage 2 working:**
```bash
You: "how safe is 4 digit pin code?"
→ Stage 1: ✅ Keyword "safe" detected
→ Stage 2: 🖥️ Qwen analyzes intent
→ Qwen decision: "This is a QUESTION, not a save request"
→ ☁️ Forwarded to OpenAI for answer
```

**💡 Why 2 stages?**
- Stage 1 is FAST (<1ms) - filters obvious non-private queries
- Stage 2 is SMART (5GB AI) - understands context and intent
- Result: Best of both worlds (speed + intelligence)

**🌍 Works in 3 languages with 30+ keyword variants:**
- **English:** save, store, remember, note, show, list, delete, forget...
- **German:** speichere, merke, notiere, zeige, liste, lösche, vergiss...
- **Spanish:** guarda, recuerda, anota, muestra, lista, borra, olvida...

**🎯 You control privacy. Keywords activate local AI. No keywords = cloud AI.**

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

### ⚠️ WITHOUT Keywords - Everything Goes to OpenAI Cloud

**What happens internally:**
1. You type message
2. Keyword scan: NO keywords found (save/remember/guarda/merke)
3. Local AI stays OFF
4. Message sent directly to OpenAI API
5. OpenAI processes and responds

```bash
👤 You ▶ My email is test@example.com
         🔍 Keyword scan: NO keywords found
         ☁️  Sent to OpenAI API
🤖 AI    I've noted that. Is there anything else you'd like to know?
         ⚠️ OpenAI saw and logged: "My email is test@example.com"
```

```bash
👤 You ▶ capital of Spain?
         🔍 Keyword scan: NO keywords found
         ☁️  Sent to OpenAI API
🤖 AI    Madrid.
         ✅ Safe - general knowledge

👤 You ▶ best food there?
         🔍 Keyword scan: NO keywords found
         ☁️  Sent to OpenAI API (with previous context)
🤖 AI    Tapas and paella are famous Spanish dishes.
         ✅ OpenAI remembers "Spain" from previous question
```

### ✅ WITH Keywords - 2-Stage Analysis

**What happens internally:**

**STAGE 1: Fast Keyword Scan (<1ms)**
1. You type message with keyword (save/store/remember/guarda/merke)
2. Keyword scan: ✅ Keyword found!
3. Decision: Activate Qwen AI for intent analysis

**STAGE 2: Intelligent Intent Analysis (Qwen 2.5 Coder - 5GB)**
4. Qwen AI reads your FULL message
5. Qwen analyzes: "Does user want to SAVE/RETRIEVE/DELETE locally?"
6. **Intent detected = SAVE** → Generate SQL: `INSERT INTO mydata ...`
7. Data encrypted and stored in local SQLite
8. Response: 🗄️ icon (proof it stayed local!)
9. OpenAI was NEVER contacted (zero network calls)

**Alternative path if Stage 2 detects NO save intent:**
6. **Intent detected = QUESTION** → Forward to OpenAI
7. Example: "how safe is my password?" → Question, not save request!

```bash
👤 You ▶ save my email test@example.com
         Stage 1: 🔍 Keyword "save" detected!
         Stage 2: 🖥️  Qwen analyzes intent → SAVE confirmed
         Stage 2: 🔐 SQL generated → Encrypted SQLite
🤖 AI    🗄️ Stored 🔒
         ✅ OpenAI NEVER saw this!

👤 You ▶ store password SecretPass123
         Stage 1: 🔍 Keyword "store" detected!
         Stage 2: 🖥️  Qwen intent → SAVE confirmed
🤖 AI    🗄️ Stored 🔒
         ✅ Encrypted locally on your Mac

👤 You ▶ remember my birthday 1990-03-15
         Stage 1: 🔍 Keyword "remember" detected!
         Stage 2: 🖥️  Qwen intent → SAVE confirmed
🤖 AI    🗄️ Stored 🔒
         ✅ Zero network calls, zero cloud exposure

👤 You ▶ guarda mi dirección Calle Mayor 1
         Stage 1: 🔍 Keyword "guarda" detected (Spanish!)
         Stage 2: 🖥️  Qwen intent → SAVE confirmed (multilingual!)
🤖 AI    🗄️ Guardado 🔒
         ✅ Works in English, German, Spanish
```

**Edge case - Keyword found BUT no save intent:**
```bash
👤 You ▶ how safe is 4 digit pin code?
         Stage 1: 🔍 Keyword "safe" detected!
         Stage 2: 🖥️  Qwen analyzes intent → QUESTION (not save!)
         Stage 2: ☁️  Qwen forwards to OpenAI
🤖 AI    4-digit PIN codes have 10,000 possible combinations...
         ⚠️ OpenAI answered this (Qwen detected it's a question)
```

### Retrieve Your Data (Also Local!)

```bash
👤 You ▶ show my email
         🔍 Keyword scan: ✅ "show" detected!
         🖥️  Local Qwen generates SQL: SELECT FROM mydata
         🚫 OpenAI NEVER contacted
🤖 AI    🗄️🔍 test@example.com (email)

👤 You ▶ list all
         🔍 Keyword scan: ✅ "list" detected!
         🖥️  Local query: SELECT * FROM mydata
🤖 AI    🗄️🔍 Found 4 items:
           1. test@example.com (email)
           2. SecretPass123 (password)
           3. 1990-03-15 (birthday)
           4. Calle Mayor 1 (dirección)
```

### Delete Your Data (Also Local!)

```bash
👤 You ▶ delete my password
         🔍 Keyword scan: ✅ "delete" detected!
         🖥️  Local Qwen generates SQL: DELETE FROM mydata
🤖 AI    🗄️🗑️ Deleted 1 item

👤 You ▶ forget my email
         🔍 Keyword scan: ✅ "forget" detected!
         🖥️  Local processing only
🤖 AI    🗄️🗑️ Deleted 1 item
```

**🎯 Key Insight:** The 🗄️ icon is your **visual proof** that:
- Local database was used
- OpenAI was NEVER contacted
- Data stayed on your Mac (encrypted)

## What Makes This Special?

### 🔒 You're In Control
- **Choose privacy on demand** - Use keywords when you need privacy
- **No automatic guessing** - We don't try to detect sensitive data (unreliable!)
- **Visual confirmation** - 🗄️ icon proves data stayed local
- **30+ keyword variants** - Natural phrasing in English, German, Spanish

### 🧠 Best of Both Worlds
- **Powerful cloud AI** - GPT-4o for complex questions and creativity
- **Smart local AI** - 5GB Qwen 2.5 Coder for private data (encrypted)
- **Context memory** - OpenAI remembers conversation flow ("there", "it" references work!)
- **2-stage intelligence** - Fast keyword filter + smart intent analysis

### 🌍 Made for Everyone
- **3 languages built-in** - English, German, Spanish (more coming!)
- **Flexible phrasing** - "save my email" = "store email" = "remember email"
- **Easy to extend** - Add your own keywords via simple config files

### ⚡ Fast & Secure
- **Instant routing** - Keyword scan in <1ms
- **Local encryption** - AES-256-CBC via SQLCipher
- **Keychain security** - Encryption keys in macOS Keychain (not files)
- **Zero config** - Install and go, encryption works automatically

### 🔍 100% Transparent
- **Open source** - Review every line of code
- **Clear documentation** - You know exactly what happens when
- **No hidden behavior** - Every decision explained in docs

## Privacy & Chat History

**Important: Chat history is automatically deleted for maximum privacy!**

### What Gets Stored (and for how long)

**1. OpenAI Chat History (Temporary)**
- Only general OpenAI conversations stored
- Deleted automatically when you exit chat
- Also deleted after 30 minutes of inactivity
- Used ONLY for context ("capital of France?" → "best food there?")

**2. Private Data (Permanent & Encrypted)**
- Data saved with keywords (save/store/remember)
- Stored in encrypted local database (AES-256)
- NEVER deleted automatically
- NEVER sent to OpenAI

**3. Qwen/SQL Operations (Not Stored in Chat History)**
- "save my email test@test.com" → NOT in chat history (only in encrypted mydata table)
- "show my email" → NOT in chat history (local query only)
- Only OpenAI conversations stored temporarily

### Why This Matters

**Traditional AI chat:** All conversations stored forever on their servers.

**AI Chat Terminal:**
- OpenAI chats: Deleted after exit or 30 min ✅
- Private data: Only when you use keywords ✅
- Maximum privacy by default ✅

**WHY:** Your conversations might contain sensitive info you forgot about. Auto-delete prevents long-term accumulation.

**REASON:** Privacy by default - you don't have to remember to clean up.

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
│ 👤 User Input                               │
└────────────┬────────────────────────────────┘
             ↓
   ┌─────────────────────┐
   │ Keyword Detection   │  ← Fast (<1ms)
   │ save/show/delete?   │
   └─────────┬───────────┘
             ↓
      ┌──────────────┐
      │  Keywords?   │
      └──┬────────┬──┘
         │        │
    ✅ YES       ❌ NO
         ↓        ↓
  ┌──────────────┐  ┌──────────────┐
  │ 🖥️ Qwen 2.5  │  │ ☁️ OpenAI    │
  │ Coder (7B)   │  │  GPT-4o      │
  │ LOCAL ONLY   │  │  (Cloud)     │
  └─────┬────────┘  └──────┬───────┘
        ↓                   ↓
  ┌─────────────┐  ┌──────────────┐
  │ 🔒🗄️        │  │ 💬 Response  │
  │ Encrypted   │  │ with Context │
  │ SQLite DB   │  │ (OpenAI saw  │
  │ (AES-256)   │  │  your input) │
  └─────────────┘  └──────────────┘
   ⬆️ NEVER sent      ⬆️ Sent to cloud
     to cloud!
```

**The Difference:**
- **Left path:** Keywords detected → Local processing → Private
- **Right path:** No keywords → Cloud AI → OpenAI sees your message

## Join the Community 🤝

**We'd love your help making AI Chat Terminal better!**

This project is **100% open source** and built by developers who care about privacy. Whether you're a Python expert or just getting started, there's a way to contribute.

**What we need:**
- 🧪 **Testing** - Try it on different macOS versions
- 🐛 **Bug reports** - Found something broken? [Tell us!](https://github.com/martinschenk/ai-chat-terminal/issues)
- 💡 **Feature ideas** - What would make this better for you?
- 📖 **Documentation** - Help others understand how it works

**New to open source?** Perfect! Check out [CONTRIBUTING.md](CONTRIBUTING.md) for a friendly guide on getting started.

**Found a bug or security issue?** See [SECURITY.md](SECURITY.md) for how to report it.

## Documentation

- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Step-by-step guide to contributing
- **[SECURITY.md](SECURITY.md)** - Security model and reporting
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - How it works internally
- **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Development notes

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Credits

Built with love by developers who care about privacy.

**Powered by:**
- **Qwen 2.5 Coder (7B)** - Alibaba Cloud via Ollama
- **SQLCipher** - AES-256 database encryption
- **OpenAI GPT-4o** - Cloud AI for general queries

**Special thanks to:**
- Everyone who tested, reported bugs, and suggested features
- The open-source community for making tools like Ollama and SQLCipher possible

---

## Ready to Take Control? 🚀

**Try AI Chat Terminal today:**
```bash
curl -fsSL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | zsh
```

**Or explore the code first:**
- ⭐ [Star the repo](https://github.com/martinschenk/ai-chat-terminal) to show support
- 🐛 [Report issues](https://github.com/martinschenk/ai-chat-terminal/issues) you find
- 💬 [Start a discussion](https://github.com/martinschenk/ai-chat-terminal/discussions) about features
- 🤝 [Contribute](CONTRIBUTING.md) - we welcome all skill levels!

**Questions?** Check [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for technical details or [open an issue](https://github.com/martinschenk/ai-chat-terminal/issues).

---

**Made with ❤️ for privacy-conscious developers**
