# AI Chat Terminal

A ChatGPT-powered terminal interface with integrated web search and memory.

[![Version](https://img.shields.io/badge/version-5.2.0-blue.svg)](https://github.com/martinschenk/ai-chat-terminal)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20|%20Linux-lightgrey.svg)](https://github.com/martinschenk/ai-chat-terminal)
[![Author](https://img.shields.io/badge/author-Martin%20Schenk-orange.svg)](https://github.com/martinschenk)

**Copyright © 2024 Martin Schenk | Licensed under MIT License**

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

### Basic Chat
```bash
chat "Hello, how are you?"
chat "Explain Docker containers"
chat "Write a Python function to parse JSON"
```

### Web Search (Automatic)
```bash
chat "What's the latest news in AI development?"
chat "Current status of Bitcoin price"
chat "Who won today's major tech conference announcements?"
chat "Latest TypeScript version features"
```

### Memory Examples
```bash
chat "I'm working on a Node.js REST API"
chat "What's the best way to handle authentication?"  # Remembers Node.js context
chat "Show me code examples for that"                # Continues previous topic
```

### Configuration
Start chat, then type `/config` to open settings menu.

## Configuration

Start chat, then type `/config` inside the chat to access the configuration menu:

1. **Change Command** - Switch between `chat`, `ai`, `ask`, `q`, or custom
2. **Change Language** - Select from 19 supported languages
3. **Change Timeout** - Adjust session memory duration
4. **Toggle ESC Exit** - Enable/disable quick exit with ESC key
5. **Change AI Model** - Select OpenAI model (GPT-4o recommended)
6. **Clear Cache** - Reset conversation history
7. **Back to Chat** - Return to conversation
8. **Uninstall** - Complete removal with cleanup

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