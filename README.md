# AI Chat Terminal - Privacy-First AI Assistant

**The heart of AI Chat Terminal: Chat with complete peace of mind.** Every message is automatically analyzed BEFORE sending - if it contains credit cards, passwords, API keys, company secrets, or personal information, it's instantly routed to your local vector database instead of OpenAI. When you later ask for this information, it's retrieved from your local storage, never touching the cloud. This automatic detection and routing happens seamlessly in the background, giving you the full power of AI while keeping your sensitive data 100% private.

[![Version](https://img.shields.io/badge/version-6.2.0-blue.svg)](https://github.com/martinschenk/ai-chat-terminal)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20|%20Linux-lightgrey.svg)](https://github.com/martinschenk/ai-chat-terminal)
[![Privacy](https://img.shields.io/badge/privacy-first-green.svg)](https://github.com/martinschenk/ai-chat-terminal)

## 🔐 Core Innovation

**Automatic Privacy Protection:** Our triple-layer AI system (Presidio NER + Semantic Classifier + Vector Database) ensures:
- **Sensitive data NEVER reaches OpenAI** - intercepted and stored locally before transmission
- **Seamless retrieval** - "What's my API key?" pulls from local vector database, not cloud
- **Zero configuration** - works out of the box for all 19 supported languages
- **Future-proof** - designed to support multiple cloud AI providers beyond OpenAI

## 🆕 What's New in v6.2.0

### 🔍 **Enhanced PII Detection with Microsoft Presidio**
- Professional-grade PII detection using Named Entity Recognition
- Supports 15+ languages with spaCy models
- Custom patterns for API keys, credit cards, passwords
- Graceful fallback to regex when Presidio unavailable

### 🤖 **Natural Response Generation with Phi-3**
- Phi-3 integration via Ollama for contextual responses
- Template fallback system for lightweight operation
- Multilingual response generation
- Works perfectly without Phi-3 installed

### 📈 **Upgraded Memory System**
- Migrated from `multilingual-e5-small` to `multilingual-e5-base`
- 15% better cross-language search performance
- Proper E5 prefixing for optimal results
- Migration script for existing users

---

## ⚡ Quick Start

**60-second setup:**

```bash
# Install with automatic configuration
curl -sL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | bash

# Reload shell
source ~/.zshrc

# Start chatting
chat
```

**First run setup:**
1. Enter your [OpenAI API key](https://platform.openai.com/api-keys)
2. Choose language (19 supported + regional dialects)
3. Select privacy level (Enhanced recommended)
4. Optional: Install Phi-3 for natural responses

---

## 📦 What Gets Installed WHERE

Understanding exactly what goes where on your system:

### **In `~/.aichat/` (Application-specific)**
| Component | Description | Size |
|-----------|-------------|------|
| Python scripts (*.py) | Core application logic | ~5MB |
| Shell modules | ZSH integration | ~1MB |
| Language configs | 19 language files | ~500KB |
| Your data | memory.db, config, .env | Variable |
| Embeddings cache | privacy_embeddings.pkl | ~100KB |

### **Global (Shared with other applications)**

#### **Python Packages** (`~/.local/lib/python/`)
| Package | Purpose | Size | Shareable |
|---------|---------|------|-----------|
| sentence-transformers | AI embeddings | ~100MB | ✅ Yes |
| presidio-analyzer | PII detection | ~30MB | ✅ Yes |
| presidio-anonymizer | Data anonymization | ~10MB | ✅ Yes |
| spacy | NLP engine | ~50MB | ✅ Yes |
| sqlite-vec | Vector search | ~5MB | ✅ Yes |

#### **AI Models** (`~/.cache/huggingface/hub/`)
| Model | Purpose | Size | Auto-shared |
|-------|---------|------|-------------|
| all-MiniLM-L6-v2 | Privacy classification | 22MB | ✅ Yes |
| multilingual-e5-base | Semantic search | 278MB | ✅ Yes |

#### **spaCy Language Models** (`~/Library/Python/` or `~/.local/`)
| Languages | Models Available | Size Each |
|-----------|-----------------|-----------|
| Core (EN, DE) | Always installed | ~15MB |
| European (12 models) | ES, FR, IT, PT, NL, PL, DA, SV, NO, FI, RU, CA | ~15MB |
| Asian (3 models) | ZH, JA, KO | ~20-40MB |

#### **Ollama & Phi-3** (`~/.ollama/models/`)
| Component | Purpose | Size | Usage |
|-----------|---------|------|--------|
| Ollama | Model manager | ~50MB | System-wide |
| Phi-3 | Natural responses | ~2GB | `ollama run phi3` |

---

## 🎯 Smart Features

### **Automatic Model Sharing**
- **Models are NEVER downloaded twice** - if you have `multilingual-e5-base` from another project, we use it!
- **Automatic cache detection** - checks `~/.cache/huggingface/hub/` first
- **Version management** - updates shared across all applications

### **Existing Model Detection**
The installer automatically detects:
```bash
# HuggingFace models
~/.cache/huggingface/hub/models--intfloat--multilingual-e5-base/

# Ollama models
ollama list | grep phi3

# Python packages
pip3 list | grep presidio

# spaCy models
python3 -m spacy info
```

### **Zero Redundancy**
- If Presidio is installed → Skip installation
- If Phi-3 exists → Use existing model
- If E5-base cached → No download needed
- If spaCy model present → Reuse it

---

## 📊 Storage Overview

| Component | Location | Size | Shared? | Removable? |
|-----------|----------|------|---------|------------|
| **Core App** | ~/.aichat/ | ~5MB | No | Yes - loses all data |
| **MiniLM** | ~/.cache/huggingface/ | 22MB | Yes | Yes - re-downloads |
| **E5-base** | ~/.cache/huggingface/ | 278MB | Yes | Yes - re-downloads |
| **Presidio** | ~/.local/lib/python/ | 50MB | Yes | Keep for other apps |
| **spaCy Models** | ~/Library/Python/ | 15-40MB each | Yes | Keep for NLP |
| **Phi-3** | ~/.ollama/models/ | 2GB | Yes | Keep for Ollama |

**Total fresh install:** ~350MB (without Phi-3) or ~2.3GB (with Phi-3)

---

## 🧠 Technical Architecture

### **Triple-Layer Privacy Protection**

```
User Input
    ↓
[1. Presidio PII Check] ← NEW! Professional NER detection
    ├─→ Concrete PII found → Store locally
    └─→ No PII → Continue
    ↓
[2. Privacy Classifier] ← Semantic understanding
    ├─→ SENSITIVE/PROPRIETARY/PERSONAL → Local
    └─→ PUBLIC → Continue
    ↓
[3. OpenAI Processing] ← General knowledge
    └─→ Function Calling for private data queries
```

### **Core Components**

1. **PII Detector** (`pii_detector.py`)
   - Microsoft Presidio integration
   - Custom API key patterns
   - Multilingual NER support
   - Regex fallback system

2. **Privacy Classifier** (`privacy_classifier_fast.py`)
   - Model: `all-MiniLM-L6-v2` (22MB)
   - 4-category classification
   - 160+ training examples
   - ~31ms classification time

3. **Memory System** (`memory_system.py`)
   - Model: `multilingual-e5-base` (278MB)
   - Vector similarity search
   - E5 prefix optimization
   - Cross-language retrieval

4. **Response Generator** (`response_generator.py`)
   - Phi-3 via Ollama (optional)
   - Template-based fallback
   - Multilingual support
   - Context-aware responses

---

## 🌍 Multi-Language Support

### **Interface Languages** (19 total)
- **European**: English, German, Spanish, French, Italian, Portuguese, Dutch, Swedish, Norwegian, Danish, Finnish, Polish, Russian
- **Asian**: Chinese, Japanese, Korean, Hindi
- **Regional**: Catalan, Basque, Galician
- **Dialects**: German (Schwäbisch, Bayerisch), Spanish (Mexican, Argentinian)

### **PII Detection Languages** (spaCy models)
The installer offers models for 15+ languages. Each model enables professional NER-based PII detection:

| Region | Languages | Models |
|--------|-----------|---------|
| **Core** | English, German | Installed by default |
| **European** | Spanish, French, Italian, Portuguese, Dutch, Polish, Danish, Swedish, Norwegian, Finnish, Russian, Catalan | Optional |
| **Asian** | Chinese, Japanese, Korean | Optional |

---

## 💡 Installation Options

### **Minimal Installation** (~100MB)
```bash
# Choose during install:
- Privacy Level: Basic (semantic only)
- Additional languages: 0 (skip)
- Phi-3: N (skip)
```

### **Standard Installation** (~350MB)
```bash
# Choose during install:
- Privacy Level: Enhanced (Presidio + semantic)
- Additional languages: Select your needs
- Phi-3: N (templates work great)
```

### **Full Installation** (~2.5GB)
```bash
# Choose during install:
- Privacy Level: Enhanced
- Additional languages: all
- Phi-3: Y (natural responses)
```

---

## 🔒 Privacy Examples

### **What Stays Local (NEVER sent to OpenAI)**
```
"My credit card is 4532-1234-5678-9012"      → Stored locally
"API key: sk-proj-abc123..."                 → Stored locally
"Company revenue target is $5M"              → Stored locally
"My sister lives in Berlin"                  → Stored locally
```

### **What Goes to OpenAI (PUBLIC queries)**
```
"Explain quantum physics"                    → OpenAI
"What's the capital of Japan?"              → OpenAI
"How to center a div in CSS?"               → OpenAI
"Convert 100 Fahrenheit to Celsius"         → OpenAI
```

### **Smart Retrieval (from local database)**
```
"What's my API key?"                        → Retrieved locally
"Show me my credit card"                    → Retrieved locally
"What was that password?"                   → Retrieved locally
"Delete my sensitive data"                  → Deleted locally
```

---

## 🛠️ Configuration

### **Interactive Config Menu**
```bash
chat        # Start chatting
/config     # Opens configuration menu
```

**Options available:**
1. Change command alias
2. Select language (19 options)
3. Toggle ESC key behavior
4. Choose AI model (gpt-4o, gpt-4o-mini, gpt-3.5-turbo)
5. Adjust context window
6. Configure OpenAI API key
7. Privacy protection level
8. Memory system management
9. Clear cache
10. About & version info

### **Manual Configuration**
Edit `~/.aichat/config`:
```bash
AI_CHAT_LANGUAGE="en"
AI_CHAT_MODEL="gpt-4o-mini"
PRIVACY_LEVEL="enhanced"
PHI3_ENABLED="true"
PRESIDIO_ENABLED="true"
```

---

## 🧪 Testing & Validation

### **Test PII Detection**
```bash
cd ~/Development/ai-chat-terminal
python3 test_pii.py
```

### **Test Individual Components**
```bash
# Privacy classifier
python3 privacy_classifier_fast.py

# PII detector
python3 -c "
from pii_detector import PIIDetector
d = PIIDetector()
print(d.get_detection_info())
"

# Response generator
python3 -c "
from response_generator import ResponseGenerator
g = ResponseGenerator()
print(g.get_generator_info())
"
```

---

## 📈 Migration from Previous Versions

### **For users upgrading from v6.0.0 or v6.1.0:**
```bash
# Run migration script
python3 migrate_to_e5_base.py

# This will:
# - Backup your database
# - Re-encode embeddings with e5-base
# - Preserve all your data
# - Update configuration
```

---

## 🚀 Advanced Features

### **Function Calling Integration**
OpenAI function calling for private data queries - automatically triggered when asking for stored information.

### **Vector Search**
SQLite with vector extensions for semantic similarity search across all stored conversations.

### **Smart Deletion**
Pattern-based deletion of sensitive data: "Delete all credit card info" → Removes matching entries.

### **Cross-Language Memory**
Store in German, retrieve in English. Store in Spanish, query in French. True multilingual understanding.

---

## 🤝 Contributing

We welcome contributions! Areas of interest:

- **Privacy Detection**: Improve PII patterns and detection
- **Language Support**: Add more spaCy models
- **Response Quality**: Enhance template responses
- **Performance**: Optimize embedding generation

---

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## ❓ FAQ

### **Q: Is my data really private?**
A: Yes! Check the routing indicator:
- `🔒 local-privacy-routing` = Never sent to OpenAI
- `🌐 gpt-4o` = Public query to OpenAI

### **Q: Can I use this offline?**
A: Local features work offline. OpenAI queries need internet.

### **Q: How do I backup my data?**
A: Copy `~/.aichat/memory.db` to backup all conversations.

### **Q: Can I uninstall cleanly?**
A: Yes! Use `/config` → [11] Complete uninstall, or manually:
```bash
rm -rf ~/.aichat  # Removes app and your data
# Python packages and models remain (shared with other apps)
```

---

**Privacy-First AI for Everyone** 🔒🚀

Built with ❤️ for privacy-conscious users.