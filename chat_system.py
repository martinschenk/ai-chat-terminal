#!/usr/bin/env python3
"""
AI Chat Terminal - Direct OpenAI API Integration
Replaces shell-gpt dependency with native Python implementation
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
import warnings
from typing import Dict, List, Optional, Tuple

# Suppress urllib3 LibreSSL warnings on macOS BEFORE importing requests
# This is a known issue: https://github.com/urllib3/urllib3/issues/3020
# urllib3 v2 requires OpenSSL 1.1.1+ but macOS ships with LibreSSL 2.8.3
# The functionality still works correctly, only the warning is cosmetic
warnings.filterwarnings("ignore", message=".*urllib3 v2.*OpenSSL.*")

# Now safe to import requests (which uses urllib3)
import requests

# Additional urllib3 warning suppression for runtime
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)
except (ImportError, AttributeError):
    pass

class ChatSystem:
    def __init__(self, config_dir: str = None):
        self.config_dir = config_dir or os.path.expanduser("~/.aichat")
        self.env_file = os.path.join(self.config_dir, ".env")
        self.config_file = os.path.join(self.config_dir, "config")
        self.db_file = os.path.join(self.config_dir, "memory.db")

        # Load environment and config
        self.api_key = self.load_api_key()
        self.config = self.load_config()

        # OpenAI API settings
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = self.config.get("AI_CHAT_MODEL", "gpt-4o-mini")
        self.context_window = int(self.config.get("AI_CHAT_CONTEXT_WINDOW", "20"))

    def load_api_key(self) -> str:
        """Load OpenAI API key from .env file"""
        if not os.path.exists(self.env_file):
            raise FileNotFoundError(f"API key file not found: {self.env_file}")

        with open(self.env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('OPENAI_API_KEY='):
                    key = line.split('=', 1)[1].strip().strip('"\'')
                    if key:
                        return key

        raise ValueError("OPENAI_API_KEY not found in .env file")

    def load_config(self) -> Dict[str, str]:
        """Load configuration from config file"""
        config = {}
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        config[key] = value.strip().strip('"\'')
        return config

    def get_chat_history(self, session_id: str, limit: int = None) -> List[Dict]:
        """Get chat history from memory database"""
        if limit is None:
            limit = self.context_window * 2  # user + assistant pairs

        if not os.path.exists(self.db_file):
            return []

        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            # Get recent messages for this session
            cursor.execute("""
                SELECT role, content, timestamp FROM chat_history
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (session_id, limit))

            rows = cursor.fetchall()
            conn.close()

            # Reverse to get chronological order and format for OpenAI
            messages = []
            for role, content, timestamp in reversed(rows):
                messages.append({
                    "role": role,
                    "content": content
                })

            return messages

        except Exception as e:
            print(f"Warning: Could not load chat history: {e}", file=sys.stderr)
            return []

    def save_message(self, session_id: str, role: str, content: str):
        """Save message to memory database"""
        try:
            # Import memory system to use existing save functionality
            script_dir = os.path.dirname(os.path.abspath(__file__))
            sys.path.insert(0, script_dir)

            # Use existing memory_system.py
            import subprocess
            memory_script = os.path.join(script_dir, "memory_system.py")
            if os.path.exists(memory_script):
                subprocess.run([
                    sys.executable, memory_script, "add",
                    session_id, role, content
                ], capture_output=True, timeout=5)

        except Exception as e:
            print(f"Warning: Could not save to memory: {e}", file=sys.stderr)

    def count_tokens(self, text: str) -> int:
        """Rough token count estimation (1 token ≈ 4 characters)"""
        return len(text) // 4

    def send_message(self, session_id: str, user_input: str, system_prompt: str = "") -> Tuple[str, Dict]:
        """Send message to OpenAI API and get response"""
        try:
            # Build messages array
            messages = []

            # Add system prompt if provided
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })

            # Add chat history
            history = self.get_chat_history(session_id)
            messages.extend(history)

            # Add current user message
            messages.append({
                "role": "user",
                "content": user_input
            })

            # Prepare API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2000,
                "stream": False
            }

            # Make API request
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code != 200:
                error_msg = f"OpenAI API error {response.status_code}: {response.text}"
                return error_msg, {"error": True, "status_code": response.status_code}

            # Parse response
            data = response.json()

            if "choices" not in data or not data["choices"]:
                return "Error: No response from OpenAI API", {"error": True}

            ai_response = data["choices"][0]["message"]["content"]

            # Save both messages to memory
            self.save_message(session_id, "user", user_input)
            self.save_message(session_id, "assistant", ai_response)

            # Calculate token usage
            input_tokens = sum(self.count_tokens(msg["content"]) for msg in messages)
            output_tokens = self.count_tokens(ai_response)

            stats = {
                "error": False,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "model": self.model,
                "messages_in_context": len(messages)
            }

            return ai_response, stats

        except requests.exceptions.Timeout:
            return "Error: Request timed out. Please try again.", {"error": True, "timeout": True}
        except requests.exceptions.RequestException as e:
            return f"Error: Network error - {e}", {"error": True, "network": True}
        except json.JSONDecodeError:
            return "Error: Invalid response from OpenAI API", {"error": True, "json": True}
        except Exception as e:
            return f"Error: {e}", {"error": True, "exception": str(e)}

def main():
    """Command line interface"""
    if len(sys.argv) < 3:
        print("Usage: python3 chat_system.py <session_id> <message> [system_prompt]")
        sys.exit(1)

    session_id = sys.argv[1]
    user_message = sys.argv[2]
    system_prompt = sys.argv[3] if len(sys.argv) > 3 else ""

    try:
        chat = ChatSystem()
        response, stats = chat.send_message(session_id, user_message, system_prompt)

        # Print response (this is what the shell script will capture)
        print(response)

        # Print stats to stderr for debugging
        if not stats.get("error", False):
            print(f"Tokens: {stats['total_tokens']} | Context: {stats['messages_in_context']} messages", file=sys.stderr)

    except FileNotFoundError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        print("Error: OpenAI API key not configured. Please run setup first.")
        sys.exit(1)
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        print("Error: Invalid API key configuration.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        print("Error: An unexpected error occurred. Please try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()