# 🔒 AI Chat Terminal - Privacy-First AI Assistant

## Project Overview
AI Chat Terminal is a privacy-focused AI terminal that automatically routes sensitive data to local processing while using OpenAI for general queries.

**GitHub**: https://github.com/martinschenk/ai-chat-terminal
**Current Version**: 6.0.0 (Smart Privacy Routing - Sept 2025)

## Smart Privacy Routing System

**🎯 Major Features (v6.0.0):**
- **🧠 Dual AI Architecture**: Two separate `multilingual-e5-small` models for different purposes
- **🔍 Model #1 - Privacy Classifier**: Semantic classification of 4 privacy levels (160+ training examples)
- **💾 Model #2 - Memory System**: Vector-based semantic search in local SQLite database
- **🔒 100% Local Processing**: Credit cards, passwords, business secrets never sent to OpenAI
- **⚡ Ultra-Fast Training**: AI embeddings created in 0.7s, cached for instant loading
- **🌍 Multilingual Privacy**: Works across all 19 supported languages without hardcoded keywords
- **🗑️ Secure Deletion**: "Delete my credit card info" removes data permanently
- **💰 Cost Optimization**: 70-80% reduction in OpenAI API calls
- **🏢 Enterprise-Ready**: GDPR/CCPA compliant by design

## 🧠 DUAL AI MODEL ARCHITECTURE - CRITICAL UNDERSTANDING

### **TWO SEPARATE AI MODELS:**

#### **1️⃣ Privacy Classifier** (`privacy_classifier_fast.py`) - **NEW v6.0.0**
- **Model**: `sentence-transformers/all-MiniLM-L6-v2` (384D embeddings, 22MB)
- **Purpose**: Ultra-fast binary routing decision (PRIVATE vs PUBLIC)
- **Categories**: SENSITIVE/PROPRIETARY/PERSONAL → LOCAL, PUBLIC → OpenAI
- **Training**: 160+ examples (140 PRIVATE + 40 PUBLIC optimized for MiniLM)
- **Performance**: 0.5s training time, ~31ms classification per message (40% faster!)
- **Method**: Cosine similarity without E5 prefixing (MiniLM optimized)
- **Binary Logic**: `route_locally = category in ['SENSITIVE', 'PROPRIETARY', 'PERSONAL']`
- **Fallback**: Conservative routing (everything → local) if AI unavailable

#### **2️⃣ Memory System** (`memory_system.py`)
- **Model**: `intfloat/multilingual-e5-small` (384D embeddings, 120MB)
- **Purpose**: Multilingual semantic search and storage in local SQLite database
- **Features**: Vector similarity search, importance scoring, language detection
- **Storage**: All conversations with 384D embeddings + privacy categories + timestamps
- **Database Schema**: created_at, updated_at, metadata JSON with privacy_category
- **Cross-lingual**: Query in German, find English content seamlessly (100+ languages)
- **Prefixing**: Uses "query:" and "passage:" prefixes for optimal E5 performance

### **SYSTEM FLOW - NO HARDCODED KEYWORDS:**
```
User Input → Privacy Classifier (Model #1) → Classification Decision
                    ↓
    ┌─────────────────────────────────────────────────────────┐
    │                                                         │
    ▼ LOCAL (SENSITIVE/PROPRIETARY/PERSONAL)                  ▼ OPENAI (PUBLIC)
┌─────────────────┐                                    ┌──────────────────┐
│ Intent Detection│                                    │ Standard OpenAI  │
│ STORAGE/QUERY/  │                                    │ API Processing   │
│ DELETE          │                                    │ + Function Calls │
└─────────────────┘                                    └──────────────────┘
          │
          ▼
┌─────────────────┐
│ Memory System   │
│ (Model #2)      │
│ Store/Search    │
│ using Embeddings│
└─────────────────┘
```

