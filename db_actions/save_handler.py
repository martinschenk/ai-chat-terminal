#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAVE Action Handler
Handles saving data to local database

⚠️ ARCHITECTURE NOTE:
   This handler receives pre-classified actions from Llama 3.2.

   NO string matching for types (email/phone/etc) allowed here!
   - Llama already classified the action (SAVE)
   - Llama already extracted the data
   - Llama already detected false positives

   String matching ONLY happens in:
   - local_storage_detector.py (initial keyword trigger from lang/*.conf)

   We only detect type from CONTENT pattern (@ = email, digits = phone),
   NOT from keywords like "email", "phone" etc!
"""

import sys
import re

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
            phi3_result: Parsed Llama result with extracted data

        Returns:
            (response_message, metadata)
        """
        # Get data from Llama (already extracted!) or fallback to full input
        value = phi3_result.get('data') or user_input

        # Default type
        data_type = 'note'

        # Auto-detect type from CONTENT pattern (NOT from keywords!)
        # EMAIL: has @ and .
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', value)
        if email_match:
            data_type = 'email'
            value = email_match.group()
        # PHONE: mostly digits with optional spaces/dashes
        else:
            phone_match = re.search(r'\b[\d\s\-\(\)]{7,}\b', value)
            if phone_match:
                # Check it's not mixed with letters
                phone_candidate = phone_match.group()
                if not any(c.isalpha() for c in phone_candidate):
                    data_type = 'phone'
                    value = phone_candidate.strip()

        label = ''
        context = ''

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

        # KISS: Simple confirmation from lang file
        confirmation = self.lang.get('msg_stored', '✅ Stored 🔒')

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
