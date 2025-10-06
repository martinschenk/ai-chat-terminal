#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAVE Handler v10.1.0 - ULTRA KISS!
Nutzt Llama 3.2 für Data Extraction, speichert in local_data
"""

import sqlite3
import time

class SaveHandler:
    """Handler für SAVE Operationen"""

    def __init__(self, db_path, llama_extractor, lang_manager):
        """
        Args:
            db_path: Path to memory.db
            llama_extractor: LlamaDataExtractor instance
            lang_manager: LangManager instance
        """
        self.db_path = db_path
        self.phi3 = llama_extractor  # Keep 'phi3' name for compatibility
        self.lang = lang_manager

    def handle(self, user_input: str) -> tuple:
        """
        Handle SAVE action

        Args:
            user_input: "save my email test@test.com"

        Returns:
            (response_message, metadata)
        """
        # Extract data with Phi-3
        content = self.phi3.extract_for_save(user_input)

        if not content or content == user_input:
            # Phi-3 failed - fallback to user_input
            content = user_input

        # Save to DB
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO local_data (timestamp, content)
                VALUES (?, ?)
            """, (int(time.time()), content))

            conn.commit()
            conn.close()

            # Success message
            confirmation = self.lang.get('msg_stored', '✅ Stored 🔒')

            return confirmation, {
                "error": False,
                "model": "local-save",
                "tokens": 0,
                "source": "local"
            }

        except Exception as e:
            error_msg = f"❌ Save error: {e}"
            return error_msg, {"error": True}
