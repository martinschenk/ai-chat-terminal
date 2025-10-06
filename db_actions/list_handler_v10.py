#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIST Handler v10.1.0 - ULTRA KISS + Llama 3.2 Filtering!
Zeigt alle Daten oder gefiltert nach Typ
"""

import sqlite3

class ListHandler:
    """Handler für LIST Operationen"""

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
        Handle LIST action with optional filtering

        Args:
            user_input: "show all my data" or "list my emails"

        Returns:
            (response_message, metadata)
        """
        # Extract filter with Llama
        filter_term, method = self.phi3.extract_for_list(user_input)

        # Check if Llama failed
        if filter_term is None or method == 'error':
            error_msg = f"❌ Llama extraction failed for: {user_input}\nPlease report this case!"
            return error_msg, {"error": True, "llama_failed": True}

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check if filter is "*" (all) or specific
            if filter_term == "*":
                # Get ALL data
                cursor.execute("""
                    SELECT content
                    FROM local_data
                    ORDER BY timestamp DESC
                    LIMIT 50
                """)
            else:
                # Get FILTERED data
                cursor.execute("""
                    SELECT content
                    FROM local_data
                    WHERE content LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT 50
                """, (f"%{filter_term}%",))

            results = cursor.fetchall()
            conn.close()

            if results:
                # Format list
                filter_info = f" (filtered by '{filter_term}')" if filter_term != "*" else ""
                method_info = f" [via {method}]" if method == 'regex' else ""

                lines = [f"📦 Your data ({len(results)}){filter_info}{method_info}:"]
                for i, (content,) in enumerate(results, 1):
                    # Truncate long content
                    display = content[:70] + "..." if len(content) > 70 else content
                    lines.append(f"  {i}. {display}")

                response = "\n".join(lines)

                return response, {
                    "error": False,
                    "model": "local-list",
                    "tokens": 0,
                    "source": "local",
                    "count": len(results),
                    "filter": filter_term,
                    "method": method
                }
            else:
                # No data found
                if filter_term == "*":
                    empty_msg = self.lang.get('msg_list_empty', 'No data stored yet')
                else:
                    empty_msg = f"📦 No '{filter_term}' found"

                return empty_msg, {
                    "error": False,
                    "model": "local-list",
                    "tokens": 0,
                    "source": "local",
                    "filter": filter_term
                }

        except Exception as e:
            error_msg = f"❌ List error: {e}"
            return error_msg, {"error": True}
