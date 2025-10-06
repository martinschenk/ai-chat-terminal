#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RETRIEVE Handler v10.1.0 - ULTRA KISS!
Nutzt Llama 3.2 für Query Extraction, semantic search in local_data
"""

import sqlite3

class RetrieveHandler:
    """Handler für RETRIEVE Operationen"""

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
        Handle RETRIEVE action

        Args:
            user_input: "show my email"

        Returns:
            (response_message, metadata)
        """
        # Extract search term with Phi-3
        search_term = self.phi3.extract_for_retrieve(user_input)

        if not search_term:
            search_term = user_input

        # Search in DB (simple LIKE search)
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT content
                FROM local_data
                WHERE content LIKE ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (f"%{search_term}%",))

            result = cursor.fetchone()
            conn.close()

            if result:
                # Found - show with icon
                content = result[0]
                return f"🔍 {content}", {
                    "error": False,
                    "model": "local-retrieve",
                    "tokens": 0,
                    "source": "local"
                }
            else:
                # Not found
                no_results = self.lang.get('msg_no_results', '❌ No data found')
                return no_results, {
                    "error": False,
                    "model": "local-retrieve",
                    "tokens": 0,
                    "source": "local"
                }

        except Exception as e:
            error_msg = f"❌ Retrieve error: {e}"
            return error_msg, {"error": True}
