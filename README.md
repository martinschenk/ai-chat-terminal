# 🤖 AI Chat Terminal - Instant & Simple

**Instant AI chat in your terminal with memory.** No menus, no hassle - just type and chat!

![Version](https://img.shields.io/badge/version-3.5.0-blue)
![Memory](https://img.shields.io/badge/memory-2%20minutes-red)
![Languages](https://img.shields.io/badge/languages-16%20Total-orange)
![OS](https://img.shields.io/badge/OS-macOS%20|%20Linux-green)

## 🚀 Super Easy Installation - Just Copy & Paste!

**No experience needed! Just copy this line and paste it in your terminal:**

```bash
curl -sSL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | bash
```

### 📝 Step-by-Step for Beginners:

1. **Open your Terminal**
   - Mac: Press `Cmd + Space`, type "Terminal", hit Enter
   - Linux: Press `Ctrl + Alt + T`

2. **Copy the command above** (the line starting with `curl`)

3. **Paste it in Terminal** and press Enter

4. **Follow the simple prompts:**
   - Choose your command (just press Enter for default `q`)
   - Pick your language (English or German)
   - Enter your OpenAI API key (the installer shows you how to get one!)

5. **That's it!** Type `q` to start chatting

### 🎯 What the installer does:
- ✅ Downloads everything automatically
- ✅ Works from ANY directory (no need to navigate anywhere!)
- ✅ Sets up your shell configuration
- ✅ Guides you through API key setup
- ✅ Ready to chat in 30 seconds

## 💬 Instant Chat - No Menus!

### Start chatting immediately:
```bash
q
# You're now in chat mode! Just type...
```

### Ask a quick question:
```bash
q What's the capital of France?
# Get instant answer and continue chatting
```

### The AI remembers context:
```bash
q My name is Alice
# "Hello Alice! Nice to meet you."

q What's my name?
# "Your name is Alice."
```

## ⚡ Features

- **🧠 Memory** - Remembers your conversation for 2 minutes
- **⚡ Instant** - No menus, starts immediately
- **🎮 Game-Style Config** - Type `/config` in chat for settings
- **🚪 Quick Exit** - Press `ESC` or type `exit`
- **🌍 Multi-Language** - 15 variants total (with regional dialects!)
- **📱 Simple** - One command does everything

## 🎮 In-Chat Commands

While chatting, use these commands:

| Command | Action |
|---------|--------|
| `/config` | Open settings menu |
| `clear` | Clear screen |
| `exit` | Exit chat |
| `ESC` key | Quick exit (if enabled) |

## ⚙️ Configuration

Type `/config` while in chat to see this menu:

```
⚙️  CONFIGURATION

╔═══════════════════════════════════════╗
║  Current Settings:                   ║
║  ├─ Command: q                       ║
║  ├─ Language: en                     ║
║  ├─ Timeout: 120s                    ║
║  └─ ESC to exit: true                ║
╠═══════════════════════════════════════╣
║  [1] Change command character        ║
║  [2] Change language                 ║
║  [3] Change timeout                  ║
║  [4] Toggle ESC key exit             ║
║  [5] Change AI model                 ║
║  [6] Back to chat                    ║
╚═══════════════════════════════════════╝
```

## 📋 Requirements

- **OS**: macOS or Linux (sorry, no Windows yet)
- **Shell**: zsh, bash, or sh
- **Python**: 3.8+
- **API Key**: OpenAI API key ([get one here](https://platform.openai.com/api-keys))

## 🪟 Windows Users

Options for Windows:
1. **WSL** - Windows Subsystem for Linux (recommended)
2. **Git Bash** - May work with limitations
3. **Cygwin** - Unix-like environment for Windows

## 🔧 Alternative Installation Methods

### Method 1: Download and Run (if curl doesn't work)
```bash
# Go to your home directory (or any directory you like!)
cd ~

# Download the installer
wget https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh

# Make it executable
chmod +x install.sh

# Run it
./install.sh

# Reload your shell
source ~/.zshrc  # or ~/.bashrc

# Start chatting!
q
```

### Method 2: Manual Git Clone
```bash
# 1. Go to any directory (home is fine)
cd ~

# 2. Clone the repository
git clone https://github.com/martinschenk/ai-chat-terminal.git

# 3. Enter the directory
cd ai-chat-terminal

# 4. Run installer
./install.sh

# 5. Reload shell
source ~/.zshrc  # or ~/.bashrc

# 6. Start chatting!
q
```

## 🧩 Project Structure

Super simple - just 3 files:

```
ai-chat-terminal/
├── chat.zsh          # Main chat function
├── install.sh        # Smart installer
└── languages/        # Language packs (15 total!)
    ├── en.conf       # English
    ├── de.conf       # German (Hochdeutsch)
    ├── de-schwaebisch.conf  # Schwäbisch
    ├── de-bayerisch.conf    # Bayerisch
    ├── de-saechsisch.conf   # Sächsisch
    ├── fr.conf       # French
    ├── it.conf       # Italian
    ├── es.conf       # Spanish (Standard)
    ├── es-mexicano.conf     # Mexican Spanish
    ├── es-argentino.conf    # Argentinian Spanish
    ├── es-colombiano.conf   # Colombian Spanish
    ├── es-chileno.conf      # Chilean Spanish
    ├── es-andaluz.conf      # Andalusian Spanish
    ├── zh.conf       # Chinese (Mandarin)
    └── hi.conf       # Hindi
```

## 🌍 Supported Languages

**Main Languages:**
- 🇬🇧 English (en)
- 🇩🇪 German (de) - with 3 dialects!
- 🇫🇷 French (fr)
- 🇮🇹 Italian (it)
- 🇪🇸 Spanish (es) - with 5 regional variants!
- 🇨🇳 Chinese Mandarin (zh)
- 🇮🇳 Hindi (hi)

**German Dialects (Easter Egg!):**
- Schwäbisch - Southern German charm
- Bayerisch - Bavarian style
- Sächsisch - Saxon dialect

**Spanish Variants (¡Órale!):**
- 🇲🇽 Mexicano - ¡Órale, güey!
- 🇦🇷 Argentino - Che, ¿cómo andás?
- 🇨🇴 Colombiano - ¡Qué más, parce!
- 🇨🇱 Chileno - ¿Cachai po?
- 🇪🇸 Andaluz - ¡Quillo, qué arte!

First run asks for your language preference!

## 🌍 Add Your Language

Create `languages/your-lang.conf`:

```bash
LANG_LABEL_YOU="You"
LANG_LABEL_AI="AI"
LANG_MSG_GOODBYE="Goodbye!"
LANG_HEADER_CONTINUE="Continue"
LANG_STATUS_SECONDS="s"
```

Then set it: `/config` → Option 2 → Enter your language code

## 🐛 Troubleshooting

### One-liner installation not working?

**"curl: command not found"**
- Use the wget method above (Method 1)
- Or install curl first: `sudo apt-get install curl` (Linux) or `brew install curl` (Mac)

**"Permission denied"**
```bash
# Add sudo if needed:
curl -sSL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | sudo bash
```

**Behind a firewall/proxy?**
- Download the files manually from: https://github.com/martinschenk/ai-chat-terminal
- Then follow Method 2 above

### After Installation Issues

**"Command not found" after installation**
```bash
# Reload your shell configuration
source ~/.zshrc  # for zsh
source ~/.bashrc  # for bash
# Or just close and reopen your terminal!
```

**API Key Issues**
- The chat will guide you on first run if no key is found
- Or set manually:
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### Test Memory Feature
```bash
q my favorite color is blue
q what's my favorite color?
# Should respond: "Your favorite color is blue"
```

## 🎯 Pro Tips

1. **Quick workflow**: `q` → chat → `ESC` to exit
2. **Context matters**: Stay within 2 minutes for memory
3. **Custom commands**: Create aliases
   ```bash
   alias code="q write code for"
   alias fix="q find the bug in"
   ```

## 📝 License

MIT - Use it, modify it, share it!

## 🙏 Credits

- Powered by [Shell GPT](https://github.com/TheR1D/shell_gpt)
- OpenAI for the API
- You for using it!

---

**⭐ If this makes your terminal smarter, star the repo!**

## 🎉 Complete Beginner? Start Here!

**Just 3 simple steps:**

```bash
# STEP 1: Copy and paste this line into your terminal
curl -sSL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | bash

# STEP 2: Reload your terminal (copy & paste this)
source ~/.zshrc   # Mac users
source ~/.bashrc  # Linux users

# STEP 3: Start chatting!
q

# 🎊 That's it! You're now chatting with AI!
```

**First time? The chat will help you get an API key!**