### **KEY BREAKTHROUGH - AI REPLACES ALL HARDCODED LOGIC:**
- ❌ **OLD v5.x**: `if 'kreditkarte' in text or 'password' in text` (hardcoded keywords)
- ✅ **NEW v6.0**: AI learns from examples, understands context semantically
- ✅ **SCALABLE**: Add 100s more examples without touching code
- ✅ **MULTILINGUAL**: Recognizes "tarjeta de crédito" = "credit card" = "Kreditkarte" automatically
- ✅ **CONTEXT-AWARE**: "I need a card for the presentation" ≠ "My card number is 1234"

## 🔄 Smart Privacy Routing System Flow

### 🔐 SENSITIVE Data (e.g., "My credit card is 1234-5678")
```
User Input → Privacy Classifier → SENSITIVE (96% confidence)
           → Route Locally = TRUE
           → Store in Local SQLite
           → Template Response: "Sensitive data saved securely"
           → NEVER sent to OpenAI ✅
```

### 🏢 PROPRIETARY Data (e.g., "Our Q4 revenue target is $5M")
```
User Input → Privacy Classifier → PROPRIETARY (95% confidence)
           → Route Locally = TRUE
           → Store in Local SQLite
           → Template Response: "Business data stored locally"
           → NEVER sent to OpenAI ✅
```

### 👤 PERSONAL Data (e.g., "My sister lives in Berlin")
```
User Input → Privacy Classifier → PERSONAL (94% confidence)
           → Route Locally = TRUE
           → Store in Local SQLite
           → Template Response: "Personal info noted"
           → NEVER sent to OpenAI ✅
```

### 🌐 PUBLIC Knowledge (e.g., "Explain quantum physics")
```
User Input → Privacy Classifier → PUBLIC (95% confidence)
           → Route to OpenAI = TRUE
           → Full OpenAI API Processing
           → Rich, detailed response
           → Normal OpenAI usage ✅
```

### 🔍 SENSITIVE Query (e.g., "What's my credit card number?")
```
User Query → Privacy Classifier → SENSITIVE (96% confidence)
           → Route Locally = TRUE
           → Search Local SQLite Database
           → Find: "My credit card is 1234-5678"
           → Local Template Formatting
           → Response: "Your credit card is 1234-5678"
           → NEVER sent to OpenAI ✅
```

### 🗑️ DELETE Request (e.g., "Delete my credit card information")
```
User Request → Privacy Classifier → DELETE intent detected
            → Route Locally = TRUE
            → SQL DELETE with pattern matching
            → Remove matching entries
            → Response: "Deleted 3 entries from local database"
            → NEVER sent to OpenAI ✅
```

## 🛠️ Technical Architecture v6.0.0

### Core Components
1. **`privacy_classifier_fast.py`** - Ultra-fast MiniLM-based semantic classifier (NEW!)
2. **`chat_system.py`** - Smart routing integration with OpenAI API + metadata storage
3. **`memory_system.py`** - SQLite vector database with category search capabilities

### 🆕 NEW: Category-Based Database Queries

#### **Query by Privacy Category:**
```sql
-- Find all SENSITIVE data
SELECT content, datetime(created_at, 'unixepoch') as created
FROM chat_history
WHERE json_extract(metadata, '$.privacy_category') = 'SENSITIVE'
ORDER BY created_at DESC;

-- Find all PROPRIETARY company data
SELECT content, datetime(created_at, 'unixepoch') as created
FROM chat_history
WHERE json_extract(metadata, '$.privacy_category') = 'PROPRIETARY'
ORDER BY created_at DESC;

-- Count private data by category
SELECT json_extract(metadata, '$.privacy_category') as category,
       COUNT(*) as count
FROM chat_history
WHERE json_extract(metadata, '$.privacy_category') != 'PUBLIC'
GROUP BY category;
```

