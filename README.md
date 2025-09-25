# Shell Scripts Collection

Personal collection of shell scripts and functions for Mac Studio.

## Structure

### 📁 ai-chat/
AI-powered chat functions for terminal
- `f_function.zsh` - Interactive AI chat with sgpt (Shell GPT)
  - Single query mode: `f your question here`
  - Interactive mode: just type `f`
  - 2-minute context retention
  - Beautiful UI with colors and icons

## Installation

Add to your `~/.zshrc`:
```bash
source ~/shell-scripts/ai-chat/f_function.zsh
alias f='noglob f_function'
```

## Requirements
- sgpt (shell-gpt) installed via pip
- OpenAI API key configured
- zsh shell

## Usage

### Quick question
```bash
f what is 2+2
```

### Interactive chat
```bash
f
# Then type your questions
# Use exit, quit, or bye to leave
# Or press Ctrl+C
```