#!/usr/bin/env python3
"""
AI Chat Terminal - Fast Privacy Classifier
Lightweight classification using E5 embeddings + similarity search
"""

import os
import warnings

# Suppress ALL warnings for clean operation
warnings.filterwarnings("ignore", category=UserWarning)
os.environ['PYTHONWARNINGS'] = 'ignore::UserWarning'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'  # Prevent tokenizer fork warnings

import pickle
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import sys
import time

try:
    # Suppress warnings during import
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from sentence_transformers import SentenceTransformer
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity
    HAS_AI_MODELS = True
except ImportError:
    # AI models not available - will use pure fallback
    HAS_AI_MODELS = False
    print("Note: AI models not available, using keyword-based classification", file=sys.stderr)

class FastPrivacyClassifier:
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = Path.home() / '.aichat'

        self.config_dir = Path(config_dir)
        self.embeddings_path = self.config_dir / 'privacy_embeddings.pkl'

        # Categories for classification
        self.categories = ['SENSITIVE', 'PROPRIETARY', 'PERSONAL', 'PUBLIC']

        # Lazy load model
        self._model = None
        self.category_embeddings = None
        self.is_trained = False

    @property
    def model(self):
        """Lazy load the MiniLM model for ultra-fast privacy classification"""
        if not HAS_AI_MODELS:
            return None

        if self._model is None:
            try:
                # Suppress any warnings during model loading
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    self._model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            except Exception as e:
                print(f"Warning: Could not load MiniLM model: {e}", file=sys.stderr)
                return None
        return self._model

    def get_category_examples(self) -> Dict[str, List[str]]:
        """Get representative examples for each category - extensive training set"""
        return {
            'SENSITIVE': [
                # Credit Cards - multilingual variations
                "My credit card number is 1234-5678-9012-3456",
                "Meine Kreditkartennummer ist 4532-1234-5678",
                "Mi número de tarjeta es 5555-4444-3333-2222",
                "Visa card ending in 7890",
                "Mastercard PIN: 1234",
                "AMEX Gold Card security code",
                "Die Nummer meiner Bankkarte lautet 4111",
                "Ma carte bancaire se termine par 5678",

                # Passwords - all variations
                "Password for account: secret123",
                "Passwort für Database: MySecret2023",
                "Contraseña del sistema: Clave2023",
                "Admin password is SuperSecret456",
                "Root access: password123",
                "WiFi Passwort: MeinWLAN2023",
                "Login credentials: user/pass123",
                "Server login password",
                "Database access code",

                # API Keys & Tokens
                "API key: sk-abc123def456",
                "OAuth token: bearer_EXAMPLE_TOKEN",
                "Authentication token for service",
                "JWT token: eyJhbGciOiJIUzI1NiIs",
                "Private key for encryption",
                "Secret access key",
                "Google API Schlüssel",
                "GitHub access token",

                # Personal IDs & Numbers
                "Social Security Number: 123-45-6789",
                "Personalausweisnummer: 123456789",
                "Reisepass-Nummer: P12345678",
                "Driver's license: DL123456",
                "Steuerliche Identifikationsnummer",
                "Número de identificación nacional",
                "Health insurance number",

                # Financial sensitive data
                "IBAN: DE89 3704 0044 0532 0130 00",
                "Bank account number: 1234567890",
                "Kontonummer bei der Sparkasse",
                "Credit score: 750",
                "Bitcoin wallet address",
                "Investment portfolio value",
                "Salary information: €50,000",

                # Access codes & PINs
                "PIN code is 9876",
                "Security code: 123",
                "Verification code from SMS",
                "Two-factor authentication code",
                "Unlock code for phone",
                "Safe combination: 12-34-56",
                "Alarm system code",

                # Biometric & health data
                "Fingerprint scan data",
                "Medical record number",
                "Blood type and allergies",
                "Prescription medication list",
                "Doctor visit notes",
                "Insurance claim number"
            ],
            'PROPRIETARY': [
                # Business strategy & planning
                "Our Q2 product launch is planned for June",
                "Internal workflow has 3 escalation stages",
                "Company revenue target for 2025 is $5M",
                "Proprietary algorithm improves efficiency by 23%",
                "Unser interner Workflow hat 3 Eskalationsstufen",
                "Firmeninterne Kostenkalkulation für Projekt Z",
                "Vertrauliche Kundenliste enthält 500 Accounts",
                "El presupuesto interno del departamento es 200K",
                "Estrategia comercial confidencial para mercado",
                "Business merger discussions with ABC Corp",

                # Internal processes & data
                "Confidential client database access",
                "Internal cost analysis for project",
                "Proprietary source code architecture",
                "Trade secret manufacturing process",
                "Company acquisition strategy",
                "Competitive analysis report",
                "Internal audit findings",
                "Employee salary bands by department",
                "Vendor contract negotiations",
                "Product roadmap for next 3 years",
                "Strategic partnership discussions",
                "Board meeting confidential agenda",

                # Intellectual property
                "Patent application draft",
                "Copyright protected content",
                "Trademark registration process",
                "Proprietary research methodology",
                "Internal innovation pipeline",
                "R&D budget allocation",
                "Technical specifications confidential",
                "Internal training materials",
                "Company policy drafts",
                "Legal strategy discussion"
            ],
            'PERSONAL': [
                # Names & identity
                "My name is Martin Schenk",
                "Mein Name ist Hans Mueller",
                "Mi nombre es Carlos Rodriguez",
                "I am called Sarah Johnson",
                "Ich heiße Anna Schmidt",
                "Me llamo María García",

                # Family & relationships
                "My uncle lives in Seattle and loves fishing",
                "Daughter's soccer game is this Saturday",
                "Mein Onkel Hans wohnt in München",
                "Mi hermano vive en Barcelona con familia",
                "Friend Mike recommended this restaurant",
                "Family vacation planned for August",
                "My wife works as a teacher",
                "Meine Schwester ist Ärztin",
                "Wife's birthday is next month",
                "Kids go to elementary school",

                # Personal appointments & activities
                "Personal reminder: buy groceries for dinner",
                "Zahnarzttermin ist am Freitag um 14:00",
                "Persönliche Notiz: Geburtstag meiner Mutter",
                "Cita médica el lunes a las 10:30",
                "Dentist appointment on Tuesday",
                "Gym session at 6 PM today",
                "Personal trainer meeting",
                "Hair salon appointment",
                "Birthday party this weekend",
                "Anniversary dinner reservation",

                # Personal preferences & hobbies
                "I love playing guitar in my free time",
                "Mein Hobby ist Fotografieren",
                "Me gusta cocinar los fines de semana",
                "Personal favorite movie is Inception",
                "I prefer coffee over tea",
                "Personal workout routine",
                "Favorite restaurant downtown",
                "Personal reading list",
                "Weekend hobby projects",
                "Personal music playlist"
            ],
            'PUBLIC': [
                # General knowledge questions
                "What's the capital of Japan?",
                "Explain quantum physics concepts",
                "How do solar panels work?",
                "When did World War II end?",
                "When was Beethoven born?",
                "When was Einstein born?",
                "When was Shakespeare born?",
                "When was the Declaration of Independence signed?",
                "When was the internet invented?",
                "When was the first computer built?",
                "Wie ist das Wetter heute in Berlin?",
                "Wann wurde Mozart geboren?",
                "Wann wurde Newton geboren?",
                "wann wurde beethoven geboren?",
                "wann wurde mozart geboren?",
                "wann wurde einstein geboren?",
                "Wann wurde Shakespeare geboren?",
                "wann wurde shakespeare geboren?",
                "Wann wurde Napoleon geboren?",
                "wann wurde napoleon geboren?",
                "When was Caesar born?",
                "When was Da Vinci born?",
                "When was Galileo born?",
                "Was ist die Hauptstadt von Frankreich?",
                "¿Cuál es la fórmula del agua?",
                "¿Cuándo fue la Revolución Francesa?",
                "¿Cuándo nació Cervantes?",
                "Convert 100 Fahrenheit to Celsius",

                # Educational & informational
                "How does photosynthesis work?",
                "Explain the theory of relativity",
                "What are the benefits of renewable energy?",
                "History of the Roman Empire",
                "How to cook pasta properly",
                "Basic principles of economics",
                "Famous landmarks in Europe",
                "How to learn a new language",
                "Benefits of exercise and fitness",
                "Climate change explained",

                # Technical & programming questions
                "How to center a div in CSS?",
                "Python vs JavaScript comparison",
                "What is machine learning?",
                "Database design best practices",
                "How does the internet work?",
                "Difference between HTTP and HTTPS",
                "What is cloud computing?",
                "Introduction to blockchain technology",
                "How to debug code effectively",
                "Version control with Git",

                # General assistance requests
                "Can you help me write an email?",
                "How to organize my schedule?",
                "Tips for better productivity",
                "Recommend a good book to read",
                "How to maintain work-life balance?",
                "Healthy meal planning ideas",
                "Travel tips for Europe",
                "How to start learning guitar?",
                "Photography techniques for beginners",
                "Public speaking tips and advice"
            ]
        }

    def train_fast(self, force_retrain: bool = False) -> bool:
        """Create embeddings for category examples using E5 model"""
        try:
            # Check if AI models are available
            if not HAS_AI_MODELS or self.model is None:
                self.is_trained = True
                return True

            # Check if embeddings already exist
            if self.embeddings_path.exists() and not force_retrain:
                with open(self.embeddings_path, 'rb') as f:
                    self.category_embeddings = pickle.load(f)
                self.is_trained = True
                return True

            # Create embeddings silently
            examples = self.get_category_examples()
            self.category_embeddings = {}

            for category, texts in examples.items():
                # Get embeddings for all examples in this category
                embeddings = self.model.encode(texts, show_progress_bar=False)
                # Store mean embedding as category prototype
                self.category_embeddings[category] = np.mean(embeddings, axis=0)

            # Save embeddings for next time
            self.config_dir.mkdir(exist_ok=True)
            with open(self.embeddings_path, 'wb') as f:
                pickle.dump(self.category_embeddings, f)

            self.is_trained = True
            return True

        except Exception as e:
            # Silent fallback - no user-visible errors
            self.is_trained = True  # Continue with fallback
            return True

    def classify_privacy(self, text: str) -> Tuple[str, float]:
        """
        Classify text into privacy category using AI similarity matching
        Returns: (category_name, confidence_score)
        """
        # Ensure training is complete
        if not self.is_trained:
            if not self.train_fast():
                return self._fallback_classify(text)

        # Try AI-based classification first
        if HAS_AI_MODELS and self.model is not None and self.category_embeddings:
            try:
                # Pre-check: Historical questions should be PUBLIC regardless of similarity
                text_lower = text.lower()
                historical_patterns = ['wann wurde', 'when was', 'when did', 'cuándo nació']
                famous_people = ['beethoven', 'mozart', 'einstein', 'shakespeare', 'napoleon', 'caesar', 'da vinci', 'galileo', 'newton', 'elizabeth strout', 'stephen king', 'j.k. rowling', 'hemingway', 'dickens', 'tolkien', 'george orwell', 'virginia woolf', 'mark twain', 'jane austen', 'agatha christie']
                if any(pattern in text_lower for pattern in historical_patterns) and any(person in text_lower for person in famous_people):
                    return 'PUBLIC', 0.85  # High confidence for obvious historical questions

                # Get embedding for input text
                text_embedding = self.model.encode([text], show_progress_bar=False)[0]

                # Calculate similarities to each category
                similarities = {}
                for category, category_embedding in self.category_embeddings.items():
                    similarity = cosine_similarity(
                        [text_embedding],
                        [category_embedding]
                    )[0][0]
                    similarities[category] = similarity

                # Find best match
                best_category = max(similarities, key=similarities.get)
                confidence = float(similarities[best_category])

                # Normalize confidence to 0-1 range (cosine similarity can be negative)
                confidence = (confidence + 1) / 2

                # High confidence threshold for AI classification
                if confidence > 0.75:
                    return best_category, confidence

                # Special rule: if best category is PUBLIC and it's a historical question, accept lower confidence
                if best_category == 'PUBLIC' and confidence > 0.55:
                    text_lower = text.lower()
                    historical_patterns = ['wann wurde', 'when was', 'when did', 'cuándo nació', 'geboren', 'born']
                    if any(pattern in text_lower for pattern in historical_patterns):
                        return best_category, confidence

                # Medium confidence - still use AI but note lower confidence
                if confidence > 0.60:
                    return best_category, confidence * 0.9  # Slightly reduce confidence

            except Exception as e:
                print(f"Error in AI classification: {e}", file=sys.stderr)

        # Fallback to keyword-based classification (only as backup)
        return self._fallback_classify(text)

    def _fallback_classify(self, text: str) -> Tuple[str, float]:
        """
        Conservative fallback classification (only when AI unavailable)
        Routes everything non-trivial to local processing for safety
        """
        text_lower = text.lower()

        # Only classify obvious public questions - everything else goes local for safety
        # This is very conservative to prevent sensitive data leaks
        obvious_public_patterns = [
            'what is', 'how to', 'explain', 'define', 'calculate', 'convert',
            'was ist', 'wie', 'erkläre', 'definiere', 'rechne', 'konvertiere',
            'qué es', 'cómo', 'explica', 'define', 'calcula', 'convierte'
        ]

        # If it looks like a clear public question
        if any(pattern in text_lower for pattern in obvious_public_patterns):
            return 'PUBLIC', 0.7

        # Everything else gets routed locally for safety (conservative approach)
        # Better safe than sorry when AI classification unavailable
        return 'PERSONAL', 0.8

    def detect_intent(self, text: str) -> Tuple[str, float]:
        """Detect STORAGE vs QUERY intent"""
        text_lower = text.lower()

        storage_patterns = [
            # German - definitive storage indicators
            'speichere', 'merke dir', 'notiere', 'schreibe auf', 'behalte', 'mein.*ist', 'ich bin', 'ich heiße',
            # English - definitive storage indicators
            'save', 'remember', 'note', 'store', 'keep', 'my.*is', 'i am', 'called',
            # Spanish - definitive storage indicators
            'guarda', 'recuerda', 'apunta', 'almacena', 'mi.*es', 'soy', 'me llamo'
        ]

        query_patterns = [
            # German - questions asking for information
            'wie ist mein', 'was ist mein', 'zeige mir', 'gib mir', 'welche.*habe', 'was weißt du über mein',
            # English - questions asking for information
            'what is my', 'how is my', 'show me my', 'give me my', 'which.*do i have', 'what do you know about my',
            # Spanish - questions asking for information
            'qué es mi', 'cómo es mi', 'muestra mi', 'dame mi', 'cuál.*tengo', 'qué sabes de mi'
        ]

        delete_patterns = [
            # German
            'lösche', 'entferne', 'vergiss', 'löschen', 'entfernen', 'vergessen', 'delete',
            # English
            'delete', 'remove', 'forget', 'clear', 'erase',
            # Spanish
            'elimina', 'borra', 'olvida', 'borrar', 'eliminar'
        ]

        import re

        storage_score = sum(1 for pattern in storage_patterns if re.search(pattern, text_lower))
        query_score = sum(1 for pattern in query_patterns if re.search(pattern, text_lower))
        delete_score = sum(1 for pattern in delete_patterns if pattern in text_lower)

        # Check for delete intent first (highest priority)
        if delete_score > 0:
            return 'DELETE', min(0.9, 0.6 + delete_score * 0.1)
        elif storage_score > query_score:
            return 'STORAGE', min(0.9, 0.5 + storage_score * 0.1)
        elif query_score > storage_score:
            return 'QUERY', min(0.9, 0.5 + query_score * 0.1)
        else:
            # Default heuristics
            if '?' in text or text_lower.startswith(('wie', 'was', 'what', 'how', 'qué', 'cómo')):
                return 'QUERY', 0.7
            elif any(pattern in text_lower for pattern in ['ist', 'is', 'es']):
                return 'STORAGE', 0.7
            else:
                return 'QUERY', 0.6

    def should_route_locally(self, text: str, confidence_threshold: float = 0.65) -> Tuple[bool, Dict]:
        """
        Determine routing with conservative approach
        Returns: (route_locally, routing_info)
        """
        privacy_category, privacy_confidence = self.classify_privacy(text)
        intent, intent_confidence = self.detect_intent(text)

        # Conservative: route locally for any non-PUBLIC category
        route_locally = privacy_category in ['SENSITIVE', 'PROPRIETARY', 'PERSONAL']

        # Extra conservative: if confidence is low and not clearly PUBLIC, route locally
        if privacy_confidence < confidence_threshold and privacy_category != 'PUBLIC':
            route_locally = True

        routing_info = {
            'privacy_category': privacy_category,
            'privacy_confidence': privacy_confidence,
            'intent': intent,
            'intent_confidence': intent_confidence,
            'route_locally': route_locally,
            'reason': f"Category: {privacy_category} ({privacy_confidence:.2f}), Intent: {intent} ({intent_confidence:.2f})"
        }

        return route_locally, routing_info

def main():
    """Test the fast privacy classifier"""
    classifier = FastPrivacyClassifier()

    # Fast training
    start_time = time.time()
    classifier.train_fast()
    training_time = time.time() - start_time

    # Test examples
    test_cases = [
        "Meine Kreditkartennummer ist 1234-5678",
        "Wie ist das Wetter heute?",
        "Unser interner Workflow hat 3 Stufen",
        "Mein Onkel wohnt in Berlin",
        "What's the capital of France?",
        "Save my password: secret123",
        "API key for service X: abc789",
        "My company's strategy for 2025",
        "Personal note: doctor appointment Friday",
        "Explain quantum physics"
    ]

    print(f"Fast Privacy Classifier (Training: {training_time:.2f}s)")
    print("=" * 60)

    for text in test_cases:
        start_time = time.time()
        route_locally, info = classifier.should_route_locally(text)
        classification_time = time.time() - start_time

        print(f"Text: {text}")
        print(f"Route locally: {route_locally}")
        print(f"Details: {info['reason']}")
        print(f"Classification time: {classification_time*1000:.1f}ms")
        print("-" * 40)

if __name__ == "__main__":
    main()