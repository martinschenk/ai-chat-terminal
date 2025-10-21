# Security Policy

## Supported Versions

AI Chat Terminal follows semantic versioning. Security updates are provided for the latest stable release.

| Version | Supported          |
| ------- | ------------------ |
| 11.6.x  | :white_check_mark: |
| 11.5.x  | :white_check_mark: |
| < 11.0  | :x:                |

## Security Model - Critical Disclaimer

⚠️ **AI Chat Terminal does NOT automatically protect you from sending sensitive data to OpenAI.**

**This is NOT a security filter.** This is an **alternative storage method** that YOU must actively use.

If you type sensitive data WITHOUT keywords, it WILL be sent to OpenAI.

### How It Works

**❌ WITHOUT keywords** → Sent to OpenAI (cloud):
```bash
You: "My email is test@example.com"
→ ⚠️ Entire message sent to OpenAI
→ ⚠️ OpenAI sees and logs your email
→ ⚠️ NO PROTECTION - you forgot the keyword!

You: "My password is SecretPass123"
→ ⚠️ Sent to OpenAI! Password exposed!
→ ⚠️ We did NOT stop this - you must use keywords!
```

**✅ WITH keywords** → Stored locally (never sent to cloud):
```bash
You: "save my email test@example.com"
→ ✅ Keyword detected: Local processing only
→ ✅ Processed by Qwen 2.5 Coder on your Mac
→ ✅ Stored in encrypted SQLite database
→ ✅ OpenAI NEVER sees this

You: "save my password SecretPass123"
→ ✅ Local storage, zero cloud exposure
```

**Key principle:**
- We offer an alternative (local storage with keywords)
- We do NOT automatically protect you
- YOU must remember to use keywords for private data
- If you forget keywords, data goes to OpenAI!

### What This Means for You

**Think of it like a light switch:**
- **Switch OFF** (no keywords) = Everything goes to OpenAI (like regular ChatGPT)
- **Switch ON** (with keywords) = Local AI activated, data stays on your Mac

**YOU control the switch. Keywords = Local AI ON. No keywords = OpenAI.**

### The 2-Stage Intent Detection System - How It Really Works

**Complete transparency - step by step:**

#### Path 1: NO Keywords = Direct to OpenAI

1. **You type:** "My email is test@test.com"
2. **Stage 1 (Keyword scan <1ms):** ❌ NO keywords found
3. **Decision:** Skip Stage 2, send directly to OpenAI
4. **Result:** ☁️ OpenAI processes and logs your message

#### Path 2: Keywords Found = 2-Stage Analysis

1. **You type:** "save my email test@test.com"

2. **STAGE 1: Fast Keyword Scan (<1ms)**
   - Checks for: save, store, remember, show, delete, guarda, merke, etc. (30+ variants)
   - Result: ✅ "save" keyword found!
   - Decision: Activate Qwen AI for intelligent analysis

3. **STAGE 2: Intelligent Intent Analysis (Qwen 2.5 Coder - 5GB local AI)**
   - Qwen reads your FULL message context
   - Qwen analyzes: "Does user want to SAVE/RETRIEVE/DELETE data locally?"
   - **Two possible outcomes:**

   **A) Intent = SAVE/RETRIEVE/DELETE locally**
   - Qwen generates SQL: `INSERT INTO mydata (content, meta) VALUES ('test@test.com', 'email')`
   - Data encrypted with AES-256 and stored locally
   - Response shows 🗄️ icon (visual proof!)
   - OpenAI was NEVER contacted (zero network calls)

   **B) Intent = QUESTION (no save/retrieve/delete intent)**
   - Example: "how safe is 4 digit pin code?"
   - Stage 1: ✅ Keyword "safe" detected
   - Stage 2: 🖥️ Qwen analyzes → "This is a QUESTION, not a save request"
   - Decision: Forward to OpenAI for better answer
   - Result: ☁️ OpenAI answers the question

**Key principle:**
- Stage 1 = Fast keyword filter (you trigger with words)
- Stage 2 = Intelligent AI analysis (Qwen decides intent)
- YOU activate Stage 1 with keywords
- Qwen decides Stage 2 outcome intelligently
- We do NOT automatically protect you without keywords

### Data Privacy Features

