#!/usr/bin/env python3
"""
AI Chat Terminal - Memory System
SQLite-based semantic memory with vector embeddings
"""

import os
import sys
import warnings

# Suppress all warnings BEFORE any other imports
warnings.filterwarnings("ignore")
os.environ['PYTHONWARNINGS'] = 'ignore'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'  # Suppress tokenizers fork warning

import json
import time
import re
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

try:
    from sentence_transformers import SentenceTransformer
    import sqlite_vec
except ImportError as e:
    print(f"Error: Missing required packages. Please install with:")
    print(f"pip3 install sentence-transformers sqlite-vec apsw")
    sys.exit(1)

# Global flag to show vector warning only once per session
_VECTOR_WARNING_SHOWN = False

class ChatMemorySystem:
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
            self.db.execute("PRAGMA kdf_iter = 64000")  # Optimized (was 256000)
            self.db.execute("PRAGMA cipher_hmac_algorithm = HMAC_SHA512")
            self.db.execute("PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA512")
        elif USE_APSW:
            # Use APSW (no encryption)
            self.db = apsw.Connection(str(db_path))
        else:
            # Use sqlite3 (no encryption)
            self.db = sqlite3.connect(str(db_path))

        # Check for vector extension support
        global _VECTOR_WARNING_SHOWN
        self.vector_support = False
        try:
            self.db.enable_load_extension(True)
            # Load sqlite-vec extension
            sqlite_vec.load(self.db)
            self.vector_support = True
            # Don't show success message - only show if vector search FAILS
            _VECTOR_WARNING_SHOWN = True
        except AttributeError as e:
            # Python's SQLite was compiled without extension support
            if not _VECTOR_WARNING_SHOWN:
                print("\n" + "="*70, file=sys.stderr)
                print("❌ CRITICAL ERROR: Vector search NOT available!", file=sys.stderr)
                print("="*70, file=sys.stderr)
                print(f"Reason: Python's SQLite compiled WITHOUT extension support", file=sys.stderr)
                print(f"\nSOLUTION: Install APSW with extension support:", file=sys.stderr)
                print(f"  pip3 install apsw", file=sys.stderr)
                print(f"\nVector search is REQUIRED - cannot continue without it!", file=sys.stderr)
                print("="*70 + "\n", file=sys.stderr)
                sys.exit(1)  # HARD FAIL - no fallback!
        except Exception as e:
            # sqlite-vec not available or other error
            if not _VECTOR_WARNING_SHOWN:
                print("\n" + "="*70, file=sys.stderr)
                print("❌ CRITICAL ERROR: Vector search NOT available!", file=sys.stderr)
                print("="*70, file=sys.stderr)
                print(f"Reason: {e}", file=sys.stderr)
                print(f"\nSOLUTION: Install required packages:", file=sys.stderr)
                print(f"  pip3 install apsw sqlite-vec", file=sys.stderr)
                print(f"\nVector search is REQUIRED - cannot continue without it!", file=sys.stderr)
                print("="*70 + "\n", file=sys.stderr)
                sys.exit(1)  # HARD FAIL - no fallback!

        # Initialize embedding model (lazy loading)
        self._model = None

        # Create compatibility wrapper for APSW
        if USE_APSW:
            self._setup_apsw_compatibility()

        self._create_tables()

    def _setup_apsw_compatibility(self):
        """Make APSW behave like sqlite3 for common operations"""
        # APSW doesn't have execute() on connection, add wrapper
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
                # APSW uses last_insert_rowid() on connection
                return self._conn.last_insert_rowid()

            def __getattr__(self, name):
                # Delegate other attributes to wrapped cursor
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
                # APSW doesn't have executescript, execute statements one by one
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

            def enable_load_extension(self, enabled):
                return self._conn.enable_load_extension(enabled)

        self.db = APSWWrapper(original_db)

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

    def _detect_message_language(self, content):
        """Detect language of a message by checking against keywords from all language files"""
        try:
            config_dir = Path.home() / '.aichat'
            lang_dir = config_dir / 'lang'

            if not lang_dir.exists():
                return self._get_current_language()

            # Language scoring - count keyword matches per language
            language_scores = {}

            for lang_file in lang_dir.glob('*.conf'):
                lang_code = lang_file.stem
                # Skip dialect files for detection (use base languages only)
                if '-' in lang_code:
                    continue

                try:
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        file_content = f.read()

                    # Get keywords and patterns for this language
                    keywords = []
                    patterns = []

                    keyword_match = re.search(r'MEMORY_IMPORTANT_KEYWORDS="([^"]+)"', file_content)
                    if keyword_match:
                        keywords = [k.strip() for k in keyword_match.group(1).split(',') if k.strip()]

                    pattern_match = re.search(r'MEMORY_NAME_PATTERNS="([^"]+)"', file_content)
                    if pattern_match:
                        patterns = [p.strip() for p in pattern_match.group(1).split(',') if p.strip()]

                    # Count matches in the content
                    score = 0
                    content_lower = content.lower()

                    for keyword in keywords + patterns:
                        if keyword.lower() in content_lower:
                            score += 1

                    if score > 0:
                        language_scores[lang_code] = score

                except Exception:
                    # Skip this language file if error
                    continue

            # Return language with highest score, or current UI language if no matches
            if language_scores:
                return max(language_scores, key=language_scores.get)
            else:
                return self._get_current_language()

        except Exception:
            return self._get_current_language()

    def _load_all_language_keywords(self):
        """Load importance keywords and name patterns from ALL language files"""
        try:
            config_dir = Path.home() / '.aichat'
            lang_dir = config_dir / 'lang'

            # Default English keywords (fallback)
            all_keywords = set(['important', 'remember', 'save', 'note', 'TODO', 'bug', 'error', 'problem', 'urgent', 'FIXME', 'BUG', 'URGENT'])
            all_patterns = set(['name', 'Name', 'called', 'am', 'is'])

            if not lang_dir.exists():
                return list(all_keywords), list(all_patterns)

            # Load keywords from all language files
            for lang_file in lang_dir.glob('*.conf'):
                try:
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Extract MEMORY_IMPORTANT_KEYWORDS
                    keyword_match = re.search(r'MEMORY_IMPORTANT_KEYWORDS="([^"]+)"', content)
                    if keyword_match:
                        lang_keywords = keyword_match.group(1).split(',')
                        all_keywords.update([k.strip() for k in lang_keywords if k.strip()])

                    # Extract MEMORY_NAME_PATTERNS
                    pattern_match = re.search(r'MEMORY_NAME_PATTERNS="([^"]+)"', content)
                    if pattern_match:
                        lang_patterns = pattern_match.group(1).split(',')
                        all_patterns.update([p.strip() for p in lang_patterns if p.strip()])

                except Exception:
                    # Skip this language file if error
                    continue

            return list(all_keywords), list(all_patterns)

        except Exception as e:
            print(f"Warning: Could not load language keywords: {e}", file=sys.stderr)
            # Return English defaults
            return ['important', 'remember', 'save', 'note', 'TODO', 'bug', 'error', 'problem', 'urgent'], ['name', 'Name', 'called', 'am', 'is']

    def _load_language_keywords(self):
        """Load importance keywords and name patterns from current language file (legacy method)"""
        # For backwards compatibility, now calls the new method
        return self._load_all_language_keywords()

    @property
    def model(self):
        """Lazy load the embedding model to save startup time"""
        if self._model is None:
            try:
                # Upgrade to e5-base for better cross-language performance
                self._model = SentenceTransformer('intfloat/multilingual-e5-base')
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
                    importance REAL DEFAULT 1.0,
                    language TEXT DEFAULT 'en'
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
                        message_embedding FLOAT[768]
                    )
                """)


            # Add language column to existing databases (migration)
            try:
                self.db.execute("ALTER TABLE chat_history ADD COLUMN language TEXT DEFAULT 'en'")
            except Exception:
                # Column already exists, ignore
                pass

            # Add created_at and updated_at columns (migration)
            try:
                self.db.execute("ALTER TABLE chat_history ADD COLUMN created_at INTEGER DEFAULT (strftime('%s','now'))")
            except Exception:
                # Column already exists, ignore
                pass

            try:
                self.db.execute("ALTER TABLE chat_history ADD COLUMN updated_at INTEGER DEFAULT (strftime('%s','now'))")
            except Exception:
                # Column already exists, ignore
                pass

            # Vector table doesn't need migrations - it's just embeddings

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
            # Detect language for this message
            detected_language = self._detect_message_language(content)

            # Calculate importance (simple heuristic)
            importance = self._calculate_importance(content, role)

            # Insert into chat history
            cursor = self.db.execute(
                "INSERT INTO chat_history (session_id, role, content, metadata, timestamp, importance, language, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (session_id, role, content, json.dumps(metadata or {}), timestamp, importance, detected_language, timestamp, timestamp)
            )
            message_id = cursor.lastrowid

            # Only add embedding if vector support is available
            if self.vector_support:
                try:
                    # Add "passage:" prefix for E5 model (messages are stored content)
                    prefixed_content = f"passage: {content}"

                    # Generate embedding
                    embedding = self.model.encode([prefixed_content], convert_to_numpy=True)[0]

                    # Insert embedding with explicit rowid to match chat_history.id
                    # sqlite-vec expects embeddings as bytes (numpy array converted)
                    self.db.execute(
                        "INSERT INTO chat_embeddings (rowid, message_embedding) VALUES (?, ?)",
                        (message_id, embedding.astype('float32').tobytes())
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
            # Add "query:" prefix for E5 model
            prefixed_query = f"query: {query}"

            # Generate query embedding
            query_embedding = self.model.encode([prefixed_query])[0]
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

    def encode_for_search(self, text: str):
        """Encode text for searching (with 'query:' prefix for E5 optimization)"""
        return self.model.encode(f"query: {text}", convert_to_tensor=False)

    def encode_for_storage(self, text: str):
        """Encode text for storage (with 'passage:' prefix for E5 optimization)"""
        return self.model.encode(f"passage: {text}", convert_to_tensor=False)

    def search_private_data(self, query: str, limit: int = 5, silent: bool = False):
        """Search for private data in chat_history by metadata"""
        try:
            # Search for messages with SENSITIVE, PROPRIETARY, or PERSONAL categories
            cursor = self.db.cursor()

            # Use semantic search if vector support is available
            if self.vector_support:
                query_embedding = self.encode_for_search(query)

                # Define truly sensitive categories (matches pii_detector.py whitelist)
                TRULY_SENSITIVE = [
                    'CREDIT_CARD', 'IBAN_CODE', 'CRYPTO',
                    'PASSWORD', 'API_KEY', 'JWT_TOKEN',
                    'US_SSN', 'UK_NHS', 'US_PASSPORT', 'US_DRIVER_LICENSE',
                    'MEDICAL_LICENSE', 'NIF', 'DNI',
                    'PHONE_NUMBER', 'EMAIL_ADDRESS',
                    'IP_ADDRESS',
                    'OPENAI_API_KEY', 'OPENAI_PROJECT_KEY',
                    'AWS_ACCESS_KEY', 'AWS_SECRET_KEY',
                    'GITHUB_TOKEN', 'GITHUB_CLASSIC_TOKEN',
                    'GOOGLE_API_KEY', 'SLACK_TOKEN', 'STRIPE_KEY',
                    'TELEGRAM_BOT_TOKEN', 'PRIVATE_KEY', 'DB_CONNECTION',
                    'GENERIC_API_KEY',
                ]

                # Build SQL IN clause for truly sensitive categories
                placeholders = ','.join('?' * len(TRULY_SENSITIVE))

                # Search ONLY truly sensitive data (not LOCATION, PERSON, etc.)
                # Note: sqlite-vec uses vec_distance_L2, not vec_distance
                query_bytes = query_embedding.astype('float32').tobytes()

                # Use subquery to filter by distance (can't use alias in WHERE)
                # Sort by created_at DESC first (newest first), then by distance (most similar)
                cursor.execute(f"""
                    SELECT content, metadata, created_at, distance
                    FROM (
                        SELECT h.content, h.metadata, h.created_at,
                               vec_distance_L2(e.message_embedding, ?) as distance
                        FROM chat_history h
                        JOIN chat_embeddings e ON h.id = e.rowid
                        WHERE json_extract(h.metadata, '$.privacy_category') IN ({placeholders})
                    )
                    WHERE distance < 0.7
                    ORDER BY created_at DESC, distance ASC
                    LIMIT ?
                """, (query_bytes, *TRULY_SENSITIVE, limit))
            else:
                # Define truly sensitive categories (matches pii_detector.py whitelist)
                TRULY_SENSITIVE = [
                    'CREDIT_CARD', 'IBAN_CODE', 'CRYPTO',
                    'PASSWORD', 'API_KEY', 'JWT_TOKEN',
                    'US_SSN', 'UK_NHS', 'US_PASSPORT', 'US_DRIVER_LICENSE',
                    'MEDICAL_LICENSE', 'NIF', 'DNI',
                    'PHONE_NUMBER', 'EMAIL_ADDRESS',
                    'IP_ADDRESS',
                    'OPENAI_API_KEY', 'OPENAI_PROJECT_KEY',
                    'AWS_ACCESS_KEY', 'AWS_SECRET_KEY',
                    'GITHUB_TOKEN', 'GITHUB_CLASSIC_TOKEN',
                    'GOOGLE_API_KEY', 'SLACK_TOKEN', 'STRIPE_KEY',
                    'TELEGRAM_BOT_TOKEN', 'PRIVATE_KEY', 'DB_CONNECTION',
                    'GENERIC_API_KEY',
                ]

                # Keyword-based search: map query keywords to PII types
                keyword_to_pii = {
                    # Email
                    'email': 'EMAIL_ADDRESS', 'e-mail': 'EMAIL_ADDRESS', 'mail': 'EMAIL_ADDRESS',
                    # Phone
                    'phone': 'PHONE_NUMBER', 'telefon': 'PHONE_NUMBER', 'handy': 'PHONE_NUMBER',
                    'mobile': 'PHONE_NUMBER', 'number': 'PHONE_NUMBER',
                    # Password
                    'password': 'PASSWORD', 'passwort': 'PASSWORD', 'pass': 'PASSWORD',
                    'kennwort': 'PASSWORD', 'contraseña': 'PASSWORD',
                    # API Keys
                    'api': 'API_KEY', 'key': 'API_KEY', 'token': 'JWT_TOKEN',
                    'schlüssel': 'API_KEY', 'openai': 'OPENAI_API_KEY',
                    # Credit Card
                    'credit': 'CREDIT_CARD', 'card': 'CREDIT_CARD', 'karte': 'CREDIT_CARD',
                    'kreditkarte': 'CREDIT_CARD', 'tarjeta': 'CREDIT_CARD',
                    # Identity
                    'ssn': 'US_SSN', 'dni': 'DNI', 'nif': 'NIF', 'passport': 'US_PASSPORT',
                    'ausweis': 'US_PASSPORT', 'pasaporte': 'US_PASSPORT',
                    # Other
                    'ip': 'IP_ADDRESS', 'address': 'IP_ADDRESS', 'adresse': 'IP_ADDRESS',
                    'koffer': 'PASSWORD',  # "koffercode" -> treat as password
                    'code': 'PASSWORD',
                }

                # Extract keywords from query (lowercase)
                query_lower = query.lower()
                detected_types = set()
                for keyword, pii_type in keyword_to_pii.items():
                    if keyword in query_lower and pii_type in TRULY_SENSITIVE:
                        detected_types.add(pii_type)

                # If we detected types, search by category
                if detected_types:
                    category_placeholders = ','.join('?' * len(detected_types))
                    cursor.execute(f"""
                        SELECT content, metadata, created_at
                        FROM chat_history
                        WHERE json_extract(metadata, '$.privacy_category') IN ({category_placeholders})
                        ORDER BY created_at DESC
                        LIMIT ?
                    """, (*detected_types, limit))
                else:
                    # No keywords detected - search all sensitive data with content match
                    placeholders = ','.join('?' * len(TRULY_SENSITIVE))
                    cursor.execute(f"""
                        SELECT content, metadata, created_at
                        FROM chat_history
                        WHERE json_extract(metadata, '$.privacy_category') IN ({placeholders})
                          AND content LIKE ?
                        ORDER BY created_at DESC
                        LIMIT ?
                    """, (*TRULY_SENSITIVE, f"%{query}%", limit))

            results = []
            for row in cursor.fetchall():
                metadata = json.loads(row[1]) if row[1] else {}
                results.append({
                    'content': row[0],
                    'data_type': metadata.get('privacy_category', 'UNKNOWN'),
                    'metadata': metadata,
                    'created_at': row[2],
                    'similarity': 1 - row[3] if len(row) > 3 else 1.0
                })

            return results

        except Exception as e:
            print(f"Error searching private data: {e}", file=sys.stderr)
            return []

    def store_private_data(self, content: str, data_type: str, full_message: str, metadata: dict = None):
        """Store private data in chat_history with privacy metadata"""
        try:
            if metadata is None:
                metadata = {}

            # Map Phi-3 data types to PII categories that search_private_data expects
            TYPE_TO_PII_CATEGORY = {
                'email': 'EMAIL_ADDRESS',
                'phone': 'PHONE_NUMBER',
                'phone_number': 'PHONE_NUMBER',
                'password': 'PASSWORD',
                'api_key': 'API_KEY',
                'credit_card': 'CREDIT_CARD',
                'ssn': 'US_SSN',
                'passport': 'US_PASSPORT',
                'nif': 'NIF',
                'dni': 'DNI',
                'ip_address': 'IP_ADDRESS',
                'note': 'GENERIC_API_KEY',  # Generic fallback for notes
            }

            # Convert to PII category for compatibility with search_private_data
            pii_category = TYPE_TO_PII_CATEGORY.get(data_type.lower(), 'GENERIC_API_KEY')

            # Set privacy category in metadata
            metadata['privacy_category'] = pii_category
            metadata['data_type'] = data_type  # Keep original for display
            metadata['is_private'] = True

            # Store in chat_history
            timestamp = int(time.time())
            cursor = self.db.cursor()

            cursor.execute("""
                INSERT INTO chat_history (session_id, timestamp, role, content, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                'private_data',  # Special session for private data
                timestamp,
                'user',
                content,
                json.dumps(metadata),
                timestamp,
                timestamp
            ))

            message_id = cursor.lastrowid

            # Store embedding if vector support is available
            if self.vector_support:
                embedding = self.encode_for_storage(full_message)
                # sqlite-vec expects embeddings as bytes (numpy array converted)
                cursor.execute("""
                    INSERT INTO chat_embeddings (rowid, message_embedding)
                    VALUES (?, ?)
                """, (message_id, embedding.astype('float32').tobytes()))

            self.db.commit()
            return message_id

        except Exception as e:
            print(f"Error storing private data: {e}", file=sys.stderr)
            return None

    def delete_private_data(self, pattern: str):
        """Delete private data matching pattern"""
        try:
            cursor = self.db.cursor()

            # Find matching private data - use actual privacy categories
            # EMAIL_ADDRESS, PHONE_NUMBER, etc. instead of SENSITIVE/PROPRIETARY/PERSONAL
            cursor.execute("""
                SELECT id FROM chat_history
                WHERE json_extract(metadata, '$.is_private') = 1
                  AND content LIKE ?
            """, (f"%{pattern}%",))

            ids = [row[0] for row in cursor.fetchall()]

            if ids:
                # Delete from both tables
                placeholders = ','.join('?' * len(ids))
                cursor.execute(f"DELETE FROM chat_history WHERE id IN ({placeholders})", ids)

                if self.vector_support:
                    cursor.execute(f"DELETE FROM chat_embeddings WHERE rowid IN ({placeholders})", ids)

                self.db.commit()

            return len(ids)

        except Exception as e:
            print(f"Error deleting private data: {e}", file=sys.stderr)
            return 0

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
        print("  search <query>     - Search for similar messages")
        print("  add <session> <role> <content> - Add a message")
        print("  cleanup [force]    - Smart cleanup (5000+ msgs or 50MB triggers)")
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