#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIST Action Handler (NEW in v9.0.0)
Handles listing all stored data from local database
"""

import sys

class ListHandler:
    """Handler for LIST database operations"""

    def __init__(self, memory_system, lang_manager):
        """
        Initialize LIST handler

        Args:
            memory_system: MemorySystem instance for DB operations
            lang_manager: LangManager instance for translations
        """
        self.memory = memory_system
        self.lang = lang_manager

    def handle(self, session_id: str, user_input: str, phi3_result: dict) -> tuple:
        """
        Handle LIST action - show all stored data

        Args:
            session_id: Current session ID
            user_input: Original user message
            phi3_result: Parsed Phi-3 result (filter info if any)

        Returns:
            (response_message, metadata)
        """
        # Extract any filters from Phi-3
        data = phi3_result.get('data') or {}
        filter_type = data.get('filter', None)

        # Get all stored data (LOCAL_STORAGE entries)
        all_data = self._get_all_local_storage()

        if all_data:
            # Simple header - NO Phi-3 to avoid hallucinations!
            count = len(all_data)
            lang = self.lang.language.split('-')[0] if '-' in self.lang.language else self.lang.language

            if lang == 'de':
                header = f"📦 Deine Daten ({count}):"
            elif lang == 'es':
                header = f"📦 Tus datos ({count}):"
            else:
                header = f"📦 Your data ({count}):"

            formatted_items = []

            for i, item in enumerate(all_data, 1):
                content = item.get('content', '')
                metadata = item.get('metadata') or {}  # Handle None case
                data_type = metadata.get('data_type', 'note')

                # Format each item
                formatted_items.append(f"  {i}. [{data_type}] {content[:80]}...")

            response = f"{header}\n" + "\n".join(formatted_items)

            return response, {
                "error": False,
                "model": "local-db-list",
                "tokens": 0,
                "source": "local",
                "action": "LIST",
                "items_count": len(all_data)
            }
        else:
            # No data stored
            empty_msg = self.lang.get('msg_list_empty')
            return empty_msg, {
                "error": False,
                "model": "local-db-list",
                "tokens": 0,
                "source": "local",
                "action": "LIST_EMPTY"
            }

    def _get_all_local_storage(self) -> list:
        """
        Get all LOCAL_STORAGE entries from database

        Returns:
            List of messages with LOCAL_STORAGE category
        """
        try:
            # Use direct DB query to get ALL private data entries
            cursor = self.memory.db.cursor()

            # Get all messages from 'private_data' session
            cursor.execute("""
                SELECT content, metadata, created_at
                FROM chat_history
                WHERE session_id = 'private_data'
                ORDER BY created_at DESC
                LIMIT 100
            """)

            results = []
            for row in cursor.fetchall():
                import json
                metadata = json.loads(row[1]) if row[1] else {}
                results.append({
                    'content': row[0],
                    'metadata': metadata,
                    'created_at': row[2]
                })

            return results
        except Exception as e:
            print(f"⚠️  Error getting local storage: {e}", file=sys.stderr)
            return []
