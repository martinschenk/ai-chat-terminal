# AI Chat Terminal - Development Guidelines

## Project Overview
Privacy-focused AI terminal that routes sensitive data locally while using OpenAI for general queries.

**GitHub**: https://github.com/martinschenk/ai-chat-terminal
**Current Version**: 6.1.0

## Core Architecture

### Dual AI Models
1. **Privacy Classifier** (`privacy_classifier_fast.py`)
   - Model: `all-MiniLM-L6-v2` (22MB)
   - Routes SENSITIVE/PROPRIETARY/PERSONAL → Local
   - Routes PUBLIC → OpenAI

2. **Memory System** (`memory_system.py`)
   - Model: `multilingual-e5-base` (278MB)
   - Semantic search in SQLite with vector embeddings
   - Uses E5 prefixes: "query:" for search, "passage:" for storage

3. **PII Detector** (`pii_detector.py`)
   - Microsoft Presidio integration (optional)
   - Fallback to regex patterns
   - Detects credit cards, API keys, passwords, etc.

4. **Response Generator** (`response_generator.py`)
   - Phi-3 via Ollama for natural responses (optional)
   - Template fallback system

## Key Files
- `chat_system.py` - Main routing logic with OpenAI integration
- `install.sh` - Installation with optional Presidio/Phi-3
- `memory_system.py` - Database with enhanced private data methods
- `test_pii.py` - Comprehensive test suite

## Development Workflow

### Testing
```bash
# Run tests
python3 test_pii.py

# Test classifier
python3 privacy_classifier_fast.py
```

### After Changes
```bash
# Copy to test environment
cp *.py /Users/martin/.aichat/
cp modules/*.zsh /Users/martin/.aichat/modules/

# Retrain if needed
cd /Users/martin/.aichat
python3 -c "from privacy_classifier_fast import FastPrivacyClassifier; c = FastPrivacyClassifier(); c.train_fast()"
```

## Important Notes
- Privacy categories stored in `chat_history.metadata` JSON field
- No separate private_data table needed
- Presidio and Phi-3 are optional with fallbacks
- System works without any optional dependencies