#!/usr/bin/env python3
"""
AI Chat Terminal - PII Detection Test Suite
Comprehensive testing for Presidio integration and response generation
"""

import sys
import time
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from pii_detector import PIIDetector
    from response_generator import ResponseGenerator
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

class PIITestSuite:
    def __init__(self):
        self.detector = PIIDetector()
        self.generator = ResponseGenerator()
        self.test_results = []

    def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 AI Chat Terminal - PII Detection Test Suite")
        print("=" * 60)
        print()

        # Display system info
        self._show_system_info()
        print()

        # Run test categories
        self._test_pii_detection()
        self._test_multilingual_detection()
        self._test_edge_cases()
        self._test_response_generation()
        self._test_performance()

        # Show summary
        self._show_summary()

    def _show_system_info(self):
        """Display information about detection capabilities"""
        print("🔧 System Information:")
        print("-" * 30)

        detector_info = self.detector.get_detection_info()
        generator_info = self.generator.get_generator_info()

        print(f"Presidio available: {detector_info['presidio_available']}")
        print(f"Analyzer ready: {detector_info['analyzer_ready']}")
        print(f"Detection methods: {', '.join(detector_info['detection_methods'])}")
        print(f"Supported languages: {', '.join(detector_info['supported_languages'])}")
        print()
        print(f"Phi-3 available: {generator_info['phi3_available']}")
        print(f"Phi-3 enabled: {generator_info['phi3_enabled']}")
        print(f"Generation mode: {generator_info['generation_mode']}")
        print(f"Response language: {generator_info['language']}")

    def _test_pii_detection(self):
        """Test basic PII detection functionality"""
        print("🔍 Testing PII Detection:")
        print("-" * 30)

        test_cases = [
            # Credit Cards
            {
                'text': "My credit card is 4532-1234-5678-9012",
                'expected': True,
                'expected_types': ['CREDIT_CARD'],
                'description': "Standard credit card format"
            },
            {
                'text': "Kreditkarte: 4111 1111 1111 1111",
                'expected': True,
                'expected_types': ['CREDIT_CARD'],
                'description': "German credit card with spaces"
            },

            # API Keys
            {
                'text': "API key: sk-proj-abc123def456ghi789jkl012mno345pqr678stu901",
                'expected': True,
                'expected_types': ['OPENAI_API_KEY', 'OPENAI_PROJECT_KEY'],
                'description': "OpenAI project API key"
            },
            {
                'text': "GitHub token: ghp_1234567890abcdef1234567890abcdef12",
                'expected': True,
                'expected_types': ['GITHUB_TOKEN'],
                'description': "GitHub personal access token"
            },

            # Emails
            {
                'text': "Contact me at test@example.com",
                'expected': True,
                'expected_types': ['EMAIL'],
                'description': "Standard email address"
            },

            # Phone Numbers
            {
                'text': "Call me at +49 151 12345678",
                'expected': True,
                'expected_types': ['PHONE'],
                'description': "International phone number"
            },

            # Passwords
            {
                'text': "Password: mySecretPassword123",
                'expected': True,
                'expected_types': ['PASSWORD'],
                'description': "Password with label"
            },

            # Non-PII (should not trigger)
            {
                'text': "What's the weather like today?",
                'expected': False,
                'expected_types': [],
                'description': "General question"
            },
            {
                'text': "I need a card for the presentation",
                'expected': False,
                'expected_types': [],
                'description': "Card in non-financial context"
            }
        ]

        for i, test_case in enumerate(test_cases, 1):
            success = self._run_detection_test(i, test_case)
            self.test_results.append({
                'category': 'PII Detection',
                'test': test_case['description'],
                'success': success
            })

        print()

    def _test_multilingual_detection(self):
        """Test multilingual PII detection"""
        print("🌍 Testing Multilingual Detection:")
        print("-" * 35)

        multilingual_cases = [
            {
                'text': "Meine E-Mail ist martin@example.de",
                'expected': True,
                'description': "German email"
            },
            {
                'text': "Mi contraseña es miPassword123",
                'expected': True,
                'description': "Spanish password"
            },
            {
                'text': "Mon numéro de téléphone: +33 1 23 45 67 89",
                'expected': True,
                'description': "French phone number"
            },
            {
                'text': "API chiave: sk-test123456789012345678901234567890123456",
                'expected': True,
                'description': "Italian API key"
            }
        ]

        for i, test_case in enumerate(multilingual_cases, 1):
            success = self._run_detection_test(i, test_case, prefix="ML")
            self.test_results.append({
                'category': 'Multilingual',
                'test': test_case['description'],
                'success': success
            })

        print()

    def _test_edge_cases(self):
        """Test edge cases and potential false positives"""
        print("⚠️ Testing Edge Cases:")
        print("-" * 25)

        edge_cases = [
            {
                'text': "Credit card format is XXXX-XXXX-XXXX-XXXX",
                'expected': False,
                'description': "Credit card format description"
            },
            {
                'text': "The API key format starts with sk-",
                'expected': False,
                'description': "API key format description"
            },
            {
                'text': "Email format: user@domain.com",
                'expected': True,  # This might still trigger, which is okay
                'description': "Email example in documentation"
            },
            {
                'text': "Phone number: 123-456-7890",
                'expected': True,
                'description': "Example phone number"
            },
            {
                'text': "",
                'expected': False,
                'description': "Empty string"
            },
            {
                'text': "   ",
                'expected': False,
                'description': "Whitespace only"
            }
        ]

        for i, test_case in enumerate(edge_cases, 1):
            success = self._run_detection_test(i, test_case, prefix="EDGE")
            self.test_results.append({
                'category': 'Edge Cases',
                'test': test_case['description'],
                'success': success
            })

        print()

    def _test_response_generation(self):
        """Test response generation with templates and Phi-3"""
        print("🤖 Testing Response Generation:")
        print("-" * 32)

        # Test storage confirmations
        storage_tests = [
            {
                'pii_types': ['OPENAI_API_KEY'],
                'description': "OpenAI API key storage"
            },
            {
                'pii_types': ['CREDIT_CARD'],
                'description': "Credit card storage"
            },
            {
                'pii_types': ['EMAIL', 'PHONE'],
                'description': "Multiple PII types storage"
            }
        ]

        print("  📝 Storage Confirmations:")
        for i, test in enumerate(storage_tests, 1):
            try:
                response = self.generator.confirm_storage(test['pii_types'])
                success = len(response) > 10 and ('lokal' in response.lower() or 'local' in response.lower())
                status = "✅" if success else "❌"
                print(f"    {i}. {test['description']}: {status}")
                if not success:
                    print(f"       Response: {response[:50]}...")

                self.test_results.append({
                    'category': 'Response Generation',
                    'test': f"Storage: {test['description']}",
                    'success': success
                })
            except Exception as e:
                print(f"    {i}. {test['description']}: ❌ (Error: {e})")
                self.test_results.append({
                    'category': 'Response Generation',
                    'test': f"Storage: {test['description']}",
                    'success': False
                })

        # Test query responses
        query_tests = [
            {
                'query': "What's my API key?",
                'results': [{'content': 'sk-test123...', 'data_type': 'API_KEY'}],
                'description': "API key query"
            },
            {
                'query': "Show me my email",
                'results': [{'content': 'test@example.com', 'data_type': 'EMAIL'}],
                'description': "Email query"
            },
            {
                'query': "Find my password",
                'results': [],
                'description': "No results query"
            }
        ]

        print("  🔍 Query Responses:")
        for i, test in enumerate(query_tests, 1):
            try:
                response = self.generator.generate_response(test['query'], test['results'])
                success = len(response) > 5
                status = "✅" if success else "❌"
                print(f"    {i}. {test['description']}: {status}")

                self.test_results.append({
                    'category': 'Response Generation',
                    'test': f"Query: {test['description']}",
                    'success': success
                })
            except Exception as e:
                print(f"    {i}. {test['description']}: ❌ (Error: {e})")
                self.test_results.append({
                    'category': 'Response Generation',
                    'test': f"Query: {test['description']}",
                    'success': False
                })

        print()

    def _test_performance(self):
        """Test performance of PII detection"""
        print("⚡ Testing Performance:")
        print("-" * 22)

        test_text = "My email is test@example.com and my API key is sk-proj-abc123def456"
        num_tests = 10

        start_time = time.time()
        for _ in range(num_tests):
            self.detector.check_for_pii(test_text)
        end_time = time.time()

        avg_time = (end_time - start_time) / num_tests * 1000  # Convert to milliseconds

        print(f"  Average detection time: {avg_time:.1f}ms")
        performance_ok = avg_time < 200  # Should be under 200ms
        status = "✅" if performance_ok else "❌"
        print(f"  Performance target (<200ms): {status}")

        self.test_results.append({
            'category': 'Performance',
            'test': 'Detection speed',
            'success': performance_ok
        })

        print()

    def _run_detection_test(self, test_num: int, test_case: dict, prefix: str = "") -> bool:
        """Run a single PII detection test"""
        text = test_case['text']
        expected = test_case['expected']
        description = test_case['description']

        has_pii, types, details = self.detector.check_for_pii(text)

        # Check if result matches expectation
        success = (has_pii == expected)

        # For positive cases, also check if expected types are found
        if expected and 'expected_types' in test_case:
            expected_types = test_case['expected_types']
            # Check if at least one expected type is found
            type_match = any(exp_type in str(types).upper() for exp_type in expected_types)
            success = success and type_match

        status = "✅" if success else "❌"
        test_label = f"{prefix}{test_num}" if prefix else str(test_num)

        print(f"  {test_label}. {description}: {status}")

        if has_pii:
            print(f"      Detected: {', '.join(types)}")

        if not success:
            print(f"      Expected: {expected}, Got: {has_pii}")
            if expected and 'expected_types' in test_case:
                print(f"      Expected types: {test_case['expected_types']}")

        return success

    def _show_summary(self):
        """Show test results summary"""
        print("📊 Test Results Summary:")
        print("=" * 30)

        # Group results by category
        categories = {}
        for result in self.test_results:
            category = result['category']
            if category not in categories:
                categories[category] = {'total': 0, 'passed': 0}
            categories[category]['total'] += 1
            if result['success']:
                categories[category]['passed'] += 1

        total_tests = len(self.test_results)
        total_passed = sum(1 for r in self.test_results if r['success'])

        for category, stats in categories.items():
            passed = stats['passed']
            total = stats['total']
            percentage = (passed / total * 100) if total > 0 else 0
            print(f"{category}: {passed}/{total} ({percentage:.1f}%)")

        print("-" * 30)
        overall_percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0
        print(f"Overall: {total_passed}/{total_tests} ({overall_percentage:.1f}%)")

        if overall_percentage >= 90:
            print("🎉 Excellent! System is working well.")
        elif overall_percentage >= 80:
            print("👍 Good! System is mostly functional.")
        elif overall_percentage >= 70:
            print("⚠️ Warning: Some issues detected.")
        else:
            print("❌ Critical: Many tests failing.")

def main():
    """Run the complete test suite"""
    test_suite = PIITestSuite()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()