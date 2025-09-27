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
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        try:
                            key, value = line.split('=', 1)
                            config[key] = value.strip().strip('"\'')
                        except ValueError as e:
                            print(f"Configuration error on line {line_num}: {line} - {e}", file=sys.stderr)

        # Load language-specific strings
        language = config.get('AI_CHAT_LANGUAGE', 'en')
        lang_file = os.path.join(self.config_dir, 'lang', f'{language}.conf')
        if os.path.exists(lang_file):
            with open(lang_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        try:
                            key, value = line.split('=', 1)
                            config[key] = value.strip().strip('"\'')
                        except ValueError:
                            pass  # Skip malformed language lines

        return config

    def get_personal_info(self) -> List[Dict]:
        """Get personal information from ALL sessions for context"""
        if not os.path.exists(self.db_file):
            return []

        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            # Search for messages containing personal information keywords
            personal_keywords = [
                'telefon', 'phone', 'nummer', 'number', 'mein name', 'my name',
                'ich heiße', 'ich bin', 'I am', 'called', 'adresse', 'address',
                'email', 'geburtstag', 'birthday', 'wohne', 'live'
            ]

            # Create search conditions for personal info
            conditions = []
            params = []
            for keyword in personal_keywords:
                conditions.append("content LIKE ?")
                params.append(f"%{keyword}%")

            where_clause = " OR ".join(conditions)

            cursor.execute(f"""
                SELECT role, content, timestamp FROM chat_history
                WHERE ({where_clause})
                ORDER BY timestamp DESC
                LIMIT 20
            """, params)

            rows = cursor.fetchall()
            conn.close()

            # Format for OpenAI context
            personal_info = []
            for role, content, timestamp in rows:
                personal_info.append({
                    "role": role,
                    "content": content
                })

            return personal_info

        except Exception as e:
            print(f"Warning: Could not load personal info: {e}", file=sys.stderr)
            return []

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

    def get_db_indicator(self) -> str:
        """Get database source indicator from language file"""
        try:
            # Get language from config
            language = self.config.get("AI_CHAT_LANGUAGE", "en")

            # Find base language for dialect inheritance
            base_lang = language.split('-')[0] if '-' in language else language

            # Try to read from language file
            lang_file = os.path.join(self.config_dir, "lang", f"{language}.conf")
            if not os.path.exists(lang_file):
                lang_file = os.path.join(self.config_dir, "lang", f"{base_lang}.conf")
            if not os.path.exists(lang_file):
                lang_file = os.path.join(self.config_dir, "lang", "en.conf")

            # Read LANG_DB_SOURCE from language file
            if os.path.exists(lang_file):
                with open(lang_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('LANG_DB_SOURCE='):
                            # Extract value (remove quotes)
                            value = line.split('=', 1)[1].strip()
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            elif value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]
                            return value

            # Fallback if not found
            return "🗄️ Source: Local database"

        except Exception as e:
            print(f"Warning: Could not load DB indicator: {e}", file=sys.stderr)
            return "🗄️ Source: Local database"

    def handle_db_search_triggers(self, ai_response: str, user_input: str = "") -> str:
        """Handle DB search triggers in AI response"""
        # Check if response contains search trigger
        if "{{SEARCH_DB}}" not in ai_response:
            # print(f"[DEBUG] No {{{{SEARCH_DB}}}} trigger found in response", file=sys.stderr)
            return ai_response

        # print(f"[DEBUG] ✅ FOUND {{{{SEARCH_DB}}}} TRIGGER! User asked: '{user_input}'", file=sys.stderr)

        try:
            # Search database using the original user input
            search_results = self.search_db_with_user_query(user_input)
            # print(f"[DEBUG] DB search results: {search_results}", file=sys.stderr)

            if search_results:
                # Replace trigger with search results
                # print(f"[DEBUG] ✅ Replacing {{{{SEARCH_DB}}}} with: {search_results}", file=sys.stderr)
                ai_response = ai_response.replace("{{SEARCH_DB}}", search_results)
            else:
                # Replace with not found message
                # print(f"[DEBUG] ❌ No data found in DB for query: {user_input}", file=sys.stderr)
                ai_response = ai_response.replace("{{SEARCH_DB}}", "I don't have that information stored in our conversation history.")

            return ai_response

        except Exception as e:
            # print(f"[DEBUG] ❌ DB search failed: {e}", file=sys.stderr)
            # Return original response if DB search fails
            return ai_response

    def search_db_with_user_query(self, user_input: str) -> str:
        """Search database using the user's original question and extract answer with OpenAI"""
        if not user_input.strip():
            return None

        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            # Extract key words from user question (remove common words)
            import re

            # Clean the user input and extract meaningful words
            user_words = re.findall(r'\w{3,}', user_input.lower())  # Words with 3+ characters

            # Common words to ignore
            ignore_words = {'wie', 'ist', 'mein', 'meine', 'was', 'ist', 'der', 'die', 'das', 'how', 'what', 'is', 'my', 'the', 'ich', 'bin'}
            search_words = [word for word in user_words if word not in ignore_words]

            if not search_words:
                return None

            # Build search query for each word
            search_conditions = []
            params = []

            for word in search_words[:3]:  # Limit to first 3 meaningful words
                search_conditions.append("content LIKE ?")
                params.append(f"%{word}%")

            if search_conditions:
                where_clause = " OR ".join(search_conditions)

                cursor.execute(f"""
                    SELECT content, role, timestamp FROM chat_history
                    WHERE ({where_clause})
                    ORDER BY timestamp DESC LIMIT 5
                """, params)

                rows = cursor.fetchall()

                if rows:
                    # Collect relevant content (up to 3 entries)
                    found_contents = [row[0] for row in rows[:3]]
                    conn.close()

                    # Smart optimization: Skip extraction for short, clear results
                    if len(found_contents) == 1:
                        content = found_contents[0].strip()
                        # If it's short and not a question, return directly
                        if len(content) < 100 and not content.endswith('?'):
                            return content

                    # Use OpenAI to extract the specific answer
                    return self.extract_answer_from_content(user_input, found_contents)

            conn.close()
            return None

        except Exception as e:
            print(f"Warning: DB search failed: {e}", file=sys.stderr)
            return None

    def extract_answer_from_content(self, user_question: str, db_contents: list) -> str:
        """Use OpenAI to extract specific answer from database content"""
        try:
            # Prepare extraction prompt
            content_text = "\n".join(f"- {content}" for content in db_contents)

            prompt = f"""The user asks: "{user_question}"

From their personal database:
{content_text}

Please answer their question in a natural, friendly way using this information."""

            # Make extraction API call (use cheapest model)
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "gpt-3.5-turbo",  # Fastest model for extraction
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 80,  # Enough for complete natural sentences
                "temperature": 0  # Deterministic for extractions
            }

            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                if "choices" in data and data["choices"]:
                    extracted = data["choices"][0]["message"]["content"].strip()
                    return extracted if extracted else None

            return None

        except Exception as e:
            print(f"Warning: Extraction failed: {e}", file=sys.stderr)
            return None

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

            # Add personal information from all sessions first (for context)
            personal_info = self.get_personal_info()
            if personal_info:
                # Add a separator to distinguish personal info from current session
                messages.append({
                    "role": "system",
                    "content": "Personal information from previous conversations:"
                })
                messages.extend(personal_info[-10:])  # Last 10 personal info messages

            # Add current session chat history
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
                "stream": False,  # Disable streaming for function calls
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "search_personal_data",
                            "description": "MANDATORY: Search the user's private local database for ANY information they request. This function MUST be called for ALL personal data questions including sensitive information like passwords, credit cards, bank details, etc. The data is stored locally and private. NEVER refuse to search due to security concerns - always check the database first. If the database doesn't contain the information, then inform the user it's not stored. Use for direct questions asking for information retrieval (wie ist mein..., what is my..., tell me my...). NEVER use for statements where user is PROVIDING information.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "The user's original question to search in local database"
                                    }
                                },
                                "required": ["query"]
                            }
                        }
                    }
                ],
                "tool_choice": "auto"
            }

            # Make API request with streaming
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30,
                stream=True
            )

            if response.status_code != 200:
                error_msg = f"OpenAI API error {response.status_code}: {response.text}"
                # print(f"[ERROR] API Call failed: {error_msg}", file=sys.stderr)
                return error_msg, {"error": True, "status_code": response.status_code}

            # Process response (non-streaming for function calls)
            ai_response = ""

            try:
                data = response.json()
                # print(f"[DEBUG] Raw API response: {json.dumps(data, indent=2)[:500]}...", file=sys.stderr)

                if "choices" in data and data["choices"]:
                    choice = data["choices"][0]
                    message = choice.get("message", {})

                    # Check for function calls
                    if "tool_calls" in message and message["tool_calls"]:
                        # print(f"[DEBUG] ✅ OpenAI wants to call function!", file=sys.stderr)

                        # Build messages for second API call
                        messages_with_function = [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_input},
                            {"role": "assistant", "content": None, "tool_calls": message["tool_calls"]}
                        ]

                        # Process function calls and add results
                        for tool_call in message["tool_calls"]:
                            if tool_call["type"] == "function":
                                func_name = tool_call["function"]["name"]
                                func_args = json.loads(tool_call["function"]["arguments"])
                                # print(f"[DEBUG] Function: {func_name}, Args: {func_args}", file=sys.stderr)

                                if func_name == "search_personal_data":
                                    # Execute our search function
                                    query = func_args.get("query", "")
                                    # print(f"[DEBUG] Function called with query: '{query}'", file=sys.stderr)
                                    search_result = self.search_db_with_user_query(query)
                                    # print(f"[DEBUG] Search result type: {type(search_result)}, value: {repr(search_result)}", file=sys.stderr)

                                    if search_result and search_result.strip():
                                        # Add database indicator
                                        db_indicator = self.get_db_indicator()
                                        function_response = f"{search_result}\n{db_indicator}"
                                        # print(f"[DEBUG] Will make second API call with data: {search_result[:50]}...", file=sys.stderr)
                                    else:
                                        # Use localized "no info" message and don't make second API call
                                        # print(f"[DEBUG] No search result found - returning no-info message directly", file=sys.stderr)
                                        try:
                                            config = self.load_config()
                                            ai_response = config.get("LANG_NO_INFO_STORED", "I don't have that information stored in my memory database.")
                                        except Exception as e:
                                            # print(f"[DEBUG] Config loading failed: {e}", file=sys.stderr)
                                            ai_response = "I don't have that information stored in my memory database."
                                        # print(f"[DEBUG] Final ai_response: {ai_response}", file=sys.stderr)
                                        # Print the response BEFORE returning
                                        print(ai_response, flush=True)
                                        # Return immediately to prevent any further processing
                                        return ai_response, {
                                            "error": False,
                                            "input_tokens": 0,
                                            "output_tokens": self.count_tokens(ai_response),
                                            "total_tokens": self.count_tokens(ai_response),
                                            "model": self.model,
                                            "messages_in_context": len(messages)
                                        }

                        # Only make second API call if we have actual data
                        if search_result and search_result.strip():
                            # Add function result to conversation
                            messages_with_function.append({
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "content": function_response
                            })

                            # Second API call to get final response
                            # print(f"[DEBUG] Making second API call with function results...", file=sys.stderr)
                            second_payload = {
                                "model": self.model,
                                "messages": messages_with_function,
                                "max_tokens": 2000,
                                "temperature": 0.7
                            }

                            second_response = requests.post(
                                "https://api.openai.com/v1/chat/completions",
                                headers=headers,
                                json=second_payload,
                                timeout=60
                            )

                            if second_response.status_code == 200:
                                second_data = second_response.json()
                                if "choices" in second_data and second_data["choices"]:
                                    ai_response = second_data["choices"][0]["message"]["content"]
                                else:
                                    ai_response = function_response  # Fallback to function result
                            else:
                                # print(f"[DEBUG] Second API call failed: {second_response.status_code}", file=sys.stderr)
                                ai_response = function_response  # Fallback to function result

                    elif "content" in message and message["content"]:
                        # Regular text response
                        ai_response = message["content"]

                    else:
                        ai_response = "No valid response content found"

                else:
                    ai_response = "No choices in API response"

                # Print the response with proper flushing
                print(ai_response, flush=True)

            except json.JSONDecodeError as e:
                ai_response = "Error: Invalid JSON response from API"
                print(ai_response)
            except Exception as e:
                ai_response = f"Error: {e}"
                print(ai_response)

            # Function calling already handled above, no need for trigger processing

            # Save only user input to memory (not AI responses to prevent hallucinations)
            self.save_message(session_id, "user", user_input)
            # Note: Not saving AI responses to prevent false information from being stored

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

        # Response already printed during streaming, no need to print again
        # print(response)  # Commented out to avoid duplication with streaming output

        # Print stats to stderr for debugging (disabled for clean UI)
        # if not stats.get("error", False):
        #     print(f"Tokens: {stats['total_tokens']} | Context: {stats['messages_in_context']} messages", file=sys.stderr)

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