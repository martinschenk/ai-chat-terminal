# 🤖 AI Chat Terminal

<div align="center">

![Version](https://img.shields.io/badge/version-5.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-macOS%20|%20Linux-lightgrey.svg)
![Languages](https://img.shields.io/badge/languages-19-orange.svg)

**The most powerful AI assistant for your terminal - with real-time web search!**

[Installation](#-installation) • [Features](#-features) • [Languages](#-languages) • [API Keys](#-api-keys) • [Contributing](#-contributing)

</div>

---

## 🚀 Why AI Chat Terminal?

Transform your terminal into an intelligent assistant that:
- **🔍 Searches the web in real-time** - Get current news, weather, stock prices, and more
- **🧠 Remembers your conversation** - Context-aware responses with smart session management
- **🌍 Speaks your language** - 19 languages including regional dialects
- **⚡ Lightning fast** - Optimized for speed with customizable models
- **🎨 Beautiful UI** - Clean, colorful interface with emoji support
- **🔐 Secure** - API keys stored safely in encrypted `.env` files

## ✨ Features

### 🎯 Core Features
- **ChatGPT Integration** - Powered by OpenAI's latest models (GPT-4, GPT-4o, etc.)
- **Web Search** - Real-time information via Perplexity API (optional)
- **Smart Memory** - Maintains context for natural conversations
- **Multi-Model Support** - Choose the best AI model for your needs
- **Configuration Menu** - Easy settings management with `/config`

### 🌐 Web Search Examples
```bash
ai "What's the weather in Tokyo?"
ai "Latest news about AI?"
ai "Current Bitcoin price"
ai "Who won the game last night?"
```

### 💬 Regular Chat Examples
```bash
ai "Explain quantum computing"
ai "Write a Python function for fibonacci"
ai "Help me debug this error"
ai "Translate this to Spanish"
```

## 📦 Installation

### Quick Install (Recommended)
```bash
curl -sL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | bash
```

### Manual Install
```bash
git clone https://github.com/martinschenk/ai-chat-terminal.git
cd ai-chat-terminal
bash install.sh
```

## 🔑 API Keys

### OpenAI (Required)
You need an OpenAI API key to use this tool.

**Pricing**: Pay-per-use model
- ✅ **No monthly subscription needed**
- 💰 Start with just $5 credit
- 📊 Typical costs: $0.01-0.10 per conversation
- 🔗 Get your key: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

**How to get started:**
1. Create an OpenAI account
2. Add $5-10 credit to your account
3. Generate an API key
4. The installer will ask for this key

### Perplexity (Optional - For Web Search)
Enables real-time web search capabilities.

**Pricing**:
- 🆓 **Free tier available!** (Limited requests)
- 💎 Pro tier: $5/month for more requests
- 🔗 Get your key: [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api)

**Benefits of adding Perplexity:**
- Current news and events
- Real-time weather data
- Stock prices and crypto rates
- Sports scores and results
- Recent research and discoveries

## 🌍 Languages

Support for **19 languages** with regional dialects:

<details>
<summary><b>View all supported languages</b></summary>

- 🇬🇧 **English**
- 🇩🇪 **German** (+ Schwäbisch, Bayerisch, Sächsisch)
- 🇫🇷 **French**
- 🇮🇹 **Italian**
- 🇪🇸 **Spanish** (+ Mexican, Argentinian, Colombian, Venezuelan, Chilean, Andaluz)
- 🏴 **Catalan**
- 🏴 **Basque** (Euskera)
- 🏴 **Galician**
- 🇨🇳 **Chinese** (Mandarin)
- 🇮🇳 **Hindi**

</details>

## 🎮 Usage

After installation, use your chosen command (default: `ai`):

```bash
# Basic chat
ai "Hello!"

# Web search (if Perplexity configured)
ai "What's happening in tech today?"

# Open configuration
ai /config

# Clear screen
ai clear

# Exit
ai exit
```

### Pro Tips
- 🎯 Press `ESC` to quickly exit chat mode
- 🔧 Use `/config` to change language, model, or command
- 🧹 Clear chat history with option 7 in config menu
- ⚡ Choose `gpt-4o-mini` for faster, cheaper responses
- 🧠 Choose `gpt-4o` for best quality (recommended)

## 🛠️ Configuration

The configuration menu (`/config`) lets you:
1. **Change command** - Use `ai`, `ask`, `q`, `??`, or custom
2. **Change language** - Switch between 19 languages
3. **Change timeout** - Adjust session memory duration
4. **Toggle ESC key** - Enable/disable quick exit
5. **Change AI model** - Select OpenAI model
6. **Configure web search** - Add/remove Perplexity
7. **Clear cache** - Reset conversation history
8. **Uninstall** - Complete removal with cleanup

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### 🌟 Star this repo
If you find this useful, please star the repository!

### 🐛 Report bugs
Open an issue with:
- Your OS and shell version
- Error messages
- Steps to reproduce

### 💡 Suggest features
We'd love to hear your ideas for:
- New language support
- Additional AI providers
- UI improvements
- New commands

### 🔧 Submit PRs
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to your branch
5. Open a Pull Request

### 📚 Module System
Want to add new capabilities? Create a module:
```bash
# Example: weather module
modules/weather.zsh
```

## 📈 Roadmap

- [ ] Voice input/output support
- [ ] Multiple AI providers (Claude, Gemini)
- [ ] Plugin system for extensions
- [ ] Conversation export (Markdown, PDF)
- [ ] Team sharing features
- [ ] Docker container support

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 💖 Support

If you find this project helpful, please:
- ⭐ Star this repository
- 🐦 Share on social media
- 💬 Tell your friends
- ☕ [Buy me a coffee](https://buymeacoffee.com/martinschenk)

---

<div align="center">
Made with ❤️ by the open-source community

**[Report Bug](https://github.com/martinschenk/ai-chat-terminal/issues) • [Request Feature](https://github.com/martinschenk/ai-chat-terminal/issues)**
</div>