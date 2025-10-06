#!/bin/bash
# AI Chat Terminal - Complete Fresh Reinstall
# Backs up DB (keeps last 5), deletes everything, installs clean from GitHub

set -e

echo "🔄 AI Chat Terminal - Complete Fresh Reinstall"
echo "=============================================="
echo ""

# 1. Stop daemon
echo "1️⃣ Stopping daemon..."
pkill -9 -f chat_daemon.py 2>/dev/null || true
sleep 1

# 2. Backup database (keep last 5)
if [ -f ~/.aichat/memory.db ]; then
    echo "2️⃣ Backing up database..."
    BACKUP_DIR=~/aichat-backups
    mkdir -p "$BACKUP_DIR"
    
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    cp ~/.aichat/memory.db "$BACKUP_DIR/memory-$TIMESTAMP.db"
    echo "   ✅ Saved: $BACKUP_DIR/memory-$TIMESTAMP.db"
    
    # Keep only last 5 backups
    cd "$BACKUP_DIR"
    ls -t memory-*.db | tail -n +6 | xargs rm -f 2>/dev/null || true
    echo "   📦 Backups kept: $(ls -1 memory-*.db 2>/dev/null | wc -l)"
fi

# 3. Delete everything in .aichat
echo "3️⃣ Deleting ~/.aichat (including .env, config, db)..."
rm -rf ~/.aichat
echo "   ✅ Deleted"

# 4. Delete local git repo to force clean download
echo "4️⃣ Deleting local git repo..."
rm -rf ~/Development/ai-chat-terminal
echo "   ✅ Deleted"

# 5. Fresh install from GitHub via curl (official method)
echo "5️⃣ Installing fresh from GitHub via curl..."
curl -fsSL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | zsh

echo ""
echo "✅ Fresh installation complete!"
echo ""
echo "📦 Database backups: ~/aichat-backups/"
ls -lh ~/aichat-backups/memory-*.db 2>/dev/null || echo "   (no backups yet)"
echo ""
echo "🚀 Test with: chat remind my email test@test.com"
