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
        # Extract data from user_input (KISS - regex based!)
        import re

        # Detect type from keywords FIRST!
        data_type = 'note'  # default
        value = user_input  # default

        user_lower = user_input.lower()

        # Check keywords to determine type
        if 'email' in user_lower or 'e-mail' in user_lower:
            # EMAIL: extract email@domain
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', user_input)
            if email_match:
                data_type = 'email'
                value = email_match.group()
        elif 'phone' in user_lower or 'telefon' in user_lower or 'number' in user_lower or 'handy' in user_lower:
            # PHONE: extract phone number (digits/spaces/dashes)
            phone_match = re.search(r'[\d\s\-\(\)]{7,}', user_input)
            if phone_match:
                data_type = 'phone'
                value = phone_match.group().strip()
        elif 'address' in user_lower or 'adresse' in user_lower or 'calle' in user_lower or 'street' in user_lower:
            # ADDRESS: take everything after keyword
            data_type = 'address'
            value = re.sub(r'^(save|remember|store|merke|speicher)\s+(my|meine?)\s+(address|adresse)\s+', '', user_input, flags=re.IGNORECASE)
        elif 'password' in user_lower or 'passwort' in user_lower:
            # PASSWORD: take everything after keyword
            data_type = 'password'
            value = re.sub(r'^(save|remember|store|merke|speicher)\s+(my|meine?)\s+(password|passwort)\s+', '', user_input, flags=re.IGNORECASE)
        else:
            # No keyword found - try auto-detect
            # EMAIL: anything with @
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', user_input)
            if email_match:
                data_type = 'email'
                value = email_match.group()
            # PHONE: ONLY if it looks like a phone (no letters mixed in)
            else:
                phone_match = re.search(r'\b[\d\s\-\(\)]{9,}\b', user_input)
                if phone_match and not any(c.isalpha() for c in phone_match.group()):
                    data_type = 'phone'
                    value = phone_match.group().strip()

        # If still no value extracted, take everything after "save/remember"
        if value == user_input:
            # Remove keywords from the beginning
            value = re.sub(r'^(save|remember|store|merke|speicher)\s+(my|meine?)\s+', '', user_input, flags=re.IGNORECASE)

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
