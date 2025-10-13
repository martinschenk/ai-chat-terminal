#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Chat Terminal v11.0.0 - Memory System (KISS!)
Simple SQLite database with mydata table - NO vector embeddings, NO complex PII categories!
"""

import os
import sys
import warnings

# Suppress all warnings BEFORE any other imports
warnings.filterwarnings("ignore")
os.environ['PYTHONWARNINGS'] = 'ignore'

import json
import time
from pathlib import Path

# Try SQLCipher first (encrypted), fallback to APSW, then sqlite3
try:
    import sqlcipher3
    USE_SQLCIPHER = True
    USE_APSW = False
except ImportError:
    USE_SQLCIPHER = False
    # Try APSW (has extension support)
    try:
        import apsw
        USE_APSW = True
    except ImportError:
        import sqlite3
        USE_APSW = False

class ChatMemorySystem:
    """
    Simple memory system for AI Chat Terminal v11.0.0

    Database schema:
        mydata (
            id INTEGER PRIMARY KEY,
            content TEXT NOT NULL,     -- The actual data
            meta TEXT,                  -- Simple label: "email", "geburtstag", etc.
            lang TEXT,                  -- Language: en, de, es
            timestamp INTEGER           -- Unix timestamp
        )

    No vector embeddings, no complex metadata, no PII categories!
    """

    def __init__(self, db_path=None, encryption_key=None):
        if db_path is None:
            # Default to ~/.aichat/memory.db
            config_dir = Path.home() / '.aichat'
            config_dir.mkdir(exist_ok=True)
            db_path = config_dir / 'memory.db'

        self.db_path = db_path
        self.encryption_key = encryption_key

        # Connect using SQLCipher, APSW, or sqlite3
        if USE_SQLCIPHER and encryption_key:
            # Use SQLCipher with encryption
            self.db = sqlcipher3.connect(str(db_path))
            # Set encryption key
            self.db.execute(f"PRAGMA key = \"x'{encryption_key}'\"")
            # Optimize performance
            self.db.execute("PRAGMA cipher_page_size = 4096")
            self.db.execute("PRAGMA kdf_iter = 64000")
            self.db.execute("PRAGMA cipher_hmac_algorithm = HMAC_SHA512")
            self.db.execute("PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA512")
        elif USE_APSW:
            # Use APSW (no encryption)
            self.db = apsw.Connection(str(db_path))
        else:
            # Use sqlite3 (no encryption)
            self.db = sqlite3.connect(str(db_path))

        # Create compatibility wrapper for APSW
        if USE_APSW:
            self._setup_apsw_compatibility()

        self._create_tables()

    def _setup_apsw_compatibility(self):
        """Make APSW behave like sqlite3 for common operations"""
        original_db = self.db

        class APSWCursorWrapper:
            """Wrapper to make APSW cursor compatible with sqlite3"""
            def __init__(self, cursor, conn):
                self._cursor = cursor
                self._conn = conn

            def execute(self, sql, params=()):
                return self._cursor.execute(sql, params)

            def fetchone(self):
                return self._cursor.fetchone()

            def fetchall(self):
                return self._cursor.fetchall()

            @property
            def lastrowid(self):
                return self._conn.last_insert_rowid()

            def __getattr__(self, name):
                return getattr(self._cursor, name)

        class APSWWrapper:
            def __init__(self, conn):
                self._conn = conn

            def execute(self, sql, params=()):
                cursor = self._conn.cursor()
                cursor.execute(sql, params)
                return APSWCursorWrapper(cursor, self._conn)

            def executescript(self, script):
                cursor = self._conn.cursor()
                for statement in script.split(';'):
                    statement = statement.strip()
                    if statement:
                        cursor.execute(statement)
                return APSWCursorWrapper(cursor, self._conn)

            def commit(self):
                pass  # APSW auto-commits

            def close(self):
                self._conn.close()

            def cursor(self):
                cursor = self._conn.cursor()
                return APSWCursorWrapper(cursor, self._conn)

        self.db = APSWWrapper(original_db)

    def _create_tables(self):
        """Create simple mydata table - NO vector embeddings, NO complex metadata!"""
        try:
            self.db.executescript("""
                -- Simple data storage table (v11.0.0 KISS!)
                CREATE TABLE IF NOT EXISTS mydata (
                    id INTEGER PRIMARY KEY,
                    content TEXT NOT NULL,
                    meta TEXT,
                    lang TEXT DEFAULT 'en',
                    timestamp INTEGER DEFAULT (strftime('%s','now'))
                );

                -- Indexes for performance
                CREATE INDEX IF NOT EXISTS idx_mydata_meta ON mydata(meta);
                CREATE INDEX IF NOT EXISTS idx_mydata_timestamp ON mydata(timestamp);
                CREATE INDEX IF NOT EXISTS idx_mydata_lang ON mydata(lang);
            """)

            self.db.commit()
        except Exception as e:
            print(f"Error creating tables: {e}")
            sys.exit(1)

    def execute_sql(self, sql: str, params: tuple = (), fetch: bool = False):
        """
        Execute SQL directly on database (v11.0.0 - SQL from Qwen!)

        Args:
            sql: SQL statement (validated by qwen_sql_generator)
            params: Query parameters
            fetch: If True, return results; otherwise return None

        Returns:
            Query results if fetch=True, None otherwise
        """
        try:
            cursor = self.db.execute(sql, params)
            self.db.commit()

            if fetch:
                return cursor.fetchall()

            return cursor.lastrowid if hasattr(cursor, 'lastrowid') else None

        except Exception as e:
            print(f"SQL execution error: {e}", file=sys.stderr)
            return None if fetch else 0

    def save_data(self, content: str, meta: str = None, lang: str = 'en') -> int:
        """
        Save data to mydata table (simplified!)

        Args:
            content: The actual data to store
            meta: Simple label ("email", "geburtstag", etc.)
            lang: Language code (en, de, es)

        Returns:
            ID of inserted row
        """
        try:
            cursor = self.db.execute(
                "INSERT INTO mydata (content, meta, lang) VALUES (?, ?, ?)",
                (content, meta, lang)
            )
            self.db.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error saving data: {e}", file=sys.stderr)
            return 0

    def search_data(self, query: str, limit: int = 10):
        """
        Search mydata table with LIKE query

        Args:
            query: Search term
            limit: Max results

        Returns:
            List of dicts with id, content, meta, lang, timestamp
        """
        try:
            cursor = self.db.execute("""
                SELECT id, content, meta, lang, timestamp
                FROM mydata
                WHERE content LIKE ? OR meta LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))

            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'content': row[1],
                    'meta': row[2],
                    'lang': row[3],
                    'timestamp': row[4]
                })

            return results

        except Exception as e:
            print(f"Error searching data: {e}", file=sys.stderr)
            return []

    def delete_data(self, pattern: str) -> int:
        """
        Delete data matching pattern

        Args:
            pattern: Search pattern

        Returns:
            Number of deleted rows
        """
        try:
            # Find matching items first
            cursor = self.db.execute("""
                SELECT id FROM mydata
                WHERE content LIKE ? OR meta LIKE ?
            """, (f"%{pattern}%", f"%{pattern}%"))

            ids = [row[0] for row in cursor.fetchall()]

            if ids:
                placeholders = ','.join('?' * len(ids))
                self.db.execute(f"DELETE FROM mydata WHERE id IN ({placeholders})", ids)
                self.db.commit()

            return len(ids)

        except Exception as e:
            print(f"Error deleting data: {e}", file=sys.stderr)
            return 0

    def delete_by_ids(self, ids: list) -> int:
        """
        Delete items by their IDs

        Args:
            ids: List of IDs to delete

        Returns:
            Number of deleted rows
        """
        try:
            if not ids:
                return 0

            placeholders = ','.join('?' * len(ids))
            self.db.execute(f"DELETE FROM mydata WHERE id IN ({placeholders})", ids)
            self.db.commit()

            return len(ids)

        except Exception as e:
            print(f"Error deleting by IDs: {e}", file=sys.stderr)
            return 0

    def list_all_data(self, limit: int = 100):
        """
        List all data in mydata table

        Args:
            limit: Max results

        Returns:
            List of dicts
        """
        try:
            cursor = self.db.execute("""
                SELECT id, content, meta, lang, timestamp
                FROM mydata
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))

            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'content': row[1],
                    'meta': row[2],
                    'lang': row[3],
                    'timestamp': row[4]
                })

            return results

        except Exception as e:
            print(f"Error listing data: {e}", file=sys.stderr)
            return []

    def get_stats(self) -> dict:
        """Get database statistics"""
        try:
            stats = {}

            # Item count
            stats['total_items'] = self.db.execute("SELECT COUNT(*) FROM mydata").fetchone()[0]

            # Database size
            stats['db_size_mb'] = os.path.getsize(self.db_path) / (1024 * 1024)

            # Date range
            date_range = self.db.execute(
                "SELECT MIN(timestamp), MAX(timestamp) FROM mydata"
            ).fetchone()

            if date_range[0]:
                stats['oldest_item'] = time.strftime('%Y-%m-%d', time.localtime(date_range[0]))
                stats['newest_item'] = time.strftime('%Y-%m-%d', time.localtime(date_range[1]))

            return stats
        except Exception as e:
            print(f"Error getting stats: {e}", file=sys.stderr)
            return {}

    def close(self):
        """Close database connection"""
        if self.db:
            self.db.close()


def get_encryption_key_auto() -> str:
    """
    Automatically get encryption key from Keychain
    Returns empty string if encryption not available

    Returns:
        Hex-encoded encryption key or empty string
    """
    try:
        # Import here to avoid circular dependency
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, script_dir)
        from encryption_manager import EncryptionManager

        manager = EncryptionManager()

        # Check if encryption available
        if not manager.is_encryption_available():
            return ""

        # Get or create key
        key = manager.get_or_create_key()
        return key if key else ""

    except ImportError:
        # encryption_manager not available
        return ""
    except Exception as e:
        print(f"Warning: Could not get encryption key: {e}", file=sys.stderr)
        return ""


def main():
    """Command line interface for testing"""
    if len(sys.argv) < 2:
        print("Usage: python3 memory_system.py <command> [args...]")
        print("Commands:")
        print("  stats              - Show database statistics")
        print("  list [limit]       - List all data")
        print("  search <query>     - Search for data")
        print("  save <content> <meta> <lang> - Save data")
        print("  delete <pattern>   - Delete matching data")
        return

    # Get encryption key automatically
    encryption_key = get_encryption_key_auto()

    # Initialize with encryption if available
    memory = ChatMemorySystem(encryption_key=encryption_key)
    command = sys.argv[1]

    try:
        if command == 'stats':
            stats = memory.get_stats()
            print(json.dumps(stats, indent=2))

        elif command == 'list':
            limit = int(sys.argv[2]) if len(sys.argv) >= 3 else 100
            results = memory.list_all_data(limit)
            for item in results:
                date_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(item['timestamp']))
                print(f"[{date_str}] {item['meta'] or 'no label'}: {item['content'][:100]}")

        elif command == 'search' and len(sys.argv) >= 3:
            query = ' '.join(sys.argv[2:])
            results = memory.search_data(query, limit=10)
            for item in results:
                date_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(item['timestamp']))
                print(f"[{date_str}] {item['meta'] or 'no label'}: {item['content']}")

        elif command == 'save' and len(sys.argv) >= 4:
            content = sys.argv[2]
            meta = sys.argv[3] if len(sys.argv) >= 4 else None
            lang = sys.argv[4] if len(sys.argv) >= 5 else 'en'
            item_id = memory.save_data(content, meta, lang)
            print(f"Saved with ID: {item_id}")

        elif command == 'delete' and len(sys.argv) >= 3:
            pattern = sys.argv[2]
            deleted = memory.delete_data(pattern)
            print(f"Deleted {deleted} items")

        else:
            print(f"Unknown command: {command}")

    finally:
        memory.close()

if __name__ == '__main__':
    main()
