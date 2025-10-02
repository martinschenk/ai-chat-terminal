#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UPDATE Action Handler (NEW in v9.0.0)
Handles updating existing data in local database
"""

import sys

class UpdateHandler:
    """Handler for UPDATE database operations"""

    def __init__(self, memory_system, lang_manager):
        """
        Initialize UPDATE handler

        Args:
            memory_system: MemorySystem instance for DB operations
            lang_manager: LangManager instance for translations
        """
        self.memory = memory_system
        self.lang = lang_manager

    def handle(self, session_id: str, user_input: str, phi3_result: dict) -> tuple:
        """
        Handle UPDATE action

        Args:
            session_id: Current session ID
            user_input: Original user message
            phi3_result: Parsed Phi-3 result with update target and new value

        Returns:
            (response_message, metadata)
        """
        # Extract update information
        data = phi3_result.get('data', {})
        target = data.get('target', '')
        new_value = data.get('value', '')
        data_type = data.get('type', '')

        if not target or not new_value:
            # Insufficient information to update
            error_msg = self.lang.get('msg_update_insufficient_info')
            return error_msg, {
                "error": True,
                "model": "local-db-update",
                "action": "UPDATE_INSUFFICIENT_INFO"
            }

        # Find items to update
        results = self.memory.search(target, limit=1)

        if results:
            old_item = results[0]
            old_content = old_item.get('content', '')

            try:
                # Update the item
                # This assumes MemorySystem has an update method
                self.memory.update_message(old_item['id'], new_value, {
                    'privacy_category': 'LOCAL_STORAGE',
                    'data_type': data_type,
                    'updated_from': old_content
                })

                # Generate confirmation
                confirmation = self.lang.format('msg_update_confirmation',
                    target=target,
                    old_value=old_content[:50],
                    new_value=new_value[:50],
                    type=data_type if data_type else ''
                )

                # Print DB notification
                notification = self.lang.get('msg_update_notification')
                print(f"\n{notification}\n", file=sys.stderr)

                return confirmation, {
                    "error": False,
                    "model": "local-db-update",
                    "tokens": 0,
                    "source": "local",
                    "action": "UPDATE",
                    "updated_id": old_item['id']
                }

            except Exception as e:
                # Update failed
                error_msg = self.lang.format('msg_update_error', error=str(e))
                return error_msg, {
                    "error": True,
                    "model": "local-db-update",
                    "action": "UPDATE_FAILED"
                }
        else:
            # Nothing found to update
            no_results = self.lang.get('msg_no_results')
            return no_results, {
                "error": False,
                "model": "local-db-update",
                "tokens": 0,
                "source": "local",
                "action": "UPDATE_NOT_FOUND"
            }
