#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RETRIEVE Action Handler
Handles retrieving data from local database

⚠️ ARCHITECTURE NOTE:
   This handler receives pre-classified actions from Llama 3.2.

   NO string matching for types (email/phone/etc) allowed here!
   - Llama already classified the action (RETRIEVE)
   - Llama already extracted the query
   - Llama already detected false positives

   String matching ONLY happens in:
   - local_storage_detector.py (initial keyword trigger from lang/*.conf)

   We return ALL search results - NO type filtering!
   Llama's query is already precise enough.
"""

import sys

class RetrieveHandler:
    """Handler for RETRIEVE database operations"""

    def __init__(self, memory_system, lang_manager):
        """
        Initialize RETRIEVE handler

        Args:
            memory_system: MemorySystem instance for DB operations
            lang_manager: LangManager instance for translations
        """
        self.memory = memory_system
        self.lang = lang_manager

    def handle(self, session_id: str, user_input: str, phi3_result: dict) -> tuple:
        """
        Handle RETRIEVE action

        Args:
            session_id: Current session ID
            user_input: Original user message
            phi3_result: Parsed Llama result with query information

        Returns:
            (response_message, metadata)
        """
        # Search in database using search_private_data
        # NO type filtering - Llama's query is already precise!
        # NO limit - return ALL matching results (RETRIEVE now handles both single items and "show everything")
        results = self.memory.search_private_data(user_input, silent=True)

        if results:
            # Format results naturally
            formatted_response = self._format_results(results, user_input)

            # Save to history
            self.memory.add_message(session_id, 'user', user_input, {
                'privacy_category': 'LOCAL_RETRIEVAL',
                'query': user_input
            })

            self.memory.add_message(session_id, 'assistant', formatted_response, {
                'privacy_category': 'LOCAL_RESULT'
            })

            return formatted_response, {
                "error": False,
                "model": "local-db-retrieval",
                "tokens": 0,
                "source": "local",
                "action": "RETRIEVE",
                "results_count": len(results)
            }
        else:
            # No results found
            no_results_msg = self.lang.get('msg_no_results')

            return no_results_msg, {
                "error": False,
                "model": "local-db-retrieval",
                "tokens": 0,
                "source": "local",
                "action": "RETRIEVE_EMPTY"
            }

    def _format_results(self, results: list, query: str) -> str:
        """
        Format search results - KISS: Show data with 🔍 icon

        Handles both single item queries and "show everything" queries

        Args:
            results: List of search results from database
            query: Original query string

        Returns:
            Formatted response string
        """
        if not results:
            return self.lang.get('msg_no_results', 'Not found')

        # Single result: show inline with icon
        if len(results) == 1:
            content = results[0].get('content', '').strip()
            return f"🔍 {content}"

        # Multiple results: show as numbered list
        output = f"🔍 Found {len(results)} items:\n"
        for i, result in enumerate(results, 1):
            content = result.get('content', '').strip()
            # Truncate long items in list view
            if len(content) > 70:
                content = content[:70] + "..."
            output += f"  {i}. {content}\n"

        return output.rstrip()