#### **Enhanced Database Schema (v6.0.0):**
```sql
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    role TEXT NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    metadata JSON DEFAULT '{}',  -- NEW: {"privacy_category": "SENSITIVE"}
    importance REAL DEFAULT 1.0,
    language TEXT DEFAULT 'en',
    created_at INTEGER,  -- NEW: Unix timestamp
    updated_at INTEGER   -- NEW: Unix timestamp
);
```

#### **User-Friendly Queries:**
```bash
# Show me all my sensitive information
SELECT content FROM chat_history
WHERE json_extract(metadata, '$.privacy_category') = 'SENSITIVE';

# Show company confidential data from last week
SELECT content, datetime(created_at, 'unixepoch')
FROM chat_history
WHERE json_extract(metadata, '$.privacy_category') = 'PROPRIETARY'
  AND created_at > strftime('%s', 'now', '-7 days');
```

### Privacy Classifier Details (Updated v6.0.0)
- **Model**: sentence-transformers/all-MiniLM-L6-v2 (384-dimensional embeddings, 22MB)
- **Training**: 160+ examples total (52 SENSITIVE + 32 PROPRIETARY + 36 PERSONAL + 40 PUBLIC)
- **Performance**: ~31ms classification time (40% faster than E5)
- **Method**: Mean embeddings per category → cosine similarity for classification
- **Binary Routing**: Everything except PUBLIC → Local Database
- **Accuracy**: High confidence >75%, medium confidence >60%
- **Languages**: All languages supported by MiniLM (100+)
- **Intents**: STORAGE, QUERY, DELETE detection with regex patterns
- **Fallback**: Conservative routing when AI unavailable

### Database Schema
```sql
chat_history (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    timestamp INTEGER,
    role TEXT,           -- 'user' or 'assistant'
    content TEXT,        -- The actual message
    importance REAL,     -- AI-calculated importance score
    language TEXT        -- Detected language
)
```

## 📁 Project Structure

```
ai-chat-terminal/
├── install.sh                    # Smart installer with conflict detection
├── aichat.zsh                   # Main shell integration
├── modules/
│   ├── functions.zsh            # Chat loop with DIALECT_PROMPT system
│   └── config-menu.zsh          # Interactive configuration
├── privacy_classifier_fast.py   # 🆕 Privacy classification engine
├── chat_system.py              # 🆕 Smart routing integration
├── memory_system.py            # Vector database system
├── lang/                       # 19 language files with dialects
│   ├── en.conf
│   ├── de.conf                 # German + Schwäbisch, Bayerisch, etc.
│   └── es.conf                 # Spanish + Mexican, Argentinian, etc.
├── VERSION                     # Current: 6.0.0
├── README.md                   # 🆕 Privacy-focused documentation
└── CLAUDE.md                   # This file
```

## 🔍 Privacy Classification Examples

### SENSITIVE Detection
```python
# These inputs are classified as SENSITIVE and processed 100% locally:
"My credit card is 4532-1234-5678-9012"
"Password for account: secret123"
"API key: sk-abc123def456"
"Meine Kreditkartennummer ist 1234-5678"
"PIN code is 9876"
```

### PROPRIETARY Detection
```python
# These inputs stay local to protect business secrets:
"Our Q2 product launch is planned for June"
"Internal workflow has 3 escalation stages"
"Company revenue target for 2025 is $5M"
"Unser interner Workflow hat 3 Eskalationsstufen"
"Confidential client project codenamed Phoenix"
```

### PERSONAL Detection
```python
# Personal information is processed locally:
"My uncle lives in Seattle and loves fishing"
"Daughter's soccer game is this Saturday"
"Mein Onkel Hans wohnt in München"
"Personal reminder: buy groceries for dinner"
"Family vacation planned for August"
```

### PUBLIC Processing
```python
# General knowledge gets full OpenAI intelligence:
"What's the capital of Japan?"
"Explain quantum physics concepts"
"Wie ist das Wetter heute in Berlin?"
"Convert 100 Fahrenheit to Celsius"
"¿Cuál es la fórmula del agua?"
```

