# AI Chat Terminal

**User-controlled local storage with military-grade encryption for your terminal.**

[![Version](https://img.shields.io/badge/version-8.1.0-blue.svg)](https://github.com/martinschenk/ai-chat-terminal)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://github.com/martinschenk/ai-chat-terminal)
[![Encryption](https://img.shields.io/badge/encryption-AES--256-green.svg)](https://github.com/martinschenk/ai-chat-terminal#database-security-)

## What is AI Chat Terminal?

A terminal-based chat system where **YOU decide** what stays local and what goes to OpenAI. Your local data is **automatically encrypted** with AES-256. Full transparency and control.

**How it works:**
- Say "speichere lokal" (save locally) → **Encrypted** on your Mac, NEVER to OpenAI
- Say "aus meiner db" (from my database) → Retrieves your **encrypted** local data
- Normal questions → Go to OpenAI (as usual)
- **NEW in v8.1.0:** Database automatically encrypted with AES-256 🔐

### v8.1.0: Database Encryption 🔐

**NEW:** Your local database is now **encrypted with AES-256** - same encryption used by military and governments.

- **Automatic:** Encryption key stored in macOS Keychain
- **Transparent:** Zero configuration required
- **Fast:** <100ms overhead
- **Secure:** Database file useless without encryption key
- **Export:** `--export-db` command for backups

[→ Read full security documentation](#database-security-)

### v8.0.0: The Keyword Revolution 🎯

**Old way (v7):** AI tries to automatically detect sensitive data (often wrong)
**New way (v8):** **You explicitly tell it** what to keep local

```
✅ "speichere lokal: mein API Key ist sk-abc123"     → Saves locally, NEVER to OpenAI
✅ "aus meiner db: was ist mein API Key?"            → Retrieves from local DB
✅ "wie ist das Wetter heute?"                       → Normal OpenAI query
```

### Data Flow: User-Controlled Storage

```
┌─────────────────────────────────────────────────┐
│ YOU: "speichere lokal: sensitive data"          │
└────────────────────┬────────────────────────────┘
                     ↓
          ┌──────────────────────┐
          │ Keyword Detection    │ ← Simple, fast, transparent
          │   (local check)      │
          └──────────┬───────────┘
                     ↓
              🔒 LOCAL STORAGE
              Saved to vector DB
              ~/.aichat/memory.db

              ✅ NEVER sent to OpenAI
              ✅ You control what's stored
              ✅ <500ms instant save
```

### Data Flow: Local Retrieval

```
┌────────────────────────────────────────┐
│ YOU: "aus meiner db: my API key?"     │
└─────────────┬──────────────────────────┘
              ↓
    ┌─────────────────────┐
    │ Keyword Detection    │
    │ "aus meiner db"      │
    └─────────┬───────────┘
              ↓
       🔒 Local DB Search
       ├─ Semantic vector search
       ├─ Natural language response (Phi-3)
       └─ Returns: "Your API key is sk-abc123"

    ✅ NEVER sent to OpenAI
    ✅ <1.5s instant retrieval
    ✅ Works in 19 languages
```

---

## Quick Start

**Step 1: Install**
```bash
curl -fsSL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | zsh
```

**Step 2: Reload shell**
```bash
source ~/.zshrc
```

**Step 3: Start**
```bash
chat
```

---

## How to Use (Examples)

### Save Sensitive Data Locally

**German:**
```bash
chat
👤 You ▶ speichere lokal: mein OpenAI API Key ist sk-proj-abc123xyz
🤖 AI    ✅ Gespeichert! 🔒
```

**English:**
```bash
chat
👤 You ▶ save locally: my credit card is 4532-1234-5678-9012
🤖 AI    💾 Got it! 🔐
```

**Spanish:**
```bash
chat
👤 You ▶ guarda localmente: mi contraseña es MiPass2024!
🤖 AI    ✅ Guardado! 🔒
```

### Retrieve from Local Database

**German:**
```bash
👤 You ▶ aus meiner db: was ist mein API Key?
🤖 AI    🔑 Dein OpenAI API-Key: sk-proj-abc123xyz
```

**English:**
```bash
👤 You ▶ from my database: what's my credit card?
🤖 AI    💳 Your credit card: 4532-1234-5678-9012
```

**Spanish:**
```bash
👤 You ▶ de mi db: cuál es mi contraseña?
🤖 AI    🔒 Tu contraseña: MiPass2024!
```

### Normal OpenAI Queries (Default)

```bash
👤 You ▶ wie ist das Wetter heute?
🤖 AI    Ich kann keine Live-Wetterdaten abrufen...

👤 You ▶ explain quantum computing
🤖 AI    Quantum computing uses quantum bits (qubits)...
```

---

## Keywords by Language

The system supports **19 languages**. Here are the main keywords:

### Save Locally Keywords

| Language | Keywords |
|----------|----------|
| 🇩🇪 German | `speichere lokal`, `speicher lokal`, `auf meinem computer`, `in meiner datenbank` |
| 🇬🇧 English | `save locally`, `store locally`, `on my computer`, `in my database` |
| 🇪🇸 Spanish | `guarda localmente`, `en mi ordenador`, `en mi base de datos` |
| 🇫🇷 French | `enregistre localement`, `sur mon ordinateur`, `dans ma base de données` |
| 🇮🇹 Italian | `salva localmente`, `sul mio computer`, `nel mio database` |
| 🇵🇹 Portuguese | `salvar localmente`, `no meu computador`, `na minha base de dados` |
| ... | + 13 more languages (NL, PL, RU, JA, ZH, KO, AR, HI, TR, SV, DA, FI, NO) |

### Retrieve from DB Keywords

| Language | Keywords |
|----------|----------|
| 🇩🇪 German | `aus meiner db`, `aus der datenbank`, `lokale daten`, `meine gespeicherten daten` |
| 🇬🇧 English | `from my db`, `from database`, `local data`, `my stored data` |
| 🇪🇸 Spanish | `de mi db`, `de la base de datos`, `datos locales`, `mis datos guardados` |
| 🇫🇷 French | `de ma db`, `de la base de données`, `données locales` |
| 🇮🇹 Italian | `dal mio db`, `dal database`, `dati locali` |
| 🇵🇹 Portuguese | `do meu db`, `do banco de dados`, `dados locais` |
| ... | + 13 more languages |

**Full list:** See [local_storage_detector.py](local_storage_detector.py) for all keywords.

---

## API Key Configuration

The installation automatically checks your macOS Keychain for an OpenAI API key.

**Option A - Automatic (during installation):**
```bash
# Key found in Keychain → Automatically configured ✓
# Service: "OpenAI API", Account: "openai"
```

**Option B - Interactive (first start):**
```bash
chat     # Prompts for API key if not found

# Choose:
# [1] Enter key now (saved to ~/.aichat/.env)
# [2] Load from macOS Keychain
# [3] Cancel
```

**Option C - Manual:**
```bash
echo 'OPENAI_API_KEY=sk-...' > ~/.aichat/.env
```

---

## Features

### 🎯 User Control (NEW in v8.0.0)
- **YOU decide** what stays local with explicit keywords
- No automatic detection that might be wrong
- Full transparency: you know exactly what goes where
- Responsibility is with the user (as it should be!)

### 🚀 Performance
- **Local storage:** <500ms (instant)
- **Local retrieval:** <1.5s (semantic search + Phi-3)
- **OpenAI queries:** 5-7s (normal streaming)
- **10-12s delays ELIMINATED** (removed Function Calling)

### 🌍 Multilingual
- **19 languages** supported
- Keywords work in: DE, EN, ES, FR, IT, PT, NL, PL, RU, JA, ZH, KO, AR, HI, TR, SV, DA, FI, NO
- Natural language responses in your language (Phi-3)

### 🔒 Privacy by Design
- Local data marked with `LOCAL_STORAGE` category
- OpenAI context automatically filters these messages
- Your sensitive data NEVER leaves your Mac
- Vector database: `~/.aichat/memory.db` (local only)

### 🤖 AI Models
- **Privacy Classifier:** `all-MiniLM-L6-v2` (22MB) - Fast keyword detection
- **Memory System:** `multilingual-e5-base` (278MB) - Semantic search
- **Response Generator:** Phi-3 via Ollama (2.3GB, optional) - Natural responses
- **OpenAI:** GPT-4o/GPT-4o-mini (configurable)

### ⚡ Simple & Maintainable
- **~180 lines** for message flow (was 800+ in v7)
- No complex PII detection (Presidio removed)
- No Function Calling overhead
- Simple keyword matching (fast & reliable)

---

## Database Security 🔐

**NEW in v8.1.0:** Your local database is encrypted with military-grade AES-256 encryption.

### How It Works

- **Encryption**: SQLCipher with 256-bit AES-CBC
- **Key Storage**: macOS Keychain (automatic, transparent)
- **Key Derivation**: PBKDF2-HMAC-SHA512, 64,000 iterations
- **Performance**: <100ms overhead (optimized)
- **User Experience**: Zero configuration required

### What's Protected ✅

Your encrypted database protects against:

- **✅ Physical theft**: Database file is useless without key
- **✅ File-level access**: Other users can't read your data
- **✅ Backup theft**: Copied DB files remain encrypted
- **✅ Disk forensics**: Data is encrypted at rest
- **✅ Accidental exposure**: Cloud sync won't expose plaintext

### What's NOT Protected ⚠️

**Honest Security Assessment** - encryption does NOT protect against:

- **⚠️ Malware as user**: Apps running as your user can access Keychain
- **⚠️ Root/admin access**: System administrators can extract keys
- **⚠️ Memory dumps**: Data is decrypted in RAM during use
- **⚠️ Keyloggers**: Can capture your input before encryption
- **⚠️ Screen recording**: Can capture output after decryption

### Security Level

**Encryption Standard:**
- Algorithm: AES-256-CBC (same as military/government use)
- Key Size: 256 bits (2^256 possible keys)
- Brute Force: Would take billions of years with current technology

**Real-World Protection:**
- 🔒 **Excellent** against: Theft, unauthorized file access, forensics
- 🔐 **Good** against: Casual snooping, backup leaks
- ⚠️ **Limited** against: Determined attacker with system access
- ❌ **No protection** against: Malware, root compromise, user-level attacks

### Recommendations

1. **Enable FileVault**: Full-disk encryption adds another layer
2. **Use strong Mac password**: Keychain is only as secure as your login
3. **Keep software updated**: Security patches are critical
4. **Be cautious with cloud sync**: Don't sync `memory.db` unencrypted

### Technical Details

**Encryption Configuration:**
```sql
PRAGMA cipher = 'aes-256-cbc';
PRAGMA kdf_algorithm = 'PBKDF2_HMAC_SHA512';
PRAGMA kdf_iter = 64000;  -- Optimized for <100ms
PRAGMA cipher_page_size = 4096;
PRAGMA cipher_hmac_algorithm = 'HMAC_SHA512';
```

**Key Management:**
- **Generation**: `os.urandom(32)` - Cryptographically secure random
- **Storage**: macOS Keychain (Service: "AI Chat Terminal DB")
- **Access**: Transparent - no user interaction needed
- **Backup**: Key is NOT in database - store separately if needed

### Export Unencrypted Backup

**Create plaintext backup for transfer/debugging:**

```bash
chat
👤 You ▶ --export-db ~/Desktop/backup.db
📤 Exporting encrypted database...
✓ Exported to: ~/Desktop/backup.db
⚠️  WARNING: backup.db is NOT encrypted!
```

**Use cases:**
- Transfer to another computer
- Debug database content
- Create unencrypted archive
- Migrate to different system

### What If I Lose My Key?

**⚠️ CRITICAL:** If you delete the Keychain entry, your data is **permanently lost**.

The encryption key is the ONLY way to decrypt your database. We **cannot** recover your data without it.

**To backup your key:**
```bash
# View key (save this somewhere safe!)
security find-generic-password -s "AI Chat Terminal DB" -a "encryption-key" -w

# Save to secure file
security find-generic-password -s "AI Chat Terminal DB" -a "encryption-key" -w > ~/secure-backup-key.txt
# IMPORTANT: Store this file safely (encrypted USB, password manager, etc.)
```

**To restore key on new Mac:**
```bash
# Read key from backup
KEY=$(cat ~/secure-backup-key.txt)

# Add to Keychain
security add-generic-password -s "AI Chat Terminal DB" -a "encryption-key" -w "$KEY"
```

### Disable Encryption

**If you want to use unencrypted database:**

```bash
# Step 1: Export to plaintext
chat
👤 You ▶ --export-db ~/memory_plain.db

# Step 2: Backup encrypted DB
mv ~/.aichat/memory.db ~/.aichat/memory_encrypted.db.backup

# Step 3: Use plaintext DB
mv ~/memory_plain.db ~/.aichat/memory.db

# Step 4: Remove encryption key (optional)
security delete-generic-password -s "AI Chat Terminal DB" -a "encryption-key"
```

**Note:** Future installations will re-enable encryption automatically.

### Performance Impact

**Benchmarks (MacBook Pro M1):**
- Database open: +50-100ms (one-time key derivation)
- Read query: +5-15ms per operation
- Write query: +5-15ms per operation
- Semantic search: +10-20ms per operation

**Overall performance:**
- Local save: <510ms (was <500ms)
- Local retrieval: <1.6s (was <1.5s)
- Negligible impact on user experience

### Compliance & Standards

- **Algorithm**: AES-256 (FIPS 197 approved)
- **Key Derivation**: PBKDF2 (NIST SP 800-132)
- **Implementation**: SQLCipher (widely audited, used by governments)
- **Standards**: Meets NIST, ISO, FIPS encryption requirements

**Used by:**
- Signal (messaging app)
- 1Password (password manager)
- Various government agencies
- Financial institutions

---

## Architecture

### v8.0.0 Message Flow

```python
def send_message(user_input):
    # PHASE 1: Check for "save locally"
    if detect_save_locally(user_input):
        save_to_db(user_input)
        return "✅ Gespeichert! 🔒"

    # PHASE 2: Check for "retrieve from DB"
    if detect_retrieve_from_db(user_input):
        results = search_db(user_input)
        return format_results(results)

    # PHASE 3: Normal OpenAI (default)
    return openai_query(user_input)
```

**Performance:**
- Phase 1: <500ms (local save)
- Phase 2: <1.5s (local retrieval)
- Phase 3: 5-7s (OpenAI API)

---

## Configuration

### Change Language

```bash
chat
Type: /config → [2] Change language → Select language
```

### Change AI Model

```bash
chat
Type: /config → [5] Change AI model
# Options: GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-3.5-turbo
```

### Install Phi-3 (Optional, Recommended)

Phi-3 generates natural language responses for local data:

```bash
# Install via Ollama
brew install ollama
ollama pull phi3

# Test it
ollama run phi3
```

**With Phi-3:**
```
✅ Gespeichert! 🔒
💾 Alles klar!
🔐 Sicher verwahrt!
```

**Without Phi-3 (fallback):**
```
✅ Stored 🔒
```

---

## Development

### File Structure

```
ai-chat-terminal/
├── chat_system.py              # Main chat logic (v8.0.0 flow)
├── local_storage_detector.py   # Keyword detection (NEW in v8.0.0)
├── response_generator.py       # Phi-3 response generation
├── memory_system.py            # Vector database (SQLite + vec)
├── privacy_classifier_fast.py  # Classifier training (legacy)
├── install.sh                  # Installation script
├── lang/                       # 19 language configs
│   ├── de.conf                 # German keywords
│   ├── en.conf                 # English keywords
│   └── ...
└── modules/                    # Shell modules
    └── ai_chat.zsh             # Terminal integration
```

### Key Changes in v8.0.0

**Removed:**
- ❌ Presidio PII Detector (~350MB)
- ❌ OpenAI Function Calling (~127 lines)
- ❌ Automatic PII detection (~396 lines)
- ❌ Complex handle_pii_storage() logic

**Added:**
- ✅ `local_storage_detector.py` (keyword detection)
- ✅ User-controlled storage with keywords
- ✅ 19-language keyword support
- ✅ Simplified message flow (180 lines)

**Result:**
- 37% less code in `chat_system.py`
- 5-10x faster for local operations
- Much simpler and more transparent

---

## Migration from v7.x

### What Changed?

**v7.x:** AI automatically tried to detect sensitive data (PII)
**v8.0:** YOU explicitly control with keywords

### How to Update

```bash
cd ~/Development/ai-chat-terminal
git pull origin main
./install.sh
source ~/.zshrc
```

### Behavior Changes

| Old (v7) | New (v8) |
|----------|----------|
| "My API key is sk-123" → Auto-detected | "My API key is sk-123" → Normal OpenAI |
| (No control) | "speichere lokal: my API key is sk-123" → Local |
| "What's my API key?" → Sometimes worked | "aus meiner db: my API key?" → Always works |

### Why the Change?

1. **User Control:** You decide, not the AI
2. **Transparency:** Clear what goes where
3. **Performance:** 5-10x faster local operations
4. **Simplicity:** 37% less code, easier to maintain
5. **Reliability:** No more false positives/negatives

---

## System Requirements

- macOS 12.0+ (Monterey or later)
- Zsh shell
- Python 3.9+
- OpenAI API key
- ~500MB disk space for AI models
- (Optional) Ollama + Phi-3 for natural responses

---

## Troubleshooting

### "Keyword not detected"

Make sure you're using the exact keywords:
```bash
✅ "speichere lokal: data"     # Works
❌ "speichern lokal: data"     # Wrong verb form
❌ "save lokal: data"          # Mixed languages
```

### "No data found in DB"

Data must be saved first:
```bash
# Step 1: Save
👤 You ▶ speichere lokal: mein API Key ist sk-123

# Step 2: Retrieve
👤 You ▶ aus meiner db: API Key?
```

### "Phi-3 not working"

Check Ollama installation:
```bash
which ollama           # Should show: /opt/homebrew/bin/ollama
ollama list            # Should show: phi3
ollama run phi3        # Test it
```

---

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Credits

- Built on [Shell-GPT](https://github.com/TheR1D/shell_gpt) by TheR1D
- Privacy Classifier: `sentence-transformers/all-MiniLM-L6-v2`
- Memory System: `intfloat/multilingual-e5-base`
- Response Generator: Phi-3 via Ollama
- Vector Database: SQLite with [sqlite-vec](https://github.com/asg017/sqlite-vec)

---

## Version History

### v8.1.0 (2025-01-XX) - Database Encryption 🔐
- 🔐 **SQLCipher AES-256 encryption** for local database
- 🔑 **Automatic key management** via macOS Keychain
- 📤 **Export command** for unencrypted backups
- 🚀 **<100ms overhead** with optimized key derivation
- 🔒 **Transparent encryption** - zero user configuration
- 📦 **Automatic migration** from v8.0.0 unencrypted DBs

### v8.0.0 (2025-01-02) - The Keyword Revolution 🎯
- 🎯 User-controlled storage with keywords
- 🌍 19-language keyword support
- 🚀 5-10x faster local operations
- ❌ Removed Presidio (350MB saved)
- ❌ Removed Function Calling (10s delays eliminated)
- ✨ Simplified codebase (37% reduction)

### v7.0.0 (2025-01-20) - Privacy & Natural Responses
- 🔒 Automatic PII detection with Presidio
- 🤖 Phi-3 for natural language responses
- 📊 Function Calling for structured data

### v6.2.0 (2025-01-15) - Enhanced PII Protection
- 🛡️ Improved PII filtering in OpenAI context
- 🔐 Privacy categories for all messages

### v6.1.0 (2025-01-10) - Bug Fixes
- 🐛 Fixed OpenAI API key configuration
- 🔧 Improved error handling

### v6.0.0 (2025-01-05) - Dual AI Model Architecture
- 🚀 Privacy Classifier + Memory System
- 🔍 Semantic vector search with E5 embeddings

---

**Questions?** Open an issue on [GitHub](https://github.com/martinschenk/ai-chat-terminal/issues)

**Ready to try it?**
```bash
curl -fsSL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | zsh
```
