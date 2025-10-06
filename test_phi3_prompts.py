#!/usr/bin/env python3
"""
Systematischer Test verschiedener Phi-3 Prompt-Strategien
"""

import subprocess
import sys

def call_phi3(prompt):
    """Call Phi-3 and return output"""
    try:
        result = subprocess.run(
            ['ollama', 'run', 'phi3', prompt],
            capture_output=True,
            text=True,
            timeout=15
        )
        return result.stdout.strip()
    except:
        return "[ERROR]"

print("🧪 Systematischer Phi-3 Prompt Test\n")
print("=" * 70)

# Test Case: SAVE extraction
test_input = "save my email test@test.com"
expected = "email: test@test.com"

print(f"\n📝 Test Input: {test_input}")
print(f"✅ Expected: {expected}\n")

# Strategy 1: Direct pattern matching
print("Strategy 1: Direct Pattern Matching")
print("-" * 70)
prompt1 = f"""save my email test@test.com → email: test@test.com
save my phone 555-1234 → phone: 555-1234
{test_input} → """

result1 = call_phi3(prompt1)
print(f"Prompt:\n{prompt1}")
print(f"\nResult: {result1}")
print(f"Match: {'✅' if result1 == expected else '❌'}\n")

# Strategy 2: With explicit instruction
print("\nStrategy 2: Explicit Instruction")
print("-" * 70)
prompt2 = f"""Extract only the data part after "save my".

Examples:
save my email test@test.com → email: test@test.com
save my phone 555-1234 → phone: 555-1234

Extract:
{test_input} → """

result2 = call_phi3(prompt2)
print(f"Result: {result2}")
print(f"Match: {'✅' if result2 == expected else '❌'}\n")

# Strategy 3: JSON format
print("\nStrategy 3: JSON Format")
print("-" * 70)
prompt3 = f"""Extract data to JSON.

save my email test@test.com → {{"type": "email", "value": "test@test.com"}}
{test_input} → """

result3 = call_phi3(prompt3)
print(f"Result: {result3}")
print(f"Valid JSON: {'✅' if '{' in result3 else '❌'}\n")

# Strategy 4: One-shot with <output> tag
print("\nStrategy 4: Tagged Output")
print("-" * 70)
prompt4 = f"""Task: Extract data

Input: save my email test@test.com
<output>email: test@test.com</output>

Input: {test_input}
<output>"""

result4 = call_phi3(prompt4)
print(f"Result: {result4}")
print(f"Match: {'✅' if expected in result4 else '❌'}\n")

# Strategy 5: Ultra minimal
print("\nStrategy 5: Ultra Minimal")
print("-" * 70)
prompt5 = f"""{test_input} →"""

result5 = call_phi3(prompt5)
print(f"Prompt: {prompt5}")
print(f"Result: {result5}")
print(f"Match: {'✅' if result5 == expected else '❌'}\n")

print("=" * 70)
print("\n📊 SUMMARY:")
print(f"Strategy 1 (Pattern): {result1[:50]}...")
print(f"Strategy 2 (Instruction): {result2[:50]}...")
print(f"Strategy 3 (JSON): {result3[:50]}...")
print(f"Strategy 4 (Tagged): {result4[:50]}...")
print(f"Strategy 5 (Minimal): {result5[:50]}...")
