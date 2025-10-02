#!/usr/bin/env zsh
# AI Chat Terminal v9.0.0 - Complete Clean Reinstall from GitHub
#
# What this script does:
# - Deletes ~/.aichat/ completely (USER DATA WILL BE LOST!)
# - Removes shell integration from ~/.zshrc
# - Reinstalls fresh from GitHub main branch
# - Does NOT touch ~/Development/ai-chat-terminal/ (your local dev copy)
# - Does NOT delete Ollama/Phi-3 (global tools)
#
# Usage: zsh reinstall.sh

set -e

echo "🔥 AI Chat Terminal v9.0.0 - Clean Reinstall from GitHub"
echo "=========================================================="
echo ""
echo "⚠️  WARNUNG: Dies löscht KOMPLETT:"
echo "   ❌ ~/.aichat/ (alle lokalen Daten & DB!)"
echo "   ❌ Shell-Integration in ~/.zshrc"
echo "   ❌ Alte Konfiguration"
echo ""
echo "   ✅ ~/Development/ai-chat-terminal/ bleibt unberührt"
echo "   ✅ Phi-3 und Ollama bleiben (global installiert)"
echo "   ✅ Installiert direkt von GitHub main branch"
echo ""
read -q "REPLY?Fortfahren? (y/N): "
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Abgebrochen."
    exit 0
fi

echo ""
echo "📦 Schritt 1: Komplette Bereinigung..."

# Backup DB falls vorhanden
if [[ -f ~/.aichat/memory.db ]]; then
    BACKUP_FILE=~/aichat-backup-$(date +%Y%m%d-%H%M%S).db
    echo "  💾 DB Backup: $BACKUP_FILE"
    cp ~/.aichat/memory.db "$BACKUP_FILE" 2>/dev/null || true
fi

# ALLES löschen
echo "  🗑️  Lösche ~/.aichat/ komplett..."
rm -rf ~/.aichat

# Shell-Integration entfernen
if [[ -f ~/.zshrc ]]; then
    echo "  🗑️  Entferne Shell-Integration aus ~/.zshrc..."
    cp ~/.zshrc ~/.zshrc.backup-$(date +%Y%m%d-%H%M%S)
    grep -v "AI Chat Terminal" ~/.zshrc > ~/.zshrc.tmp 2>/dev/null || cp ~/.zshrc ~/.zshrc.tmp
    grep -v "aichat.zsh" ~/.zshrc.tmp > ~/.zshrc.tmp2 2>/dev/null || cp ~/.zshrc.tmp ~/.zshrc.tmp2
    grep -v "alias chat" ~/.zshrc.tmp2 > ~/.zshrc 2>/dev/null || cp ~/.zshrc.tmp2 ~/.zshrc
    rm -f ~/.zshrc.tmp ~/.zshrc.tmp2
    echo "  ✓ Shell-Integration entfernt"
fi

echo ""
echo "🌐 Schritt 2: Frische Installation von GitHub..."
echo ""

# Direkt von GitHub installieren
curl -fsSL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | zsh

echo ""
echo "✅ Installation von GitHub abgeschlossen!"
echo ""
echo "📝 Nächste Schritte:"
echo ""
echo "  1. Shell neu laden:"
echo "     source ~/.zshrc"
echo ""
echo "  2. Chat starten:"
echo "     chat"
echo ""
echo "  3. v9.0.0 Testen:"
echo "     merke dir meine email test@example.com    (SAVE)"
echo "     was ist eine datenbank?                   (FALSE POSITIVE → OpenAI)"
echo "     wie ist meine email in der db?            (RETRIEVE)"
echo "     zeig mir alles was du gespeichert hast    (LIST - NEU!)"
echo ""
echo "💡 Hinweis: DB ist komplett leer und neu!"
echo ""
