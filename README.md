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

### Development Assistance
```
/config = settings | ESC/exit = quit
─────────────────────────────────────────────────────

👤 You ▶ I'm setting up a React app with TypeScript. What's the best folder structure?
🤖 AI ▶
For a React TypeScript app, I recommend this structure:

src/
├── components/          # Reusable UI components
│   ├── common/         # Shared components
│   └── ui/             # Basic UI elements
├── pages/              # Route components
├── hooks/              # Custom React hooks
├── services/           # API calls and external services
├── types/              # TypeScript type definitions
├── utils/              # Helper functions
└── styles/             # CSS/SCSS files

This keeps your code organized and scalable. Would you like me to explain any specific part?
─────────────────────────────────────────────────────

👤 You ▶ show me the tsconfig.json for this setup
🤖 AI ▶
Here's a solid tsconfig.json for your React TypeScript setup:

{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["DOM", "DOM.Iterable", "ES6"],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noFallthroughCasesInSwitch": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "baseUrl": "src",
    "paths": {
      "@/*": ["*"],
      "@/components/*": ["components/*"],
      "@/types/*": ["types/*"]
    }
  },
  "include": ["src"]
}

The paths configuration allows clean imports like `import Button from '@/components/Button'`.
─────────────────────────────────────────────────────

👤 You ▶ datetime?
🤖 AI ▶
Based on your local information, the current date and time is Saturday, September 27, 2025, at 00:26.
─────────────────────────────────────────────────────

👤 You ▶ what's the latest in JavaScript frameworks today?
🤖 AI ▶
As of September 27, 2025, here are the latest developments in JavaScript frameworks:

**React 19 RC** - Released with exciting features like Server Components becoming stable and improved concurrent rendering.

**Next.js 15** - Just launched with enhanced App Router performance and improved developer experience for full-stack applications.

**Vue 3.4** - The latest version includes better TypeScript integration and performance optimizations.

**Svelte 5** - Recently announced with a new reactivity system called "runes" that simplifies state management.

The trend is toward better server-side rendering, improved developer experience, and enhanced performance optimizations across all major frameworks.
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