When you DO use keywords correctly:
- **Keyword-triggered privacy**: Use `save`/`store`/`remember` to keep data local
- **Local AI processing**: Qwen 2.5 Coder runs on your Mac (no network)
- **AES-256 encryption**: SQLCipher encrypts local database with AES-256-CBC
- **Keychain integration**: Encryption keys stored in macOS Keychain (not in files)
- **30+ keyword variants**: Works in English, German, Spanish (see lang/*.conf files)
- **Visual confirmation**: 🗄️ icon proves data stayed local

## Chat History vs. Private Data Storage

### Two Separate Database Tables

**1. Temporary Chat History (`chat_history` table)**
- **What:** OpenAI conversations (general questions)
- **Storage:** SQLite database (encrypted)
- **Lifetime:** **Deleted on exit OR after 30 min inactivity** ← Privacy First!
- **Sent to OpenAI:** YES (last 20 messages for context)
- **Purpose:** Enable follow-up questions

**WHY auto-delete:** Conversations might contain sensitive info you forgot about.
**REASON:** Privacy by default - no long-term accumulation.

**2. Permanent Private Data (`mydata` table)**
- **What:** Data saved with keywords (save/store/remember)
- **Storage:** Encrypted SQLite (AES-256)
- **Lifetime:** Permanent (until you explicitly delete)
- **Sent to OpenAI:** NEVER
- **Purpose:** Store sensitive data locally

### What Gets Sent to OpenAI?

**✅ Sent to OpenAI (cloud):**
- General questions without keywords (e.g., "capital of Spain?")
- Conversation history from `chat_history` table (max 20 messages)
- **Note:** Deleted after exit or 30 min → No long-term storage

**❌ NEVER sent to OpenAI:**
- Private data from `mydata` table (emails, passwords, personal info)
- Keywords that triggered local processing
- SQL queries generated by Qwen
- Qwen/SQL operation results
- Encryption keys

### Encryption Details

- **Algorithm**: AES-256-CBC via SQLCipher
- **Key Storage**: macOS Keychain (service: `ai-chat-terminal-db-key`)
- **Key Derivation**: PBKDF2_HMAC_SHA512 with 64,000 iterations
- **HMAC**: HMAC_SHA512 for authentication

## Reporting a Vulnerability

If you discover a security vulnerability, please follow responsible disclosure:

### DO

1. **Email security issues privately** to: mschenk.pda@gmail.com
2. **Include detailed description**:
   - Type of vulnerability (data leak, privilege escalation, etc.)
   - Steps to reproduce
   - Affected versions
   - Potential impact
3. **Allow 48 hours for initial response**
4. **Do not disclose publicly** until patch is released

### DO NOT

- Open public GitHub issues for security vulnerabilities
- Exploit vulnerabilities beyond proof-of-concept
- Access data that doesn't belong to you

## Response Timeline

- **Initial response**: Within 48 hours
- **Severity assessment**: Within 5 business days
- **Patch release**: Within 30 days (critical issues: within 7 days)
- **Public disclosure**: After patch is released and users have time to update

## Security Best Practices for Users

### API Key Protection

```bash
# NEVER commit your API key to version control
echo "OPENAI_API_KEY=sk-..." >> ~/.aichat/.env

# Verify .env is in .gitignore
grep ".env" .gitignore
```

### Database Encryption

Encryption is automatic if SQLCipher is installed:

```bash
# Check if encryption is active
python3 << EOF
from pathlib import Path
import sys
sys.path.insert(0, str(Path.home() / '.aichat'))
from encryption_manager import EncryptionManager
print(f"Encryption: {'✅ Active' if EncryptionManager().is_encryption_available() else '❌ Not available'}")
EOF
```

### Verify Installation Integrity

```bash
# Official installation script uses HTTPS
curl -fsSL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | zsh

# Or clone and inspect before running
git clone https://github.com/martinschenk/ai-chat-terminal.git
cd ai-chat-terminal
less install.sh  # Review before executing
zsh install.sh
```

### Secure Uninstallation

The uninstaller preserves your data by default:

```bash
# Standard uninstall (keeps ~/.aichat/)
curl -fsSL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/uninstall.sh | zsh

# Complete removal (deletes all data)
rm -rf ~/.aichat  # Only if you want to delete private data!
```

## Known Security Considerations

### 1. OpenAI API Key Storage

- API key stored in `~/.aichat/.env` (plain text)
- Protected by macOS file permissions (chmod 600)
- Alternative: Use environment variable `OPENAI_API_KEY`

### 2. Chat History Sent to OpenAI

- Last 20 messages sent to OpenAI for context
- Does NOT include messages tagged with `privacy_category`
- To disable context: Set `AI_CHAT_CONTEXT_WINDOW=0` (not recommended)

### 3. Local Ollama Model

- Qwen 2.5 Coder runs locally (no network calls)
- Model downloaded from Ollama registry (verify: `ollama pull qwen2.5-coder:7b`)
- Checksums verified by Ollama automatically

### 4. Daemon Process

- `chat_daemon.py` runs in background for performance
- Process visible in Activity Monitor as "Python"
- Restart: `pkill -9 -f chat_daemon.py && chat`

## Threat Model

### In Scope

- Data exfiltration to OpenAI (mitigated by keyword detection)
- Unauthorized database access (mitigated by encryption)
- API key leakage (mitigated by file permissions)

### Out of Scope

- Physical access to unlocked Mac (use FileVault + password)
- Malicious Ollama models (trust Ollama registry)
- OpenAI API vulnerabilities (report to OpenAI)
- macOS Keychain vulnerabilities (report to Apple)

## Security Updates

Subscribe to security updates:

- **GitHub Watch**: Click "Watch" → "Custom" → "Releases only"
- **GitHub Security Advisories**: Automatically notified if repo is starred
- **RSS Feed**: `https://github.com/martinschenk/ai-chat-terminal/releases.atom`

## Third-Party Dependencies

AI Chat Terminal relies on:

- **OpenAI API** (cloud): Subject to OpenAI's security policies
- **Ollama** (local): Open-source, auditable
- **SQLCipher** (local): Industry-standard encryption
- **Python libraries**: `openai`, `requests`, `rich` (audited regularly)

To review dependencies:

```bash
pip3 list | grep -E "openai|requests|rich|sqlcipher"
```

## License

Security policy licensed under MIT License (same as project).

---

**Last Updated**: 2025-10-20
**Contact**: mschenk.pda@gmail.com
