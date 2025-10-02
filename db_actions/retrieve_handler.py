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
        # Extract what user is looking for
        data = phi3_result.get('data', {})
        query_type = data.get('type', '')
        query = data.get('query', user_input)
        label = data.get('label', '')

        # Search in database using search_private_data
        results = self.memory.search_private_data(query, limit=5, silent=True)

        if results:
            # Format results naturally
            formatted_response = self._format_results(results, query_type, query)

            # Save to history
            self.memory.add_message(session_id, 'user', user_input, {
                'privacy_category': 'LOCAL_RETRIEVAL',
                'query_type': query_type,
                'query': query
            })

            self.memory.add_message(session_id, 'assistant', formatted_response, {
                'privacy_category': 'LOCAL_RESULT'
            })

            # Print DB notification
            notification = self.lang.get('msg_retrieve_notification')
            print(f"\n{notification}\n", file=sys.stderr)

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
        Format search results naturally

        Args:
            results: List of search results from database
            query_type: Type of data being queried
            query: Original query string

        Returns:
            Formatted response string
        """
        try:
            # Try to use response_generator for natural formatting
            from response_generator import ResponseGenerator
            gen = ResponseGenerator()
            return gen.format_retrieved_data(user_input=query, results=results, language=self.lang.language)
        except Exception:
            # Fallback to simple formatting
            if len(results) == 1:
                return results[0]['content']
            else:
                # Multiple results - show all unique values
                unique_contents = []
                seen = set()
                for r in results:
                    content = r.get('content', '').strip()
                    if content and content not in seen:
                        unique_contents.append(content)
                        seen.add(content)

                if len(unique_contents) == 1:
                    return unique_contents[0]
                else:
                    # Show all unique results
                    formatted = '\n'.join(f"• {c}" for c in unique_contents)
                    count = len(unique_contents)
                    return f"{formatted}\n\n({count} {self.lang.get('msg_results_found')})"
