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
        data = phi3_result.get('data', {})
        filter_type = data.get('filter', None)

        # Get all stored data (LOCAL_STORAGE entries)
        all_data = self._get_all_local_storage()

        if all_data:
            # Format as list
            header = self.lang.get('msg_list_header')
            formatted_items = []

            for i, item in enumerate(all_data, 1):
                content = item.get('content', '')
                metadata = item.get('metadata') or {}  # Handle None case
                data_type = metadata.get('data_type', 'note')

                # Format each item
                formatted_items.append(f"  {i}. [{data_type}] {content[:80]}...")

            response = f"{header}\n" + "\n".join(formatted_items)
            try:
                response += f"\n\n{self.lang.format('msg_list_total', count=len(all_data))}"
            except:
                response += f"\n\nTotal: {len(all_data)} items"

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
            # Query database for all LOCAL_STORAGE messages
            # This assumes MemorySystem has a method to filter by metadata
            return self.memory.get_by_category('LOCAL_STORAGE', limit=100)
        except AttributeError:
            # Fallback: search with empty query to get recent items
            all_messages = self.memory.search('', limit=100)
            # Filter for LOCAL_STORAGE
            return [msg for msg in all_messages
                    if msg.get('metadata', {}).get('privacy_category') == 'LOCAL_STORAGE']
