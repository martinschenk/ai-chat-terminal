#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DELETE Action Handler (NEW in v9.0.0)
Handles deleting data from local database
"""

import sys

class DeleteHandler:
    """Handler for DELETE database operations"""

    def __init__(self, memory_system, lang_manager):
        """
        Initialize DELETE handler

        Args:
            memory_system: MemorySystem instance for DB operations
            lang_manager: LangManager instance for translations
        """
        self.memory = memory_system
        self.lang = lang_manager

    def handle(self, session_id: str, user_input: str, phi3_result: dict) -> tuple:
        """
        Handle DELETE action

        Args:
            session_id: Current session ID
            user_input: Original user message
            phi3_result: Parsed Phi-3 result with delete target

        Returns:
            (response_message, metadata)
        """
        # Extract what to delete
        data = phi3_result.get('data', {})
        target = data.get('target', user_input)

        # Delete matching items - returns actual count deleted!
        deleted_count = self.memory.delete_private_data(target)

        if deleted_count > 0:
            # Generate natural confirmation with Phi-3
            try:
                from response_generator import ResponseGenerator
                gen = ResponseGenerator()
                confirmation = gen.format_deleted_data(target, deleted_count, self.lang.language)
            except Exception as e:
                # Fallback if Phi-3 fails
                confirmation = self.lang.format('msg_delete_confirmation',
                    count=deleted_count,
                    target=target,
                    type=''
                )

            # Phi-3 already includes icon & varied phrasing!

            return confirmation, {
                "error": False,
                "model": "local-db-delete",
                "tokens": 0,
                "source": "local",
                "action": "DELETE",
                "deleted_count": deleted_count
            }
        else:
            # Nothing found to delete
            no_results = self.lang.get('msg_no_results')
            return no_results, {
                "error": False,
                "model": "local-db-delete",
                "tokens": 0,
                "source": "local",
                "action": "DELETE_NOT_FOUND"
            }
