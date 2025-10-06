#!/usr/bin/env python3
"""
Test the new KISS Phi-3 prompt
"""
import sys
sys.path.insert(0, '/Users/martin/.aichat')

from phi3_intent_parser import Phi3IntentParser

def test_cases():
    parser = Phi3IntentParser()

    tests = [
        ("save my phone number 13243546", ['save', 'my', 'phone'], "SAVE"),
        ("show my phone number", ['show', 'my', 'phone'], "RETRIEVE"),
        ("show my email", ['show', 'my', 'email'], "RETRIEVE"),
        ("what data do you have?", ['what', 'data', 'you'], "LIST"),
        ("delete my phone", ['delete', 'my', 'phone'], "DELETE"),
    ]

    print("🧪 Testing KISS Phi-3 Intent Parser\n")
    print("=" * 70)

    passed = 0
    failed = 0

    for message, keywords, expected in tests:
        print(f"\n📝 Input: {message}")
        print(f"🔑 Keywords: {keywords}")
        print(f"🎯 Expected: {expected}")

        result = parser.parse_intent(message, keywords)
        actual = result.get('action')

        if actual == expected:
            print(f"✅ PASS: Got {actual}")
            passed += 1
        else:
            print(f"❌ FAIL: Got {actual} (expected {expected})")
            print(f"📦 Full result: {result}")
            failed += 1

        print("-" * 70)

    print(f"\n{'='*70}")
    print(f"📊 Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print(f"{'='*70}\n")

    return failed == 0

if __name__ == '__main__':
    success = test_cases()
    sys.exit(0 if success else 1)
