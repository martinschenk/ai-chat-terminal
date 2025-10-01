#!/usr/bin/env python3
"""
Test script for enhanced response_generator.py (v8.0.0)
Tests new keyword-based functions
"""

from response_generator import ResponseGenerator

def test_format_stored_data():
    """Test format_stored_data() function"""
    print("🧪 Testing format_stored_data()")
    print("=" * 60)

    gen = ResponseGenerator()

    test_cases = [
        ("speichere lokal: mein API Key ist sk-abc123", "de"),
        ("save locally: my password is secret123", "en"),
        ("guarda localmente: mi correo es test@example.com", "es"),
    ]

    for message, lang in test_cases:
        response = gen.format_stored_data(message, lang)
        print(f"Input ({lang}): {message}")
        print(f"Response: {response}")
        print()

def test_format_retrieved_data():
    """Test format_retrieved_data() function"""
    print("🧪 Testing format_retrieved_data()")
    print("=" * 60)

    gen = ResponseGenerator()

    test_cases = [
        (
            "aus meiner db: was ist mein API Key?",
            [{'content': 'sk-proj-xyz789...', 'data_type': 'API_KEY'}],
            "de"
        ),
        (
            "from my database: what's my email?",
            [{'content': 'test@example.com', 'data_type': 'EMAIL'}],
            "en"
        ),
        (
            "de mi db: cuál es mi teléfono?",
            [{'content': '+34 123 456 789', 'data_type': 'PHONE'}],
            "es"
        ),
        (
            "show my local data about Python",
            [],  # No results
            "en"
        )
    ]

    for query, results, lang in test_cases:
        response = gen.format_retrieved_data(query, results, lang)
        print(f"Query ({lang}): {query}")
        print(f"Results: {len(results)} found")
        print(f"Response: {response}")
        print()

def test_generator_info():
    """Test generator info"""
    print("ℹ️  Generator Info")
    print("=" * 60)

    gen = ResponseGenerator()
    info = gen.get_generator_info()

    print(f"Phi-3 available: {info['phi3_available']}")
    print(f"Phi-3 enabled: {info['phi3_enabled']}")
    print(f"Generation mode: {info['generation_mode']}")
    print(f"Language: {info['language']}")
    print(f"Supported languages: {', '.join(info['supported_languages'])}")
    print()

if __name__ == '__main__':
    print("🤖 Response Generator v8.0.0 Test Suite")
    print("=" * 60)
    print()

    test_generator_info()
    test_format_stored_data()
    test_format_retrieved_data()

    print("✅ All tests completed!")
