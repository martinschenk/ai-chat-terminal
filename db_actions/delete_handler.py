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
        # KISS: Extract type from user_input (same as retrieve!)
        query_type = ''
        if 'email' in user_input.lower() or 'e-mail' in user_input.lower():
            query_type = 'email'
        elif 'phone' in user_input.lower() or 'telefon' in user_input.lower() or 'number' in user_input.lower():
            query_type = 'phone'
        elif 'address' in user_input.lower() or 'adresse' in user_input.lower():
            query_type = 'address'
        elif 'password' in user_input.lower() or 'passwort' in user_input.lower():
            query_type = 'password'

        # Search for items to delete
        results = self.memory.search_private_data(user_input, limit=10, silent=True)

        # ALWAYS filter by type if we detected one!
        if query_type and results:
            filtered = [r for r in results
                       if r.get('metadata', {}).get('data_type', '').lower() == query_type.lower()]
            if filtered:
                results = filtered
            else:
                results = []

        # Delete found items (with confirmation showing ALL items!)
        if results:
            # Show what will be deleted - FULL LIST (up to 20 items)
            print(f"\n⚠️  Found {len(results)} item(s) to delete:", file=sys.stderr)

            for i, r in enumerate(results, 1):
                if i > 20:
                    print(f"  ... and {len(results) - 20} more items", file=sys.stderr)
                    break

                # Show full content (up to 70 chars)
                content_preview = r['content'][:70]
                if len(r['content']) > 70:
                    content_preview += "..."

                print(f"  {i}. {content_preview}", file=sys.stderr)

            # Get confirmation message from lang file
            confirm_prompt = self.lang.get(
                'msg_delete_confirm_prompt',
                f"\n🗑️  Delete {len(results)} item(s) from local DB? (y/N): "
            )

            # Ask for confirmation
            print(confirm_prompt, end='', file=sys.stderr, flush=True)

            try:
                # Read from stdin
                confirm = input().strip().lower()

                if confirm in ['y', 'yes', 'j', 'ja', 's', 'si', 'sí']:
                    deleted_ids = [r['id'] for r in results]
                    deleted_count = self.memory.delete_by_ids(deleted_ids)
                else:
                    # User cancelled
                    cancel_msg = self.lang.get('msg_delete_cancelled', '❌ Delete cancelled')
                    return cancel_msg, {
                        "error": False,
                        "model": "local-db-delete",
                        "tokens": 0,
                        "source": "local",
                        "action": "DELETE_CANCELLED"
                    }
            except (EOFError, KeyboardInterrupt):
                # Non-interactive mode or Ctrl+C
                cancel_msg = self.lang.get('msg_delete_cancelled', '❌ Delete cancelled')
                return cancel_msg, {
                    "error": False,
                    "model": "local-db-delete",
                    "tokens": 0,
                    "source": "local",
                    "action": "DELETE_CANCELLED"
                }
        else:
            deleted_count = 0

        if deleted_count > 0:
            # KISS: Simple confirmation from lang file
            confirmation = self.lang.get('msg_deleted', f'🗑️ Deleted ({deleted_count})')

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
