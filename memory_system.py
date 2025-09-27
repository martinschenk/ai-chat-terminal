#!/usr/bin/env python3
"""
AI Chat Terminal - Memory System
SQLite-based semantic memory with vector embeddings
"""

import sqlite3
import json
import time
import sys
import os
import re
from pathlib import Path

try:
    from sentence_transformers import SentenceTransformer
    import sqlite_vec
except ImportError as e:
    print(f"Error: Missing required packages. Please install with:")
    print(f"pip3 install sentence-transformers sqlite-vec")
    sys.exit(1)

class ChatMemorySystem:
    def __init__(self, db_path=None):
        if db_path is None:
            # Default to ~/.aichat/memory.db
            config_dir = Path.home() / '.aichat'
            config_dir.mkdir(exist_ok=True)
            db_path = config_dir / 'memory.db'

        self.db_path = db_path
        self.db = sqlite3.connect(str(db_path))

        # Check for vector extension support
        self.vector_support = False
        try:
            self.db.enable_load_extension(True)
            # Load sqlite-vec extension
            sqlite_vec.load(self.db)
            self.vector_support = True
        except Exception as e:
            # Continue without vector search - basic memory still works
            self.vector_support = False

        # Initialize embedding model (lazy loading)
        self._model = None

        self._create_tables()

    def _get_current_language(self):
        """Get current language from config file"""
        try:
            config_dir = Path.home() / '.aichat'
            config_file = config_dir / 'config'

            if config_file.exists():
                with open(config_file, 'r') as f:
                    content = f.read()
                    # Look for AI_CHAT_LANGUAGE="xx" pattern
                    match = re.search(r'AI_CHAT_LANGUAGE="([^"]+)"', content)
                    if match:
                        return match.group(1)

            return 'en'  # Default to English
        except Exception:
            return 'en'  # Fallback to English

    def _load_language_keywords(self):
        """Load importance keywords and name patterns from language file"""
        try:
            language = self._get_current_language()
            config_dir = Path.home() / '.aichat'
            lang_file = config_dir / 'lang' / f'{language}.conf'

            # Default English keywords (fallback)
            default_keywords = ['important', 'remember', 'save', 'note', 'TODO', 'bug', 'error', 'problem', 'urgent', 'FIXME', 'BUG', 'URGENT']
            default_patterns = ['name', 'Name', 'called', 'am', 'is']

            if not lang_file.exists():
                return default_keywords, default_patterns

            keywords = default_keywords.copy()
            patterns = default_patterns.copy()

            with open(lang_file, 'r', encoding='utf-8') as f:
                content = f.read()

                # Extract MEMORY_IMPORTANT_KEYWORDS
                keyword_match = re.search(r'MEMORY_IMPORTANT_KEYWORDS="([^"]+)"', content)
                if keyword_match:
                    lang_keywords = keyword_match.group(1).split(',')
                    keywords = [k.strip() for k in lang_keywords if k.strip()]

                # Extract MEMORY_NAME_PATTERNS
                pattern_match = re.search(r'MEMORY_NAME_PATTERNS="([^"]+)"', content)
                if pattern_match:
                    lang_patterns = pattern_match.group(1).split(',')
                    patterns = [p.strip() for p in lang_patterns if p.strip()]

            return keywords, patterns

        except Exception as e:
            print(f"Warning: Could not load language keywords: {e}", file=sys.stderr)
            # Return English defaults
            return ['important', 'remember', 'save', 'note', 'TODO', 'bug', 'error', 'problem', 'urgent'], ['name', 'Name', 'called', 'am', 'is']

    @property
    def model(self):
        """Lazy load the embedding model to save startup time"""
        if self._model is None:
            try:
                self._model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                print(f"Error loading embedding model: {e}")
                sys.exit(1)
        return self._model

    def _create_tables(self):
        """Create tables if they don't exist"""
        try:
            # Basic tables that always work
            self.db.executescript("""
                -- Chat history table (mirrors shell-gpt format)
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    role TEXT NOT NULL,  -- 'user' or 'assistant'
                    content TEXT NOT NULL,
                    metadata JSON DEFAULT '{}',
                    importance REAL DEFAULT 1.0
                );

                -- Memory summaries for long-term storage
                CREATE TABLE IF NOT EXISTS memory_summaries (
                    id INTEGER PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    start_time INTEGER NOT NULL,
                    end_time INTEGER NOT NULL,
                    message_count INTEGER NOT NULL,
                    created_at INTEGER NOT NULL
                );

                -- Indexes for performance
                CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_history(session_id);
                CREATE INDEX IF NOT EXISTS idx_chat_timestamp ON chat_history(timestamp);
                CREATE INDEX IF NOT EXISTS idx_memory_session ON memory_summaries(session_id);
            """)

            # Vector table only if extension is available
            if self.vector_support:
                self.db.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS chat_embeddings USING vec0(
                        message_embedding FLOAT[384],
                        session_id TEXT,
                        timestamp INTEGER,
                        message_type TEXT,
                        importance REAL DEFAULT 1.0
                    )
                """)

            self.db.commit()
        except Exception as e:
            print(f"Error creating tables: {e}")
            sys.exit(1)

    def add_message(self, session_id, role, content, metadata=None):
        """Add a message and generate its embedding"""
        if not content.strip():
            return  # Skip empty messages

        timestamp = int(time.time())

        try:
            # Calculate importance (simple heuristic)
            importance = self._calculate_importance(content, role)

            # Insert into chat history
            cursor = self.db.execute(
                "INSERT INTO chat_history (session_id, role, content, metadata, timestamp, importance) VALUES (?, ?, ?, ?, ?, ?)",
                (session_id, role, content, json.dumps(metadata or {}), timestamp, importance)
            )
            message_id = cursor.lastrowid

            # Only add embedding if vector support is available
            if self.vector_support:
                try:
                    # Generate embedding
                    embedding = self.model.encode([content])[0]
                    embedding_list = embedding.tolist()

                    # Insert embedding
                    self.db.execute(
                        "INSERT INTO chat_embeddings (rowid, message_embedding, session_id, timestamp, message_type, importance) VALUES (?, ?, ?, ?, ?, ?)",
                        (message_id, json.dumps(embedding_list), session_id, timestamp, role, importance)
                    )
                except Exception as embedding_error:
                    # If embedding fails, continue without it
                    print(f"Warning: Could not generate embedding: {embedding_error}", file=sys.stderr)

            self.db.commit()
            return message_id

        except Exception as e:
            print(f"Error adding message: {e}", file=sys.stderr)
            return None

    def _calculate_importance(self, content, role):
        """Calculate message importance (0.0 - 2.0)"""
        importance = 1.0

        # User questions are generally more important
        if role == 'user':
            importance += 0.2

        # Longer messages might be more important
        if len(content) > 100:
            importance += 0.2

        # Load keywords dynamically from language files
        important_keywords, _ = self._load_language_keywords()

        for keyword in important_keywords:
            if keyword.lower() in content.lower():
                importance += 0.3
                break

        return min(importance, 2.0)  # Cap at 2.0

    def search_similar(self, query, session_id=None, limit=5, min_importance=0.5):
        """Search for semantically similar messages"""
        if not self.vector_support:
            # Fallback to basic text search without vectors
            return self._basic_text_search(query, session_id, limit, min_importance)

        try:
            # Generate query embedding
            query_embedding = self.model.encode([query])[0]
            query_json = json.dumps(query_embedding.tolist())

            # Build SQL query
            sql = """
                SELECT
                    h.content,
                    h.role,
                    h.timestamp,
                    e.importance,
                    e.distance
                FROM chat_embeddings e
                JOIN chat_history h ON h.id = e.rowid
                WHERE e.message_embedding MATCH ?
                  AND e.importance >= ?
            """
            params = [query_json, min_importance]

            # Optional session filtering
            if session_id:
                sql += " AND e.session_id = ?"
                params.append(session_id)

            sql += " ORDER BY e.distance ASC LIMIT ?"
            params.append(limit)

            results = self.db.execute(sql, params).fetchall()
            return results

        except Exception as e:
            print(f"Error in vector search, falling back to text search: {e}", file=sys.stderr)
            return self._basic_text_search(query, session_id, limit, min_importance)

    def _basic_text_search(self, query, session_id=None, limit=5, min_importance=0.5):
        """Fallback text search when vector search is not available"""
        try:
            # Simple text search using SQLite FTS or LIKE
            sql = """
                SELECT
                    content,
                    role,
                    timestamp,
                    importance,
                    0 as distance
                FROM chat_history
                WHERE content LIKE ?
                  AND importance >= ?
            """
            params = [f"%{query}%", min_importance]

            if session_id:
                sql += " AND session_id = ?"
                params.append(session_id)

            sql += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            results = self.db.execute(sql, params).fetchall()
            return results

        except Exception as e:
            print(f"Error in text search: {e}", file=sys.stderr)
            return []

    def get_session_context(self, session_id, limit=10):
        """Get recent context for a session"""
        try:
            results = self.db.execute(
                "SELECT role, content, timestamp FROM chat_history WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
                (session_id, limit)
            ).fetchall()
            return list(reversed(results))  # Return in chronological order
        except Exception as e:
            print(f"Error getting session context: {e}", file=sys.stderr)
            return []

    def cleanup_old_data(self, force=False):
        """Smart cleanup: Keep important messages, limit by count/size"""
        try:
            stats = self.get_stats()

            # Check if cleanup needed
            needs_cleanup = (
                stats['total_messages'] >= 5000 or
                stats['db_size_mb'] >= 50 or
                force
            )

            if not needs_cleanup:
                return 0

            # Target: 90% of limits (4500 messages or 45MB)
            target_messages = 4500

            # Load protected patterns dynamically from language files
            important_keywords, name_patterns = self._load_language_keywords()

            # Build protected patterns from language file + universal patterns
            protected_patterns = []

            # Add name patterns with wildcards
            for pattern in name_patterns:
                protected_patterns.append(f'%{pattern}%')

            # Add important keywords as protected patterns
            for keyword in important_keywords:
                protected_patterns.append(f'%{keyword}%')

            # Add universal symbols
            protected_patterns.extend(['%!!!%', '%TODO%', '%FIXME%', '%BUG%'])

            # Build dynamic query with all protected patterns
            conditions = ["importance < 1.5"]
            for pattern in protected_patterns:
                conditions.append(f"content NOT LIKE '{pattern}'")

            where_clause = " AND ".join(conditions)

            deletable = self.db.execute(f"""
                SELECT id FROM chat_history
                WHERE {where_clause}
                ORDER BY importance ASC, timestamp ASC
            """).fetchall()

            # Calculate how many to delete
            current_count = stats['total_messages']
            to_delete_count = max(0, current_count - target_messages)
            to_delete_count = min(to_delete_count, len(deletable))

            if to_delete_count == 0:
                return 0

            # Delete oldest, least important messages
            delete_ids = [row[0] for row in deletable[:to_delete_count]]
            placeholders = ','.join(['?' for _ in delete_ids])

            # Delete from both tables if vector support available
            if self.vector_support:
                self.db.execute(f"DELETE FROM chat_embeddings WHERE rowid IN ({placeholders})", delete_ids)
            self.db.execute(f"DELETE FROM chat_history WHERE id IN ({placeholders})", delete_ids)

            self.db.commit()
            return len(delete_ids)

        except Exception as e:
            print(f"Error in smart cleanup: {e}", file=sys.stderr)
            return 0

    def get_stats(self):
        """Get database statistics"""
        try:
            stats = {}

            # Message count
            stats['total_messages'] = self.db.execute("SELECT COUNT(*) FROM chat_history").fetchone()[0]

            # Session count
            stats['total_sessions'] = self.db.execute("SELECT COUNT(DISTINCT session_id) FROM chat_history").fetchone()[0]

            # Database size
            stats['db_size_mb'] = os.path.getsize(self.db_path) / (1024 * 1024)

            # Date range
            date_range = self.db.execute(
                "SELECT MIN(timestamp), MAX(timestamp) FROM chat_history"
            ).fetchone()

            if date_range[0]:
                stats['oldest_message'] = time.strftime('%Y-%m-%d', time.localtime(date_range[0]))
                stats['newest_message'] = time.strftime('%Y-%m-%d', time.localtime(date_range[1]))

            return stats
        except Exception as e:
            print(f"Error getting stats: {e}", file=sys.stderr)
            return {}

    def close(self):
        """Close database connection"""
        if self.db:
            self.db.close()

def main():
    """Command line interface for testing"""
    if len(sys.argv) < 2:
        print("Usage: python3 memory_system.py <command> [args...]")
        print("Commands:")
        print("  stats              - Show database statistics")
        print("  search <query>     - Search for similar messages")
        print("  add <session> <role> <content> - Add a message")
        print("  cleanup [force]    - Smart cleanup (5000+ msgs or 50MB triggers)")
        return

    memory = ChatMemorySystem()
    command = sys.argv[1]

    try:
        if command == 'stats':
            stats = memory.get_stats()
            print(json.dumps(stats, indent=2))

        elif command == 'search' and len(sys.argv) >= 3:
            query = ' '.join(sys.argv[2:])
            results = memory.search_similar(query, limit=10)
            for content, role, timestamp, importance, distance in results:
                date_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(timestamp))
                print(f"[{date_str}] {role}: {content[:100]}... (importance: {importance:.1f}, distance: {distance:.3f})")

        elif command == 'add' and len(sys.argv) >= 5:
            session_id = sys.argv[2]
            role = sys.argv[3]
            content = ' '.join(sys.argv[4:])
            message_id = memory.add_message(session_id, role, content)
            print(f"Added message with ID: {message_id}")

        elif command == 'cleanup':
            force = len(sys.argv) >= 3 and sys.argv[2].lower() == 'force'
            deleted = memory.cleanup_old_data(force)
            if deleted > 0:
                print(f"Smart cleanup: Deleted {deleted} low-priority messages")
            else:
                print("No cleanup needed (under 5000 messages and 50MB)")

        else:
            print(f"Unknown command: {command}")

    finally:
        memory.close()

if __name__ == '__main__':
    main()