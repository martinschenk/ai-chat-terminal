#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DELETE Handler v10.1.0 - ULTRA KISS!
Nutzt Llama 3.2 für Query Extraction, löscht aus local_data
"""

import sqlite3

class DeleteHandler:
    """Handler für DELETE Operationen"""

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
        Handle DELETE action

        Args:
            user_input: "delete my email"

        Returns:
            (response_message, metadata)
        """
        # Extract search term with Llama - returns tuple!
        search_term, method = self.phi3.extract_for_delete(user_input)

        # Check if Llama failed
        if search_term is None or method == 'error':
            error_msg = f"❌ Llama extraction failed for: {user_input}\nPlease report this case!"
            return error_msg, {"error": True, "llama_failed": True}

        # Delete from DB
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Find and delete matching entries
            cursor.execute("""
                DELETE FROM local_data
                WHERE content LIKE ?
            """, (f"%{search_term}%",))

            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()

            if deleted_count > 0:
                # Success with method info
                confirmation = self.lang.get('msg_deleted', '🗑️ Deleted')
                method_info = f" [via {method}]" if method == 'regex' else ""
                return f"{confirmation} ({deleted_count}){method_info}", {
                    "error": False,
                    "model": "local-delete",
                    "tokens": 0,
                    "source": "local",
                    "deleted_count": deleted_count,
                    "method": method
                }
            else:
                # Nothing found
                no_results = self.lang.get('msg_no_results', '❌ No data found')
                return no_results, {
                    "error": False,
                    "model": "local-delete",
                    "tokens": 0,
                    "source": "local"
                }

        except Exception as e:
            error_msg = f"❌ Delete error: {e}"
            return error_msg, {"error": True}
