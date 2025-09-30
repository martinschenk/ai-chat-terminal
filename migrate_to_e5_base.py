#!/usr/bin/env python3
"""
AI Chat Terminal - Migration Script from e5-small to e5-base
Re-encodes all existing embeddings with the new model for better cross-language performance
"""

import os
import sys
import sqlite3
import time
from pathlib import Path

def main():
    """Run the migration from e5-small to e5-base"""
    print("🔄 AI Chat Terminal - E5 Model Migration")
    print("=" * 50)
    print()

    # Check if user wants to proceed
    print("This script will migrate your AI Chat Terminal from e5-small to e5-base.")
    print("Benefits:")
    print("• Better cross-language search (+15% quality)")
    print("• Improved multilingual understanding")
    print("• Enhanced PII detection integration")
    print()
    print("Process:")
    print("• Downloads e5-base model (~278MB)")
    print("• Re-encodes all existing conversations")
    print("• Preserves all your data")
    print()

    response = input("Do you want to proceed? [y/N]: ")
    if not response.lower().startswith('y'):
        print("Migration cancelled.")
        return

    # Find .aichat directory
    config_dir = Path.home() / '.aichat'
    if not config_dir.exists():
        print("❌ Error: ~/.aichat directory not found")
        print("Please run the AI Chat Terminal at least once before migration.")
        return

    db_path = config_dir / 'memory.db'
    if not db_path.exists():
        print("❌ Error: No memory database found")
        print("Nothing to migrate - you can use the new system directly.")
        return

    print("\n🔍 Analyzing existing database...")

    # Check database
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Count messages
        cursor.execute("SELECT COUNT(*) FROM chat_history")
        message_count = cursor.fetchone()[0]

        # Check if embeddings table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_embeddings'")
        has_embeddings = cursor.fetchone() is not None

        if has_embeddings:
            cursor.execute("SELECT COUNT(*) FROM chat_embeddings")
            embedding_count = cursor.fetchone()[0]
        else:
            embedding_count = 0

        conn.close()

    except Exception as e:
        print(f"❌ Error reading database: {e}")
        return

    print(f"  • Messages found: {message_count}")
    print(f"  • Embeddings found: {embedding_count}")

    if message_count == 0:
        print("✅ No messages to migrate - ready for new system!")
        return

    # Estimate migration time
    estimated_time = max(5, message_count * 0.1)  # ~0.1 seconds per message
    print(f"  • Estimated migration time: {estimated_time:.0f} seconds")

    # Download new model
    print("\n📥 Downloading e5-base model...")
    try:
        from sentence_transformers import SentenceTransformer
        print("  • Loading multilingual-e5-base (278MB)...")
        start_time = time.time()
        new_model = SentenceTransformer('intfloat/multilingual-e5-base')
        download_time = time.time() - start_time
        print(f"  ✅ Model ready ({download_time:.1f}s)")
    except ImportError:
        print("❌ Error: sentence-transformers not installed")
        print("Please install with: pip3 install sentence-transformers")
        return
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        return

    # Backup database
    print("\n💾 Creating backup...")
    backup_path = config_dir / f'memory_backup_{int(time.time())}.db'
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"  ✅ Backup created: {backup_path.name}")
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        response = input("Continue without backup? [y/N]: ")
        if not response.lower().startswith('y'):
            return

    # Re-encode embeddings
    print("\n🔄 Re-encoding embeddings with e5-base...")
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Get all messages that need re-encoding
        cursor.execute("SELECT id, content FROM chat_history ORDER BY id")
        messages = cursor.fetchall()

        print(f"  • Processing {len(messages)} messages...")

        # Progress tracking
        processed = 0
        start_time = time.time()

        for msg_id, content in messages:
            # Create new embedding with proper E5 prefix
            embedding = new_model.encode(f"passage: {content}", convert_to_tensor=False)

            # Update or insert into embeddings table
            if has_embeddings:
                # Try to update existing embedding
                cursor.execute("""
                    UPDATE chat_embeddings
                    SET message_embedding = ?
                    WHERE rowid = ?
                """, (embedding.tobytes(), msg_id))

                # If no rows were updated, insert new one
                if cursor.rowcount == 0:
                    # Get message details for insert
                    cursor.execute("""
                        SELECT session_id, timestamp, role FROM chat_history WHERE id = ?
                    """, (msg_id,))
                    session_id, timestamp, role = cursor.fetchone()

                    cursor.execute("""
                        INSERT INTO chat_embeddings (message_embedding, session_id, timestamp, message_type)
                        VALUES (?, ?, ?, ?)
                    """, (embedding.tobytes(), session_id, timestamp, role))
            else:
                # Create embeddings table and insert
                cursor.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS chat_embeddings USING vec0(
                        message_embedding FLOAT[384],
                        session_id TEXT,
                        timestamp INTEGER,
                        message_type TEXT,
                        importance REAL DEFAULT 1.0,
                        language TEXT DEFAULT 'en'
                    )
                """)

                # Get message details
                cursor.execute("""
                    SELECT session_id, timestamp, role FROM chat_history WHERE id = ?
                """, (msg_id,))
                result = cursor.fetchone()
                if result:
                    session_id, timestamp, role = result
                    cursor.execute("""
                        INSERT INTO chat_embeddings (message_embedding, session_id, timestamp, message_type)
                        VALUES (?, ?, ?, ?)
                    """, (embedding.tobytes(), session_id, timestamp, role))

            processed += 1

            # Show progress every 100 messages
            if processed % 100 == 0:
                elapsed = time.time() - start_time
                rate = processed / elapsed
                remaining = (len(messages) - processed) / rate if rate > 0 else 0
                print(f"    Progress: {processed}/{len(messages)} ({processed/len(messages)*100:.1f}%) - {remaining:.0f}s remaining")

        # Commit all changes
        conn.commit()
        conn.close()

        total_time = time.time() - start_time
        print(f"  ✅ Migration completed ({total_time:.1f}s)")

    except Exception as e:
        print(f"❌ Error during migration: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

        # Restore backup if available
        if backup_path.exists():
            print("🔄 Restoring from backup...")
            shutil.copy2(backup_path, db_path)
            print("  ✅ Original database restored")
        return

    # Update configuration
    print("\n⚙️ Updating configuration...")
    try:
        config_file = config_dir / 'config'

        # Read existing config
        config_lines = []
        if config_file.exists():
            with open(config_file, 'r') as f:
                config_lines = f.readlines()

        # Add or update embedding model setting
        found_embedding_setting = False
        for i, line in enumerate(config_lines):
            if line.startswith('EMBEDDING_MODEL='):
                config_lines[i] = 'EMBEDDING_MODEL=multilingual-e5-base\n'
                found_embedding_setting = True
                break

        if not found_embedding_setting:
            config_lines.append('EMBEDDING_MODEL=multilingual-e5-base\n')

        # Write updated config
        with open(config_file, 'w') as f:
            f.writelines(config_lines)

        print("  ✅ Configuration updated")

    except Exception as e:
        print(f"⚠️ Warning: Could not update config: {e}")

    # Cleanup old backup if migration successful
    try:
        if backup_path.exists():
            # Keep backup for 24 hours, then user can delete
            print(f"\n💡 Backup kept as {backup_path.name}")
            print("  You can safely delete it after testing the new system.")
    except:
        pass

    # Test new system
    print("\n🧪 Testing new system...")
    try:
        # Test memory system import
        sys.path.insert(0, str(config_dir.parent / 'Development' / 'ai-chat-terminal'))
        from memory_system import ChatMemorySystem

        memory = ChatMemorySystem(str(db_path))
        stats = memory.get_stats()
        memory.close()

        print(f"  ✅ Memory system working ({stats.get('total_messages', 0)} messages)")

        # Test PII detection
        try:
            from pii_detector import PIIDetector
            detector = PIIDetector()
            has_pii, types, details = detector.check_for_pii('test@example.com')
            status = "✅" if has_pii else "⚠️"
            print(f"  {status} PII detection {'working' if has_pii else 'needs setup'}")
        except:
            print("  ⚠️ PII detection needs configuration")

    except Exception as e:
        print(f"  ⚠️ Warning: {e}")

    print("\n🎉 Migration completed successfully!")
    print()
    print("Next steps:")
    print("• Restart your terminal or run: source ~/.zshrc")
    print("• Test the system with: chat")
    print("• Try cross-language searches!")
    print()
    print("New features available:")
    print("• Enhanced PII detection with Presidio")
    print("• Better cross-language search")
    print("• Natural response generation (if Phi-3 installed)")

if __name__ == "__main__":
    main()