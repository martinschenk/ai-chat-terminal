#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RETRIEVE Action Handler
Handles retrieving data from local database
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
            phi3_result: Parsed Phi-3 result with query information

        Returns:
            (response_message, metadata)
        """
        # KISS: Extract type from user_input with keywords
        query_type = ''
        if 'email' in user_input.lower() or 'e-mail' in user_input.lower():
            query_type = 'email'
        elif 'phone' in user_input.lower() or 'telefon' in user_input.lower() or 'number' in user_input.lower():
            query_type = 'phone'
        elif 'address' in user_input.lower() or 'adresse' in user_input.lower():
            query_type = 'address'
        elif 'password' in user_input.lower() or 'passwort' in user_input.lower():
            query_type = 'password'

        # Search in database using search_private_data
        results = self.memory.search_private_data(user_input, limit=10, silent=True)

        # ALWAYS filter by type if we detected one!
        if query_type and results:
            filtered = [r for r in results
                       if r.get('metadata', {}).get('data_type', '').lower() == query_type.lower()]
            if filtered:
                results = filtered
            else:
                results = []  # No matches of this type!

        if results:
            # Format results naturally (Phi-3 handles icons & varied phrasing!)
            formatted_response = self._format_results(results, query_type, user_input)

            # Save to history
            self.memory.add_message(session_id, 'user', user_input, {
                'privacy_category': 'LOCAL_RETRIEVAL',
                'query_type': query_type,
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

    def _format_results(self, results: list, query_type: str, query: str) -> str:
        """
        Format search results - KISS: Just show the data with 🔍 icon

        Args:
            results: List of search results from database
            query_type: Type of data being queried
            query: Original query string

        Returns:
            Formatted response string
        """
        # KISS: Show first result with icon
        if results:
            content = results[0].get('content', '').strip()
            return f"🔍 {content}"

        return self.lang.get('msg_no_results', 'Not found')
