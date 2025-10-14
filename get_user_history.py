#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Chat Terminal - User History Loader
Loads last N user inputs from database for arrow key navigation
"""

import sqlite3
import sys
import os

def get_user_history(limit=50):
    """
    Get last N user inputs from chat history (for arrow key navigation)

    Args:
        limit: Maximum number of history items to return

    Returns:
        List of user input strings in chronological order (oldest first)
    """
    db_path = os.path.expanduser("~/.aichat/memory.db")

    if not os.path.exists(db_path):
        return []

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if chat_history table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_history'")
        if not cursor.fetchone():
            conn.close()
            return []

        # Get last N user messages from chat_history table
        # We only want user messages (role='user'), not assistant responses
        cursor.execute("""
            SELECT DISTINCT content
            FROM chat_history
            WHERE role = 'user'
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        results = [row[0] for row in cursor.fetchall()]
        conn.close()

        # Return as-is (newest first from DESC order)
        # Arrow UP shows most recent messages first
        return results

    except Exception as e:
        print(f"Error loading history: {e}", file=sys.stderr)
        return []

if __name__ == "__main__":
    # Allow specifying limit as command line argument
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 50

    history = get_user_history(limit)

    # Print each item on separate line
    # Escape newlines for shell processing
    for item in history:
        # Replace actual newlines with \\n for shell parsing
        print(item.replace('\n', '\\n'))
