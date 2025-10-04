#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAVE Action Handler
Handles saving data to local database with Phi-3 extracted information
"""

import sys

class SaveHandler:
    """Handler for SAVE database operations"""

    def __init__(self, memory_system, lang_manager):
        """
        Initialize SAVE handler

        Args:
            memory_system: MemorySystem instance for DB operations
            lang_manager: LangManager instance for translations
        """
        self.memory = memory_system
        self.lang = lang_manager

    def handle(self, session_id: str, user_input: str, phi3_result: dict) -> tuple:
        """
        Handle SAVE action

        Args:
            session_id: Current session ID
            user_input: Original user message
            phi3_result: Parsed Phi-3 result with extracted data

        Returns:
            (response_message, metadata)
        """
        # Extract Phi-3 parsed data
        data = phi3_result.get('data', {})
        data_type = data.get('type', 'note')
        value = data.get('value', user_input)
        label = data.get('label', '')
        context = data.get('context', '')

        # Store private data using store_private_data method
        self.memory.store_private_data(
            content=value,
            data_type=data_type,
            full_message=user_input,
            metadata={
                'label': label,
                'context': context,
                'session_id': session_id
            }
        )

        # Also save to chat history
        self.memory.add_message(session_id, 'user', user_input, {
            'privacy_category': 'LOCAL_STORAGE',
            'data_type': data_type,
            'label': label
        })

        # Generate natural confirmation response
        try:
            from response_generator import ResponseGenerator
            gen = ResponseGenerator()
            confirmation = gen.format_stored_data(user_input, self.lang.language)
        except Exception as e:
            # Fallback if response generator fails
            confirmation = self.lang.format('msg_save_confirmation',
                label=label if label else data_type
            )

        # Save confirmation to DB
        self.memory.add_message(session_id, 'assistant', confirmation, {
            'privacy_category': 'LOCAL_STORAGE_CONFIRM'
        })

        # Phi-3 already includes icon & varied phrasing!

        return confirmation, {
            "error": False,
            "model": "local-storage",
            "tokens": 0,
            "source": "local",
            "action": "SAVE",
            "data_type": data_type
        }
