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
        data_type = data.get('type', '')

        # Search for matching items
        results = self.memory.search(target, limit=10)

        if results:
            # Delete found items
            deleted_ids = []
            for result in results:
                try:
                    self.memory.delete_message(result['id'])
                    deleted_ids.append(result['id'])
                except Exception as e:
                    print(f"⚠️  Failed to delete {result['id']}: {e}", file=sys.stderr)

            if deleted_ids:
                # Generate confirmation
                confirmation = self.lang.format('msg_delete_confirmation',
                    count=len(deleted_ids),
                    target=target,
                    type=data_type if data_type else ''
                )

                # Print DB notification
                notification = self.lang.get('msg_delete_notification')
                print(f"\n{notification}\n", file=sys.stderr)

                return confirmation, {
                    "error": False,
                    "model": "local-db-delete",
                    "tokens": 0,
                    "source": "local",
                    "action": "DELETE",
                    "deleted_count": len(deleted_ids)
                }
            else:
                # Failed to delete
                error_msg = self.lang.get('msg_delete_error')
                return error_msg, {
                    "error": True,
                    "model": "local-db-delete",
                    "action": "DELETE_FAILED"
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