## 🌟 Unique Market Position

This is the **only AI terminal** that offers:
- ✅ **Automatic Privacy Detection** - No manual configuration needed
- ✅ **Semantic Understanding** - Not just keyword matching
- ✅ **Zero External Transmission** - Sensitive data never leaves device
- ✅ **Enterprise Compliance** - GDPR/CCPA ready out of the box
- ✅ **Cost Efficiency** - 70-80% fewer API calls
- ✅ **Multilingual Privacy** - Works in 19 languages

## 🔧 Development Guidelines

### Testing Privacy Classification
```bash
# Test the classifier directly
cd ~/.aichat
python3 privacy_classifier_fast.py

# Test full integration
python3 -c "
from chat_system import ChatSystem
chat = ChatSystem()

# Test sensitive data (should route locally)
response, metadata = chat.send_message('test', 'My password is secret123', 'English system prompt')
print(f'Model: {metadata.get(\"model\")}')  # Should be 'local-privacy-routing'
"
```

### Adding New Privacy Categories
1. Extend examples in `get_category_examples()` in privacy_classifier_fast.py
2. Add handling logic in `handle_local_message()` in chat_system.py
3. Test with representative examples
4. Update documentation

### Performance Monitoring
- Classification time should be <50ms
- Training time should be <5 seconds
- Accuracy should be >95% for each category
- Local processing should be faster than OpenAI API calls

## 📊 Version History & Roadmap

### v6.0.0 (Sept 2025) - Smart Privacy Routing 🔒
- Revolutionary 4-level privacy classification
- 100% local processing for sensitive data
- DELETE functionality for data removal
- Enterprise-grade privacy compliance

### v5.4.1 (Aug 2025) - Language Architecture 🌍
- Multilingual memory system with vector search
- Function calling for personal data access
- 19 languages with regional dialects

### v6.0.0 (September 2025) - Dual AI Model Architecture 🚀
- **Privacy Classifier**: all-MiniLM-L6-v2 (40% faster classification)
- **Memory Search**: multilingual-e5-small (100+ languages)
- **Enhanced Database**: Privacy categories + created/updated timestamps
- **Binary Routing**: PRIVATE (3 categories) vs PUBLIC (1 category)
- **Performance**: 30% faster loading, 40% faster classification

### v5.3.0 (July 2025) - AI Vector Database 🧠
- Semantic search with sentence-transformers
- Cross-language memory retrieval
- Smart cleanup system

## 🚨 IMPORTANT: Date/Year Handling

⚠️ **CRITICAL REMINDER**: When adding dates or years to ANY code, docs, or comments:
1. **NEVER assume the current year**
2. **ALWAYS check the current date first** (Today is September 2025)
3. **Use 2025 for all new copyright notices**
4. **Check system date if unsure**: use `date` command or ask user

## 🤝 Contributing & Issues

**GitHub Repository**: https://github.com/martinschenk/ai-chat-terminal

### Priority System
1. **priority-high**: Security issues, privacy breaches, breaking functionality
2. **priority-medium**: Feature enhancements, classification improvements
3. **priority-low**: Documentation, minor UI improvements

### Key Development Areas
- **Privacy Classifiers**: Improve detection accuracy for edge cases
- **Enterprise Features**: SSO integration, audit logs, compliance reporting
- **Performance**: Optimize embedding models, reduce memory usage
- **Language Support**: Add more languages and dialects
- **Mobile Support**: iOS/Android terminal apps

## 🔐 Security & Privacy Notes

- **No Telemetry**: System never phones home
- **Local Embeddings**: E5 model runs entirely on device
- **Encrypted Storage**: SQLite database can be encrypted
- **Audit Trail**: All routing decisions are logged locally
- **Data Portability**: Standard SQLite format for easy backup/export

**Privacy-First AI for Everyone** 🔒🚀