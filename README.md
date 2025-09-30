# AI Chat Terminal

Local terminal chat with automatic privacy protection for sensitive data.

[![Version](https://img.shields.io/badge/version-6.3.0-blue.svg)](https://github.com/martinschenk/ai-chat-terminal)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://github.com/martinschenk/ai-chat-terminal)

## What is AI Chat Terminal?

A terminal-based chat system that automatically decides: Sensitive inputs stay local in a vector database, public questions go to OpenAI.

**How it works:**
- Input with private data (API keys, passwords) → Local storage
- Public questions (e.g., "Capital of France?") → OpenAI
- Query private data → Local database (never cloud)

### Data Flow: Input & Storage

```
┌───────────────────────────────────────────────┐
│ Input: "My phone number is +1-555-0123"      │
└────────────────────┬──────────────────────────┘
                     ↓
          ┌──────────────────────┐
          │ Privacy Classifier   │ ← AI decides automatically
          │   (local on Mac)     │
          └──────────┬───────────┘
                     ↓
         ┌───────────┴───────────┐
         ↓                       ↓
   🔒 SENSITIVE             🌐 PUBLIC
   (store locally)          (→ OpenAI)
         ↓                       ↓
   [Vector Database]        [OpenAI GPT-4]
   ~/.aichat/memory.db
```

### Data Flow: Private Data Retrieval

```
┌────────────────────────────────────┐
│ Question: "What's my phone number?"│
└─────────────┬──────────────────────┘
              ↓
    ┌─────────────────────┐
    │ Detects: Private     │
    │ Data Query          │
    └─────────┬───────────┘
              ↓
       🔒 Local DB
       ├─ Semantic search in vector database
       └─ Returns: "+1-555-0123"

    ❌ Never sent to OpenAI!
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

## Requirements

| | Minimum | Recommended |
|---|---|---|
| **macOS** | Catalina 10.15+ | Monterey 12+ |
| **RAM** | 8 GB | 16 GB |
| **Storage** | 5 GB free | 10 GB free |
| **Processor** | Intel 2015+ | Apple Silicon M1+ |

### Compatibility

- ✅ **M1/M2/M3 Mac with 16+ GB RAM** → All models recommended
- ✅ **Intel Mac with 16 GB RAM** → All models work
- ⚠️ **8 GB RAM** → Base models only (no Phi-3)
- ❌ **< macOS Catalina** → Not supported (Linux/Windows: Coming soon)

---

## Examples

### Sensitive Data (stays local)

```bash
You: My phone number is +1-555-0123
AI: [Stored in local DB] 🔒

You: I live at 123 Main Street, Springfield
AI: [Stored] 🔒

You: What's my phone number?
AI: +1-555-0123 [From local DB] 🔒
```

### Public Questions (to OpenAI)

```bash
You: Capital of France?
AI: Paris [OpenAI GPT-4] 🌐

You: Explain quantum physics
AI: [Response from OpenAI] 🌐
```

---

## Features

- **Automatic Privacy**: AI-based classification
- **19 Languages**: EN, DE, ES, FR, IT, CA, ZH, HI, etc.
- **Vector Database**: SQLite with semantic search
- **Configurable**: `/config` menu for all settings
- **OpenAI Integration**: GPT-4, GPT-4o, GPT-4o-mini

---

## Installation Details

### What gets installed where?

**Local (~/.aichat/)**
- Scripts, config, chat history
- Your private data in vector database
- Used only by this tool

**Global (shared)**
- AI models (HuggingFace cache)
- Python packages (pip --user)
- Can be used by other apps

### Intelligent Model Selection

The installer analyzes your Mac and recommends:

| Your Mac | Recommendation |
|----------|---------------|
| 16+ GB RAM | Presidio ✅ + Phi-3 ✅ |
| 8-16 GB RAM | Presidio ✅, Phi-3 optional |
| <8 GB RAM | Base models only |

**Example output with 16 GB RAM:**
```
💬 Why recommended for you?
   Your Mac has 16 GB RAM - perfect for Presidio!
   Protects phone numbers, addresses, personal info.
```

---

## Technical Details

### Components

| Component | Model | Size | Purpose |
|-----------|-------|------|---------|
| Privacy Classifier | all-MiniLM-L6-v2 | 22 MB | Routing decision |
| Memory System | multilingual-e5-base | 278 MB | Semantic search |
| PII Detection | Microsoft Presidio | 350 MB | Sensitive data detection |
| Response Generator | Phi-3 via Ollama | 2.3 GB | Natural responses |

### Privacy Layers

1. **PII Detector**: Recognizes concrete data types (credit cards, API keys)
2. **Semantic Classifier**: Understands context (SENSITIVE/PUBLIC)
3. **Vector Database**: Local storage with embeddings

---

## Configuration

```bash
chat           # Start
/config        # Settings
```

**Available options:**
- Choose language (19 available)
- Change OpenAI model
- Adjust privacy level
- Install/remove models after installation
- Configure context window

---

## Uninstall

**In chat:**
```bash
chat
/config
→ [12] Complete uninstall
```

**Manual:**
```bash
rm -rf ~/.aichat
```

*Note: Global models remain (can be used by other apps)*

---

## FAQ

**Q: Is my data really private?**
A: Yes. Sensitive data never goes to OpenAI. Check the indicator: 🔒 = local, 🌐 = OpenAI

**Q: Does it work offline?**
A: Local features yes. OpenAI queries need internet.

**Q: How does detection work?**
A: Three-stage: PII Detector → Semantic Classifier → Routing

**Q: Can I use other models?**
A: Currently OpenAI only. Claude/Gemini support: Planned

**Q: Linux/Windows support?**
A: Currently macOS only. Linux: Planned for v7.0

---

## License

MIT License - see [LICENSE](LICENSE)

**Built with ❤️ for Privacy**
