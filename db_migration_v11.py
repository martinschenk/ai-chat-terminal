#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Chat Terminal v11.0.0 - Database Migration
Migrates v10 chat_history (complex metadata + vector embeddings) to v11 mydata (simple schema)
"""

import sqlite3
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

def backup_database(db_path: str) -> str:
    """Create timestamped backup of database"""
    backup_path = f"{db_path}.backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    shutil.copy2(db_path, backup_path)
    return backup_path

def migrate_to_v11(db_path: str, dry_run: bool = False) -> dict:
    """
    Migrate v10 database to v11 simple schema

    Args:
        db_path: Path to database file
        dry_run: If True, only analyze without making changes

    Returns:
        dict with migration stats
    """
    db_path = Path(db_path).expanduser()

    if not db_path.exists():
        return {"error": f"Database not found: {db_path}"}

    # Backup first
    if not dry_run:
        backup_path = backup_database(str(db_path))
        print(f"✅ Backup created: {backup_path}")

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Check if old schema exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_history'")
    if not cursor.fetchone():
        return {"error": "No chat_history table found - already migrated?"}

    # Analyze current data
    cursor.execute("SELECT COUNT(*) FROM chat_history WHERE json_extract(metadata, '$.is_private') = 1")
    private_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM chat_history")
    total_count = cursor.fetchone()[0]

    print(f"\n📊 Migration Analysis:")
    print(f"   Total messages: {total_count}")
    print(f"   Private data items: {private_count}")
    print(f"   Will migrate: {private_count} items to mydata table")

    if dry_run:
        conn.close()
        return {
            "dry_run": True,
            "total_messages": total_count,
            "private_items": private_count,
            "will_migrate": private_count
        }

    # Create new mydata table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mydata (
            id INTEGER PRIMARY KEY,
            content TEXT NOT NULL,
            meta TEXT,
            lang TEXT,
            timestamp INTEGER DEFAULT (strftime('%s','now'))
        )
    """)

    # Migrate private data from chat_history
    cursor.execute("""
        SELECT
            content,
            metadata,
            language,
            created_at
        FROM chat_history
        WHERE json_extract(metadata, '$.is_private') = 1
        ORDER BY created_at ASC
    """)

    migrated = 0
    for row in cursor.fetchall():
        content, metadata_json, language, created_at = row

        # Extract meta from old metadata
        meta = None
        if metadata_json:
            try:
                metadata = json.loads(metadata_json)
                # Try to get meaningful label
                meta = metadata.get('data_type') or metadata.get('label') or metadata.get('privacy_category')

                # Clean up PII categories (EMAIL_ADDRESS → email)
                if meta:
                    meta = meta.replace('_ADDRESS', '').replace('_NUMBER', '').replace('_', ' ').lower()
            except json.JSONDecodeError:
                meta = None

        # Insert into mydata
        cursor.execute("""
            INSERT INTO mydata (content, meta, lang, timestamp)
            VALUES (?, ?, ?, ?)
        """, (content, meta, language or 'en', created_at))

        migrated += 1

    # Create indexes for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_mydata_meta ON mydata(meta)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_mydata_timestamp ON mydata(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_mydata_lang ON mydata(lang)")

    # Drop old tables (vector embeddings, old chat history, summaries)
    print("\n🗑️  Cleaning up old tables...")
    cursor.execute("DROP TABLE IF EXISTS chat_embeddings")
    print("   ✓ Dropped chat_embeddings (vector data)")

    cursor.execute("DROP TABLE IF EXISTS chat_history")
    print("   ✓ Dropped chat_history (complex metadata)")

    cursor.execute("DROP TABLE IF EXISTS memory_summaries")
    print("   ✓ Dropped memory_summaries")

    conn.commit()
    conn.close()

    return {
        "success": True,
        "migrated_items": migrated,
        "total_messages": total_count,
        "private_items": private_count,
        "backup_path": backup_path
    }

def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("Usage: python3 db_migration_v11.py <database_path> [--dry-run]")
        print("\nExample:")
        print("  python3 db_migration_v11.py ~/.aichat/memory.db")
        print("  python3 db_migration_v11.py ~/.aichat/memory.db --dry-run")
        sys.exit(1)

    db_path = sys.argv[1]
    dry_run = '--dry-run' in sys.argv

    print("="*60)
    print("AI Chat Terminal v11.0.0 - Database Migration")
    print("="*60)

    if dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be made\n")

    result = migrate_to_v11(db_path, dry_run=dry_run)

    if "error" in result:
        print(f"\n❌ Error: {result['error']}")
        sys.exit(1)

    if dry_run:
        print(f"\n✅ Dry run completed - database unchanged")
        print(f"\nTo run actual migration:")
        print(f"  python3 db_migration_v11.py {db_path}")
    else:
        print(f"\n✅ Migration completed successfully!")
        print(f"   Migrated {result['migrated_items']} items to mydata table")
        print(f"   Old tables removed (chat_history, chat_embeddings, memory_summaries)")
        print(f"   Backup: {result['backup_path']}")

    print("\n" + "="*60)

if __name__ == '__main__':
    main()
