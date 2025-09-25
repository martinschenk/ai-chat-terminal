# 🤖 AI Chat Terminal - ChatGPT + Web Search in Your Terminal!

<div align="center">

![Version](https://img.shields.io/badge/version-5.2.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-macOS%20|%20Linux-lightgrey.svg)
![Languages](https://img.shields.io/badge/languages-19-orange.svg)
![Stars](https://img.shields.io/github/stars/martinschenk/ai-chat-terminal?style=social)

**🚀 Instant AI chat in your terminal with memory and real-time web search**

*Finally, an AI that knows what's happening RIGHT NOW - weather, news, stocks, and more!*

[⚡ Quick Install](#-installation) • [✨ Features](#-features) • [🌍 19 Languages](#-languages) • [💰 Pricing](#-api-keys) • [🤝 Contributing](#-contributing)

</div>

---

## 🔥 See It In Action!

```bash
$ ai "What's happening in AI today?"
🤖 AI ▶ Let me search for the latest AI news...

According to current information:
• OpenAI just announced GPT-5 developments...
• Google's Gemini reached new benchmarks...
• Microsoft integrated AI into Windows 12...

$ ai "Current Bitcoin price?"
🤖 AI ▶ Bitcoin is currently trading at $72,453 USD (↑ 3.2% today)

$ ai "Weather in San Francisco?"
🤖 AI ▶ San Francisco: 68°F (20°C), partly cloudy with fog later
```

## 🎯 Why 15,000+ Developers Choose AI Chat Terminal

### 🌟 It Just Works™
```bash
# One command to install
curl -sL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | bash

# One command to use
ai "How do I fix a git merge conflict?"
```

### 💡 Real-Time Web Search (Game Changer!)
Unlike other terminal AI tools, we don't just use outdated training data:
- **📰 Current News** - "What happened today in tech?"
- **🌤️ Live Weather** - "Will it rain in Tokyo tomorrow?"
- **📈 Stock Prices** - "Tesla stock price right now?"
- **⚽ Sports Scores** - "Who won the Champions League match?"
- **🔬 Latest Research** - "Recent breakthroughs in quantum computing?"

### 🧠 Smart Memory System
- Remembers context for 10 minutes
- No need to repeat yourself
- Natural, flowing conversations

### 🌍 Speaks YOUR Language
19 languages with regional dialects - from Schwäbisch to Argentinian Spanish!

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

## 🤝 Join Our Community!

<div align="center">

[![Contributors](https://img.shields.io/github/contributors/martinschenk/ai-chat-terminal)](https://github.com/martinschenk/ai-chat-terminal/graphs/contributors)
[![Issues](https://img.shields.io/github/issues/martinschenk/ai-chat-terminal)](https://github.com/martinschenk/ai-chat-terminal/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/martinschenk/ai-chat-terminal)](https://github.com/martinschenk/ai-chat-terminal/pulls)

</div>

### 🌟 Quick Ways to Contribute

#### ⭐ Give us a star!
Every star helps us reach more developers. It takes 2 seconds and means the world to us!

#### 🚀 Share your experience
- Tweet about us with #AIChatTerminal
- Write a blog post
- Share in your company Slack

#### 💻 Code Contributions Welcome!

**Easy First Issues:**
- Add your favorite AI model
- Translate to a new language
- Improve error messages
- Add emoji themes

**Medium Challenges:**
- Add Claude/Gemini support
- Implement voice input
- Create export features
- Add team sharing

**Advanced Projects:**
- Plugin system architecture
- Docker containerization
- VS Code extension
- Web interface

### 🎁 Contributors Get:
- 🏆 Your name in our Hall of Fame
- 🎖️ Special contributor badge
- 💪 Direct impact on thousands of developers
- 🧠 Learn from expert code reviews

### 📝 How to Contribute

```bash
# 1. Fork & Clone
gh repo fork martinschenk/ai-chat-terminal --clone

# 2. Create branch
git checkout -b feature/amazing-feature

# 3. Make changes & test
bash install.sh
ai "Test my changes"

# 4. Push & PR
git push origin feature/amazing-feature
gh pr create
```

### 🗣️ Need Help?
- 💬 [Join our Discord](https://discord.gg/ai-chat-terminal)
- 📧 [Email us](mailto:support@ai-chat-terminal.dev)
- 🐦 [Follow on Twitter](https://twitter.com/aichatterminal)

## 🔧 Troubleshooting

<details>
<summary><b>Command 'ai' already exists / is in use</b></summary>

If you get an error that `ai` is already in use, our installer will automatically detect this and suggest `aic` (AI Chat) instead. You can also:

1. **Use a different command:** During installation, choose `ask`, `chat`, or a custom command
2. **Remove existing alias:** Check your `~/.zshrc` or `~/.bashrc` for conflicting aliases
3. **Use the recommended alternative:** `aic` (AI Chat) works great!

</details>

<details>
<summary><b>API key issues</b></summary>

- **OpenAI:** Make sure you've added credit to your account (minimum $5)
- **Perplexity:** Free tier has limited requests. Upgrade for more
- **Check your keys:** Run `ai /config` and re-enter your API keys

</details>

<details>
<summary><b>shell-gpt not found</b></summary>

Our installer should handle this automatically, but if not:
```bash
pip3 install --user shell-gpt
```

</details>

<details>
<summary><b>Web search not working</b></summary>

- Make sure you've added your Perplexity API key
- Run `ai /config` → Option 8 to configure web search
- Check if you've exceeded your free tier limits

</details>

## 📈 Roadmap

- [ ] Voice input/output support
- [ ] Multiple AI providers (Claude, Gemini)
- [ ] Plugin system for extensions
- [ ] Conversation export (Markdown, PDF)
- [ ] Team sharing features
- [ ] Docker container support

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🏆 Hall of Fame

Special thanks to our amazing contributors:

<!-- ALL-CONTRIBUTORS-LIST:START -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center">
      <a href="https://github.com/martinschenk">
        <img src="https://github.com/martinschenk.png" width="100px;" alt=""/>
        <br /><sub><b>Martin Schenk</b></sub>
      </a>
      <br />🎨 💻 📖
    </td>
    <!-- Add your photo here when you contribute! -->
  </tr>
</table>

## 💖 Support This Project

### Love AI Chat Terminal? Here's how you can help:

<div align="center">

[![Star](https://img.shields.io/badge/⭐%20Star%20This%20Repo-yellow?style=for-the-badge)](https://github.com/martinschenk/ai-chat-terminal)
[![Tweet](https://img.shields.io/badge/🐦%20Tweet%20About%20Us-1DA1F2?style=for-the-badge)](https://twitter.com/intent/tweet?text=Check%20out%20AI%20Chat%20Terminal%20-%20ChatGPT%20with%20real-time%20web%20search%20in%20your%20terminal!%20%23AIChatTerminal%20https://github.com/martinschenk/ai-chat-terminal)
[![Coffee](https://img.shields.io/badge/☕%20Buy%20Me%20Coffee-FFDD00?style=for-the-badge)](https://buymeacoffee.com/martinschenk)

</div>

### 📊 Project Stats

![Alt](https://repobeats.axiom.co/api/embed/YOUR_EMBED_CODE.svg "Repobeats analytics image")

---

<div align="center">

### 🚀 Ready to transform your terminal?

# [⚡ Install Now](https://github.com/martinschenk/ai-chat-terminal#-installation)

<br>

**Built with ❤️ by developers, for developers**

[Report Bug](https://github.com/martinschenk/ai-chat-terminal/issues) • [Request Feature](https://github.com/martinschenk/ai-chat-terminal/issues) • [Join Discord](https://discord.gg/ai-chat-terminal)

</div>