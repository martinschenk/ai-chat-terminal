#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Chat Terminal - Database Migration
Migrates between encrypted and plaintext SQLite databases
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional

def migrate_to_encrypted(source_db: str, target_db: str, key: str) -> bool:
    """
    Migrate plaintext SQLite database to encrypted SQLCipher database

    Args:
        source_db: Path to plaintext SQLite database
        target_db: Path to create encrypted database
        key: Hex-encoded encryption key

    Returns:
        True if successful, False otherwise
    """
    try:
        import sqlite3
        import sqlcipher3

        if not os.path.exists(source_db):
            print(f"Error: Source database not found: {source_db}", file=sys.stderr)
            return False

        print(f"📦 Migrating {source_db} to encrypted database...", file=sys.stderr)

        # Open source (plaintext) database
        source_conn = sqlite3.connect(source_db)

        # Open target (encrypted) database
        target_conn = sqlcipher3.connect(target_db)
        target_conn.execute(f"PRAGMA key = \"x'{key}'\"")
        target_conn.execute("PRAGMA cipher_page_size = 4096")
        target_conn.execute("PRAGMA kdf_iter = 64000")
        target_conn.execute("PRAGMA cipher_hmac_algorithm = HMAC_SHA512")
        target_conn.execute("PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA512")

        # Backup source data via SQL dump
        for line in source_conn.iterdump():
            if line not in ('BEGIN;', 'COMMIT;'):  # Skip transaction control
                try:
                    target_conn.execute(line)
                except Exception as e:
                    # Skip errors for metadata tables
                    if 'already exists' not in str(e).lower():
                        print(f"Warning: {e}", file=sys.stderr)

        target_conn.commit()
        source_conn.close()
        target_conn.close()

        print("✅ Migration completed successfully", file=sys.stderr)
        return True

    except ImportError as e:
        print(f"Error: Required module not available: {e}", file=sys.stderr)
        print("Install with: pip3 install sqlcipher3-binary", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error during migration: {e}", file=sys.stderr)
        return False


def export_to_plaintext(source_db: str, target_db: str, key: str) -> bool:
    """
    Export encrypted SQLCipher database to plaintext SQLite

    Args:
        source_db: Path to encrypted SQLCipher database
        target_db: Path to create plaintext database
        key: Hex-encoded encryption key

    Returns:
        True if successful, False otherwise
    """
    try:
        import sqlite3
        import sqlcipher3

        if not os.path.exists(source_db):
            print(f"Error: Source database not found: {source_db}", file=sys.stderr)
            return False

        print(f"📤 Exporting {source_db} to plaintext database...", file=sys.stderr)

        # Open source (encrypted) database
        source_conn = sqlcipher3.connect(source_db)
        source_conn.execute(f"PRAGMA key = \"x'{key}'\"")

        # Verify key is correct
        try:
            source_conn.execute("SELECT count(*) FROM sqlite_master")
        except Exception as e:
            print(f"Error: Failed to decrypt database. Wrong key?", file=sys.stderr)
            print(f"Details: {e}", file=sys.stderr)
            source_conn.close()
            return False

        # Open target (plaintext) database
        target_conn = sqlite3.connect(target_db)

        # Export via SQL dump
        for line in source_conn.iterdump():
            if line not in ('BEGIN;', 'COMMIT;'):
                try:
                    target_conn.execute(line)
                except Exception as e:
                    if 'already exists' not in str(e).lower():
                        print(f"Warning: {e}", file=sys.stderr)

        target_conn.commit()
        source_conn.close()
        target_conn.close()

        print(f"✅ Export completed: {target_db}", file=sys.stderr)
        print(f"⚠️  WARNING: {target_db} is NOT encrypted!", file=sys.stderr)
        return True

    except ImportError as e:
        print(f"Error: Required module not available: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error during export: {e}", file=sys.stderr)
        return False


def backup_database(db_path: str) -> Optional[str]:
    """
    Create backup of database file

    Args:
        db_path: Path to database file

    Returns:
        Path to backup file, or None if failed
    """
    try:
        if not os.path.exists(db_path):
            return None

        backup_path = f"{db_path}.backup"
        shutil.copy2(db_path, backup_path)
        print(f"💾 Backup created: {backup_path}", file=sys.stderr)
        return backup_path

    except Exception as e:
        print(f"Error creating backup: {e}", file=sys.stderr)
        return None


def main():
    """Command line interface for database migration"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Migrate to encrypted:   python3 db_migration.py migrate <source.db> <target.db> <key>")
        print("  Export to plaintext:    python3 db_migration.py export <source.db> <target.db> <key>")
        print("  Backup database:        python3 db_migration.py backup <database.db>")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'migrate':
        if len(sys.argv) != 5:
            print("Error: migrate requires source, target, and key")
            sys.exit(1)

        source = sys.argv[2]
        target = sys.argv[3]
        key = sys.argv[4]

        # Create backup first
        backup_database(source)

        # Migrate
        success = migrate_to_encrypted(source, target, key)
        sys.exit(0 if success else 1)

    elif command == 'export':
        if len(sys.argv) != 5:
            print("Error: export requires source, target, and key")
            sys.exit(1)

        source = sys.argv[2]
        target = sys.argv[3]
        key = sys.argv[4]

        success = export_to_plaintext(source, target, key)
        sys.exit(0 if success else 1)

    elif command == 'backup':
        if len(sys.argv) != 3:
            print("Error: backup requires database path")
            sys.exit(1)

        db_path = sys.argv[2]
        backup_path = backup_database(db_path)
        sys.exit(0 if backup_path else 1)

    else:
        print(f"Error: Unknown command '{command}'")
        sys.exit(1)


if __name__ == '__main__':
    main()
