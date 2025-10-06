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
        # Extract data with Llama - returns tuple!
        content, method = self.phi3.extract_for_save(user_input)

        # Check if Llama failed
        if content is None or method == 'error':
            error_msg = f"❌ Llama extraction failed for: {user_input}\nPlease report this case!"
            return error_msg, {"error": True, "llama_failed": True}

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

            # Success message with extraction method
            confirmation = self.lang.get('msg_stored', '✅ Stored 🔒')
            method_info = f" [via {method}]" if method == 'regex' else ""

            return f"{confirmation}{method_info}", {
                "error": False,
                "model": "local-save",
                "tokens": 0,
                "source": "local",
                "method": method
            }

        except Exception as e:
            error_msg = f"❌ Save error: {e}"
            return error_msg, {"error": True}
