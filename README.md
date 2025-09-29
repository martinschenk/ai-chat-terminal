# AI Chat Terminal - Privacy-First AI Assistant

Terminal-based AI assistant with intelligent privacy routing that keeps sensitive data local while using OpenAI for general queries.

[![Version](https://img.shields.io/badge/version-6.1.0-blue.svg)](https://github.com/martinschenk/ai-chat-terminal)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20|%20Linux-lightgrey.svg)](https://github.com/martinschenk/ai-chat-terminal)
[![Privacy](https://img.shields.io/badge/privacy-first-green.svg)](https://github.com/martinschenk/ai-chat-terminal)

## Smart Privacy Routing

AI-based classification system using dual AI models to route conversations based on privacy level:

### 🧠 **Dual AI Architecture:**
1. **🔍 Privacy Classifier**: `all-MiniLM-L6-v2` - Ultra-fast privacy detection (40% faster)
2. **💾 Memory System**: `multilingual-e5-small` - Multilingual semantic search in local database

### 📊 **Privacy Categories:**
- **🔒 SENSITIVE** (Credit cards, passwords, API keys) → **100% Local Processing**
- **🏢 PROPRIETARY** (Business secrets, internal data) → **100% Local Processing**
- **👤 PERSONAL** (Names, family, appointments) → **100% Local Processing**
- **🌐 PUBLIC** (General knowledge, tutorials) → **OpenAI Processing**

**Result**: Local processing for sensitive data, OpenAI processing for general queries.

## 🆕 What's New in v6.1.0

### ✅ **Critical Bug Fixes:**
- **Fixed duplicate responses** - OpenAI answers no longer appear twice
- **Enhanced search accuracy** - Personal data queries now find stored information reliably
- **Improved classification** - Historical questions (birth dates, events) correctly route to OpenAI
- **Better language detection** - Automatic German/English response language matching

### 🔑 **New Feature: OpenAI API Key Management**
- **Secure configuration** via `/config` menu option [6]
- **Format validation** (ensures keys start with 'sk-' and proper length)
- **Safe display** (shows only first 8 characters for verification)
- **Instant activation** for new chats

### 🧠 **Enhanced AI Classification:**
- **20+ famous people** added for historical question recognition
- **Cross-language patterns** for German/English historical queries
- **Improved confidence scoring** for better routing decisions

---

## 🎯 How It Works - Dual AI Architecture

```
┌─────────────────┐    ┌───────────────────────────────┐    ┌─────────────────┐
│   Your Query    │───▶│       🧠 AI MODEL #1          │───▶│   Routing       │
│                 │    │   Privacy Classifier          │    │   Decision      │
│ "My card is     │    │ all-MiniLM-L6-v2 (384D)     │    │ SENSITIVE (85%) │
│  1234-5678"     │    │ Trained on 160+ examples     │    │                 │
└─────────────────┘    └───────────────────────────────┘    └─────────────────┘
                                                                        │
                                                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          🔐 LOCAL PROCESSING                               │
│                                                                             │
│    ┌───────────────────────────────┐    ┌──────────────────────────────┐   │
│    │       💾 AI MODEL #2          │    │        ⚡ FEATURES           │   │
│    │     Memory System             │    │                              │   │
│    │ multilingual-e5-small (384D) │    │  🔍 Semantic Search          │   │
│    │ Vector Database + Embeddings │    │  💾 Secure Storage           │   │
│    │                               │    │  🗑️ Smart Deletion          │   │
│    │ • Cross-language search       │    │  📝 Intent Detection         │   │
│    │ • Importance scoring          │    │  🛡️ Template Responses       │   │
│    │ • Auto-cleanup               │    │  ❌ NEVER sent to OpenAI    │   │
│    └───────────────────────────────┘    └──────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────────────┐
                    │          🌐 OPENAI ROUTE           │
                    │                                     │
                    │ PUBLIC queries like:                │
                    │ • "How does quantum physics work?"  │
                    │ • "Explain machine learning"        │
                    │ • "What's the weather like?"        │
                    │                                     │
                    │ ✅ Full AI capabilities             │
                    │ ⚡ OpenAI API processing            │
                    └─────────────────────────────────────┘
```

---

## Table of Contents

- [🔒 Privacy Features](#-privacy-features)
- [⚡ Quick Start](#-quick-start)
- [🧠 Smart Memory System](#-smart-memory-system)
- [📊 Flow Diagrams](#-flow-diagrams)
- [🌍 Multi-Language Support](#-multi-language-support)
- [⚙️ Installation](#-installation)
- [💡 Usage Examples](#-usage-examples)
- [🛠️ Configuration](#-configuration)
- [❓ FAQ & Troubleshooting](#-faq--troubleshooting)

---

## 🔒 Privacy Features

### ✅ What Stays Local (NEVER sent to OpenAI)
- **💳 Financial**: Credit cards, bank details, account numbers
- **🔑 Security**: Passwords, API keys, PINs, tokens
- **🏢 Business**: Company secrets, internal workflows, client data
- **👥 Personal**: Family info, private contacts, personal notes

### ✅ What Gets Enhanced by OpenAI
- **🌍 Knowledge**: Geography, history, science, math
- **💡 Explanations**: Complex concepts, how-tos, tutorials
- **🔍 Research**: Current events, technical questions
- **🎯 Analysis**: Code reviews, problem solving

### 🛡️ Triple-Layer Protection
1. **🧠 AI Classification**: Semantic understanding of content
2. **🔒 Local Processing**: Sensitive data never transmitted
3. **🗑️ Secure Deletion**: "Delete my credit card info" works instantly

---

## ⚡ Quick Start

**60-second setup:**

```bash
# 1. Install (auto-detects existing 'ai' command conflicts)
curl -sL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | bash

# 2. Reload shell
source ~/.zshrc

# 3. Start chatting
chat
```

**First run setup:**
1. Enter your [OpenAI API key](https://platform.openai.com/api-keys)
2. Choose language (19 supported + regional dialects)
3. Select AI model (gpt-3.5-turbo recommended for cost)

**🎉 That's it! Smart Privacy Routing is automatically active.**

---

## 🧠 Technical Architecture - Dual AI Models

### 1️⃣ **Privacy Classifier** (`privacy_classifier_fast.py`)
- **Model**: `intfloat/multilingual-e5-small` (384-dimensional embeddings)
- **Purpose**: Classifies user input into 4 privacy levels
- **Training**: 160+ examples across all categories (0.7s training time)
- **Performance**: <50ms classification per message
- **Languages**: Works in 100+ languages automatically

### 2️⃣ **Memory System** (`memory_system.py`)
- **Model**: `intfloat/multilingual-e5-small` (same model, different instance)
- **Purpose**: Semantic search in local SQLite database
- **Features**: Vector similarity search + graceful degradation
- **Storage**: All local conversations with embeddings
- **Cross-lingual**: Query in any language, find content in any other

### 🔄 **Smart Training Process:**
```bash
# First run (automatic):
Creating category embeddings (AI training)...
  Processing SENSITIVE: 52 examples     # Credit cards, passwords, APIs
  Processing PROPRIETARY: 32 examples   # Business secrets, internal data
  Processing PERSONAL: 36 examples      # Names, family, appointments
  Processing PUBLIC: 40 examples        # General knowledge, tutorials
AI training completed in 0.70 seconds!

# Subsequent runs (cached):
Loading existing category embeddings...  # Instant loading
```

### Dual-Layer Memory Architecture
- **Short-term**: Recent context (5-50 messages) sent to OpenAI
- **Long-term**: SQLite vector database with semantic search
- **Cross-lingual**: Query in German, find English content
- **Auto-cleanup**: Keeps important data, removes clutter

### Memory Intelligence
```bash
# Storage Examples (100% Local)
👤 "My credit card is 4532-1234-5678-9012"
🤖 "Your sensitive data has been securely saved to the local database."

👤 "Company Q4 revenue target is $2M"
🤖 "The proprietary information has been stored locally."

# Query Examples (100% Local)
👤 "What's my credit card number?"
🤖 "Your credit card number is 4532-1234-5678-9012."

👤 "What was our revenue target?"
🤖 "Your company Q4 revenue target is $2M."
```

### Secure Deletion
```bash
# Delete specific data
👤 "Delete my credit card information"
🤖 "I have deleted 3 entries from the local database."

# Delete by pattern
👤 "Delete card 4532"
🤖 "I have deleted 1 entry from the local database."
```

---

## 🌍 Multi-Language Support

**19 Languages + Regional Dialects:**

| Language | Dialects | Examples |
|----------|----------|----------|
| **🇩🇪 German** | Hochdeutsch, Schwäbisch, Bayerisch, Sächsisch | "Meine Kreditkarte ist..." |
| **🇪🇸 Spanish** | Mexican, Argentinian, Colombian, Chilean, Andaluz | "Mi tarjeta de crédito es..." |
| **🇺🇸 English** | Standard | "My credit card is..." |
| **🇫🇷 French** | Standard | "Ma carte de crédit est..." |

Plus: Italian, Chinese, Hindi, Portuguese, Russian, Japanese, Korean, Arabic, Dutch, Swedish, Norwegian, Danish, Finnish, Polish

**🎯 Smart Privacy works in ALL languages!**

---

## ⚙️ Installation

### System Requirements
- **macOS** 10.14+ or **Linux** (Ubuntu, CentOS, etc.)
- **Python 3.7+** (usually pre-installed)
- **OpenAI API Key** ([get yours here](https://platform.openai.com/api-keys))
- **$5 minimum** OpenAI credit

### Auto-Install Dependencies
The installer automatically handles:
- OpenAI Python SDK
- sentence-transformers (MiniLM + E5 models for dual architecture)
- scikit-learn (classification algorithms)
- sqlite-vec (if available for vector search)

### Manual Installation (Advanced)
```bash
# 1. Clone repository
git clone https://github.com/martinschenk/ai-chat-terminal.git
cd ai-chat-terminal

# 2. Run installer
./install.sh

# 3. Setup shell integration
echo "source ~/.aichat/aichat.zsh" >> ~/.zshrc
echo "alias chat='noglob ai_chat_function'" >> ~/.zshrc
source ~/.zshrc
```

---

## 💡 Usage Examples

### 🔒 Privacy in Action

```
/config = settings | ESC/exit = quit

# SENSITIVE - Processed 100% Locally
👤 You ▶ My credit card is 4532-1234-5678-9012
🤖 AI ▶ Your sensitive data has been securely saved to the local database.
      [🔒 NEVER sent to OpenAI]

# PROPRIETARY - Business Secrets Stay Local
👤 You ▶ Our Q2 revenue target is $5 million confidential
🤖 AI ▶ The proprietary information has been stored locally.
      [🏢 Company data protected]

# PUBLIC - Full OpenAI Intelligence
👤 You ▶ Explain machine learning algorithms
🤖 AI ▶ Machine learning algorithms are computational methods that enable
      computers to learn and make decisions from data without being explicitly
      programmed for every scenario. Here are the main categories:

      1. **Supervised Learning**: Uses labeled training data...
      [🌐 Full OpenAI processing]
```

### 🧠 Memory & Retrieval

```
# Store sensitive data
👤 You ▶ My bank PIN is 9876
🤖 AI ▶ Your sensitive data has been securely saved to the local database.

# Query days later
👤 You ▶ What's my bank PIN?
🤖 AI ▶ Your bank PIN is 9876.
      [Retrieved from local database - never touched OpenAI servers]

# Secure deletion
👤 You ▶ Delete my bank PIN information
🤖 AI ▶ I have deleted 2 entries from the local database.
```

### 🌍 Multi-Language Privacy

```
# German privacy
👤 Du ▶ Meine Kreditkartennummer ist 1234-5678
🤖 KI ▶ Ihre sensiblen Daten wurden sicher in der lokalen Datenbank gespeichert.

# Spanish privacy
👤 Tú ▶ Mi contraseña es secreto123
🤖 IA ▶ Sus datos sensibles han sido guardados de forma segura en la base de datos local.

# Cross-language retrieval
👤 You ▶ What was my German credit card?
🤖 AI ▶ Your credit card number is 1234-5678.
      [Found German entry, responded in English]
```

---

## 🛠️ Configuration

### Interactive Config Menu
```bash
chat
/config  # or just type 'config' in chat
```

**Configuration Options:**
1. **Change command** (`chat`, `ai`, `ask`, or custom)
2. **Select language** (19 languages + dialects)
3. **Toggle ESC key** (exit chat or disable)
4. **AI model** (gpt-4o, gpt-4o-mini, gpt-3.5-turbo)
5. **Context window** (5-50 messages for cost control)
6. **🔑 OpenAI API key** (secure configuration, format validation)
7. **Memory system** (search, stats, cleanup)
8. **Clear cache** (remove temporary chat files)
9. **About & version** (system information)
10. **Back to chat** (return to conversation)
11. **Complete uninstall** (removes all traces)

### Cost Optimization

| Model | Cost per 1K tokens | Best for |
|-------|-------------------|----------|
| **gpt-3.5-turbo** | $0.0010 | Daily use, cost-conscious |
| **gpt-4o-mini** | $0.0015 | Balanced performance |
| **gpt-4o** | $0.0025 | Complex tasks, best quality |

**💡 Tip**: Smart Privacy Routing reduces API costs by 70-80% by processing sensitive queries locally!

---

## 📊 How It Works - Dual AI Architecture

### 🧠 Two Specialized Models for Optimal Performance

```
                    ┌─────────────────┐
                    │   User Input    │
                    └─────────┬───────┘
                              │
                    ┌─────────▼───────┐
                    │ Model #1:       │
                    │ Privacy         │
                    │ Classifier      │
                    │                 │
                    │ all-MiniLM-L6   │
                    │ • 22MB (fast)   │
                    │ • 6 layers      │
                    │ • Classification│
                    └─────────┬───────┘
                              │
                    ┌─────────▼───────┐
                    │ Binary Router   │
                    │ PRIVATE → Local │
                    │ PUBLIC → OpenAI │
                    └─────┬───────┬───┘
                          │       │
                     PRIVATE    PUBLIC
                          │       │
                          ▼       ▼
              ┌─────────────┐   ┌─────────────┐
              │ Model #2:   │   │ OpenAI API  │
              │ Memory      │   │ Full power  │
              │ Search      │   │ for general │
              │             │   │ knowledge   │
              │ E5-small    │   └─────────────┘
              │ • 120MB     │
              │ • 12 layers │
              │ • 100 langs │
              │ • Semantic  │
              └─────────────┘
```

### 🔄 Storage Flow (e.g., "My credit card is 4532-1234")
```
User Input ──▶ MiniLM Classifier ──▶ SENSITIVE detected ──▶ Store in Local DB
     │               │                       │                      │
     │         (all-MiniLM-L6)          (High confidence)     (SQLite + metadata)
     │               │                       │                      │
     ▼               ▼                       ▼                      ▼
"My credit      Fast Analysis         Route Locally = True    ✅ Saved with category
 card is..."    Category: SENSITIVE    Intent: STORAGE        metadata: {"privacy_category": "SENSITIVE"}
                Never sent to OpenAI                         Response: "Saved securely!"
```

### 🔍 Query Flow (e.g., "What's my credit card?")
```
User Query ──▶ MiniLM Classifier ──▶ SENSITIVE detected ──▶ E5 Semantic Search
     │               │                       │                      │
     │         (all-MiniLM-L6)          (Fast routing)        (multilingual-e5)
     │               │                       │                      │
     ▼               ▼                       ▼                      ▼
"What's my      Privacy Analysis     Route Locally = True    Search by: "credit card"
 credit card?"  Category: SENSITIVE   Intent: QUERY          Found: "4532-1234..."
                Never sent to OpenAI                         Response: "Your card is 4532-1234"
```

### 🌐 Public Flow (e.g., "Explain quantum physics")
```
User Query ──▶ MiniLM Classifier ──▶ PUBLIC detected ──▶ Send to OpenAI API
     │               │                     │                      │
     │         (all-MiniLM-L6)       (High confidence)     (Full AI Power)
     │               │                     │                      │
     ▼               ▼                     ▼                      ▼
"Explain         Fast Analysis      Route to OpenAI = True   Detailed explanation
 quantum         Category: PUBLIC   Intent: QUERY           with examples, formulas,
 physics"        Safe to transmit                           and current research
                 Not saved to local DB (OpenAI has own history)
```

### 📈 Performance Benefits

| Feature | Old (E5 only) | New (Dual Model) | Improvement |
|---------|---------------|------------------|-------------|
| **Model Loading** | ~10-15s | ~8s | **30% faster** |
| **Classification** | ~50ms | ~31ms | **40% faster** |
| **Memory Usage** | 140MB | 142MB (22MB + 120MB) | Similar |
| **Languages** | 100+ | 100+ (E5 for search) | **Same** |
| **Categories** | 4 categories | 4 categories | **Enhanced** |
| **Database** | Basic storage | Category + timestamps | **Upgraded** |

---

## ❓ FAQ & Troubleshooting

### Privacy & Security

**Q: How do I know my data is truly private?**
A: Watch the model indicator:
- `🔒 local-privacy-routing` = 100% private, never sent to OpenAI
- `🌐 gpt-4o` = Public query, sent to OpenAI for processing

**Q: Can I verify what data is stored locally?**
A: Yes! Type `/config` → [6] Memory system → Search to explore your local database

**Q: How accurate is the privacy classification?**
A: High accuracy with dual AI models (MiniLM for classification, E5 for search). Conservative bias means questionable content stays local.

### Performance

**Q: Is local processing slower?**
A: Actually faster! Local queries respond in ~50ms vs 1-3 seconds for OpenAI API calls.

**Q: How much storage does it use?**
A: Minimal - MiniLM model (22MB) + E5 model (120MB) + chat history typically <10MB = ~150MB total.

### Installation Issues

**Q: "ai command not found" after installation**
A: Restart your terminal or run: `source ~/.zshrc`

**Q: Conflicts with existing 'ai' command**
A: The installer auto-detects conflicts and offers alternatives like `chat`, `ask`, or custom aliases.

**Q: Python/pip errors on macOS**
A: Install Python via Homebrew: `brew install python`

### Advanced

**Q: Can I use it offline?**
A: Local privacy features work offline. Public queries need internet for OpenAI API.

**Q: How to backup my private data?**
A: Your data is in `~/.aichat/memory.db` - copy this file to backup everything.

**Q: Enterprise deployment?**
A: Perfect for companies! Sensitive data never leaves your network while still accessing OpenAI's knowledge.

---

## Key Features

Technical capabilities:

✅ **Intelligent Privacy Routing** - Automatically detects sensitive content
✅ **Zero-Configuration Security** - Works out of the box
✅ **Privacy Compliance** - Designed for GDPR/CCPA requirements
✅ **Cost Optimization** - 70-80% reduction in API calls
✅ **Multilingual Intelligence** - 19 languages with privacy awareness
✅ **Automatic Data Protection** - No manual configuration required

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Key Areas
- **Privacy Classifiers**: Improve detection accuracy
- **Language Support**: Add more languages/dialects
- **Enterprise Features**: SSO, audit logs, compliance
- **Performance**: Optimize embedding models

---

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

**Privacy-First AI for Everyone** 🔒🚀

---

Built with ❤️ and powered by [OpenAI](https://openai.com) + local AI models for privacy.