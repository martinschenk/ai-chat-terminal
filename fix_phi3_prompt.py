#!/usr/bin/env python3
"""
Surgical fix for phi3_intent_parser.py
Replace complex prompt with KISS version
"""

def fix_prompt():
    """Replace _build_prompt method with KISS version"""

    # Read the file
    with open('/Users/martin/.aichat/phi3_intent_parser.py', 'r') as f:
        lines = f.readlines()

    # Find the _build_prompt method (line 191)
    start_idx = None
    for i, line in enumerate(lines):
        if 'def _build_prompt(self, user_message: str, matched_keywords: List[str]) -> str:' in line:
            start_idx = i
            break

    if start_idx is None:
        print("❌ Could not find _build_prompt method!")
        return False

    # Find the next method _fallback_response (line 510)
    end_idx = None
    for i in range(start_idx + 1, len(lines)):
        if 'def _fallback_response' in lines[i]:
            end_idx = i
            break

    if end_idx is None:
        print("❌ Could not find _fallback_response method!")
        return False

    print(f"✅ Found _build_prompt at line {start_idx + 1}")
    print(f"✅ Found _fallback_response at line {end_idx + 1}")
    print(f"📝 Replacing {end_idx - start_idx} lines with KISS version...")

    # New KISS method
    new_method = '''    def _build_prompt(self, user_message: str, matched_keywords: List[str]) -> str:
        """Build ULTRA-KISS Phi-3 prompt - simple and fast"""

        # Escape user message for safe JSON
        safe_message = user_message.replace('"', '\\\\"').replace('\\n', ' ')

        return f"""Classify database intent.

Message: "{safe_message}"

Rules:
- "save/remember/remind X" with data (email@, phone number, address) → SAVE
- "show/what/which is my X" (specific item) → RETRIEVE
- "delete/forget X" → DELETE
- "list/all/show all" → LIST
- Otherwise → NORMAL

EXAMPLES:
"save my phone 123456" → SAVE
"show my phone" → RETRIEVE
"what's my email?" → RETRIEVE
"list all data" → LIST
"delete my email" → DELETE
"hello there" → NORMAL

JSON response:
{{
  "action": "SAVE|RETRIEVE|DELETE|LIST|NORMAL",
  "data": {{
    "type": "email|phone|address|note",
    "value": "extracted data if SAVE"
  }}
}}"""

'''

    # Reconstruct file
    new_lines = lines[:start_idx] + [new_method] + lines[end_idx:]

    # Write back
    with open('/Users/martin/.aichat/phi3_intent_parser.py', 'w') as f:
        f.writelines(new_lines)

    # Also update Development version
    with open('/Users/martin/Development/ai-chat-terminal/phi3_intent_parser.py', 'w') as f:
        f.writelines(new_lines)

    print(f"✅ Fixed! Reduced from {len(lines)} to {len(new_lines)} lines")
    print(f"📉 Removed {len(lines) - len(new_lines)} lines of complex prompt")

    return True

if __name__ == '__main__':
    if fix_prompt():
        print("\n🎉 SUCCESS! Phi-3 prompt simplified to KISS version")
        print("📝 Files updated:")
        print("   - /Users/martin/.aichat/phi3_intent_parser.py")
        print("   - /Users/martin/Development/ai-chat-terminal/phi3_intent_parser.py")
    else:
        print("\n❌ FAILED! Check errors above")
