# AI Chat Terminal

A ChatGPT-powered terminal interface with integrated web search and memory.

[![Version](https://img.shields.io/badge/version-5.2.0-blue.svg)](https://github.com/martinschenk/ai-chat-terminal)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20|%20Linux-lightgrey.svg)](https://github.com/martinschenk/ai-chat-terminal)


## Features

- **ChatGPT Integration** - Powered by OpenAI's latest models (GPT-4o, GPT-4o-mini, etc.)
- **Integrated Web Search** - Real-time information via ChatGPT search capabilities
- **Conversational Memory** - Maintains context during chat sessions
- **Multi-Language Support** - 19 languages with regional dialects
- **Customizable Commands** - Use `chat`, `ai`, `ask`, or custom aliases

## Installation

```bash
curl -sL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | bash
```

After installation:
1. Run `source ~/.zshrc` to reload your shell
2. Run `chat` to start the initial setup
3. Enter your OpenAI API key when prompted

## Usage

Start by typing `chat` to enter the interactive terminal:

### Development Examples
```
👤 You ▶ I need help with Docker. My container keeps failing on port 3000
🤖 AI ▶
Port 3000 conflicts are common in development. Here are the solutions:

1. Check what's using port 3000:
   lsof -ti:3000
   kill -9 $(lsof -ti:3000)

2. Use a different port in Docker:
   docker run -p 3001:3000 your-app

3. In docker-compose.yml:
   ports:
     - "3001:3000"

The issue is likely another process (React dev server, Next.js, etc.) already using port 3000.
─────────────────────────────────────────────────────

👤 You ▶ show me a Python function to parse JSON with error handling
🤖 AI ▶
Here's a robust JSON parser with comprehensive error handling:

import json
from typing import Dict, Any, Optional

def safe_json_parse(json_string: str) -> Optional[Dict[str, Any]]:
    try:
        if not json_string or json_string.strip() == "":
            return None
        data = json.loads(json_string.strip())
        return data
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Usage:
result = safe_json_parse('{"name": "John", "age": 30}')
if result:
    print(f"Name: {result['name']}")

This handles malformed JSON, empty strings, and provides detailed error information.
─────────────────────────────────────────────────────

👤 You ▶ what's the current status of TypeScript 5.x features?
🤖 AI ▶
As of September 27, 2025, TypeScript 5.x has introduced several powerful features:

TypeScript 5.0 (March 2023):
- Decorators support (stage 3 proposal)
- const type parameters for better inference
- Supporting multiple config files with extends

TypeScript 5.1 (June 2023):
- Easier implicit returns for undefined-returning functions
- Unrelated types for getters and setters
- JSX element improvements

TypeScript 5.2 (August 2023):
- using declarations for explicit resource management
- Decorator metadata
- Named and anonymous tuple elements

TypeScript 5.3 (November 2023):
- Import attributes syntax
- Resolution strategy and bundler improvements
- Better performance for monorepos

TypeScript 5.4 (March 2024):
- Preserved narrowing in closures
- NoInfer utility type
- Object.groupBy typing improvements

The focus has been on developer experience, performance, and modern JavaScript feature support.
─────────────────────────────────────────────────────

👤 You ▶ datetime?
🤖 AI ▶
Based on your local information, the current date and time is Saturday, September 27, 2025, at 00:26. If you need any further assistance or have more questions, feel free to ask!
─────────────────────────────────────────────────────

👤 You ▶
```

### Quick Commands
You can also ask direct questions without entering the chat:
```bash
chat "Fix this Docker error: port already in use"
chat "Best practices for Python virtual environments"
chat "How to optimize PostgreSQL queries?"
```

### Configuration
Start chat, then type `/config` to open settings menu:

```
⚙️  CONFIGURATION

╔═══════════════════════════════════════╗
║  Current Settings:                ║
║  ├─ Command: chat                  ║
║  ├─ Language: en                 ║
║  ├─ Timeout: 3600s               ║
║  └─ ESC to exit: true          ║
╠═══════════════════════════════════════╣
║  [1] Change command character           ║
║  [2] Change language                  ║
║  [3] Change timeout                  ║
║  [4] Toggle ESC key exit            ║
║  [5] Change AI model                 ║
║  [6] 🧹 Clear chat cache              ║
║  [7] ℹ️  About & Version                ║
║  [8] Back to chat                   ║
║                                       ║
║  [9] 🗑️  Uninstall completely        ║
╚═══════════════════════════════════════╝

Select [1-9]:
```

## Configuration Options

The configuration menu provides these options:

1. **Change Command** - Switch between `chat`, `ai`, `ask`, `q`, or custom
2. **Change Language** - Select from 19 supported languages
3. **Change Timeout** - Adjust session memory duration (60-3600 seconds)
4. **Toggle ESC Exit** - Enable/disable quick exit with ESC key
5. **Change AI Model** - Select OpenAI model (GPT-4o recommended)
6. **Clear Cache** - Reset conversation history
7. **About & Version** - View version and attribution information
8. **Back to Chat** - Return to conversation
9. **Uninstall** - Complete removal with cleanup

## Requirements

- **OpenAI API Key** (required) - Get yours at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Python 3** (usually pre-installed on macOS/Linux)
- **Shell-GPT** (automatically installed)

## Supported Languages

English, German (+ Schwäbisch, Bayerisch, Sächsisch), Spanish (+ Mexican, Argentinian, Colombian, etc.), French, Italian, Catalan, Basque, Galician, Chinese (Mandarin), Hindi, and more.

## Troubleshooting

### Command already exists
If `chat` conflicts with existing commands, the installer will suggest alternatives like `ai`, `ask`, or `aic`.

### API Key Issues
Ensure your OpenAI account has sufficient credit. Start `chat` then use `/config` to update your API key.

### Shell-GPT Not Found
```bash
pip3 install --user shell-gpt
```

## Uninstall

Start `chat`, then type `/config` and select option 8 (Uninstall).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file.

## Attribution

Built on [Shell-GPT](https://github.com/TheR1D/shell_gpt) by TheR1D.