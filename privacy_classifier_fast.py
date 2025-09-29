#!/usr/bin/env python3
"""
AI Chat Terminal - Fast Privacy Classifier
Lightweight classification using E5 embeddings + similarity search
"""

import os
import pickle
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import sys
import time

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError as e:
    print(f"Error: Missing required packages: {e}")
    print("Please run: pip3 install sentence-transformers scikit-learn")
    sys.exit(1)

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
        """Lazy load the E5 model"""
        if self._model is None:
            print("Loading multilingual E5 model...", file=sys.stderr)
            self._model = SentenceTransformer('intfloat/multilingual-e5-small')
        return self._model

    def get_category_examples(self) -> Dict[str, List[str]]:
        """Get representative examples for each category"""
        return {
            'SENSITIVE': [
                "My credit card number is 1234-5678-9012-3456",
                "Password for account: secret123",
                "API key: sk-abc123def456",
                "Meine Kreditkartennummer ist 4532-1234-5678",
                "Passwort für Database: MySecret2023",
                "PIN code is 9876",
                "Social Security Number: 123-45-6789",
                "Mi número de tarjeta es 5555-4444-3333",
                "Contraseña del sistema: Clave2023",
                "OAuth token: bearer_EXAMPLE_TOKEN"
            ],
            'PROPRIETARY': [
                "Our Q2 product launch is planned for June",
                "Internal workflow has 3 escalation stages",
                "Company revenue target for 2025 is $5M",
                "Proprietary algorithm improves efficiency by 23%",
                "Unser interner Workflow hat 3 Eskalationsstufen",
                "Firmeninterne Kostenkalkulation für Projekt Z",
                "Vertrauliche Kundenliste enthält 500 Accounts",
                "El presupuesto interno del departamento es 200K",
                "Estrategia comercial confidencial para mercado",
                "Business merger discussions with ABC Corp"
            ],
            'PERSONAL': [
                "My uncle lives in Seattle and loves fishing",
                "Daughter's soccer game is this Saturday",
                "Personal reminder: buy groceries for dinner",
                "Mein Onkel Hans wohnt in München",
                "Zahnarzttermin ist am Freitag um 14:00",
                "Persönliche Notiz: Geburtstag meiner Mutter",
                "Mi hermano vive en Barcelona con familia",
                "Cita médica el lunes a las 10:30",
                "Friend Mike recommended this restaurant",
                "Family vacation planned for August"
            ],
            'PUBLIC': [
                "What's the capital of Japan?",
                "Explain quantum physics concepts",
                "How do solar panels work?",
                "When did World War II end?",
                "Wie ist das Wetter heute in Berlin?",
                "Wann wurde Mozart geboren?",
                "Was ist die Hauptstadt von Frankreich?",
                "¿Cuál es la fórmula del agua?",
                "¿Cuándo fue la Revolución Francesa?",
                "Convert 100 Fahrenheit to Celsius"
            ]
        }

    def train_fast(self, force_retrain: bool = False) -> bool:
        """Create embeddings for category examples (very fast)"""
        try:
            # Check if embeddings already exist
            if self.embeddings_path.exists() and not force_retrain:
                print("Loading existing category embeddings...", file=sys.stderr)
                with open(self.embeddings_path, 'rb') as f:
                    self.category_embeddings = pickle.load(f)
                self.is_trained = True
                return True

            print("Creating category embeddings (fast training)...", file=sys.stderr)
            start_time = time.time()

            examples = self.get_category_examples()
            self.category_embeddings = {}

            for category, texts in examples.items():
                # Get embeddings for all examples in this category
                embeddings = self.model.encode(texts)
                # Store mean embedding as category prototype
                self.category_embeddings[category] = np.mean(embeddings, axis=0)

            # Save embeddings
            self.config_dir.mkdir(exist_ok=True)
            with open(self.embeddings_path, 'wb') as f:
                pickle.dump(self.category_embeddings, f)

            training_time = time.time() - start_time
            print(f"Fast training completed in {training_time:.2f} seconds!", file=sys.stderr)
            self.is_trained = True
            return True

        except Exception as e:
            print(f"Error in fast training: {e}", file=sys.stderr)
            return False

    def classify_privacy(self, text: str) -> Tuple[str, float]:
        """
        Classify text into privacy category using similarity
        Returns: (category_name, confidence_score)
        """
        if not self.is_trained:
            if not self.train_fast():
                return self._fallback_classify(text)

        try:
            # Get embedding for input text
            text_embedding = self.model.encode([text])[0]

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

            return best_category, confidence

        except Exception as e:
            print(f"Error in privacy classification: {e}", file=sys.stderr)
            return self._fallback_classify(text)

    def _fallback_classify(self, text: str) -> Tuple[str, float]:
        """Keyword-based fallback classification"""
        text_lower = text.lower()

        # Sensitive keywords (multilingual)
        sensitive_keywords = [
            'kreditkarte', 'credit card', 'tarjeta', 'password', 'passwort', 'contraseña',
            'pin', 'api', 'token', 'key', 'schlüssel', 'telefonnummer', 'phone', 'teléfono',
            'iban', 'account', 'konto', 'cuenta', 'social security', 'bitcoin', 'wallet'
        ]

        # Proprietary keywords
        proprietary_keywords = [
            'firma', 'company', 'empresa', 'internal', 'intern', 'workflow', 'business',
            'confidential', 'vertraulich', 'confidencial', 'proprietary', 'strategy',
            'strategie', 'revenue', 'umsatz', 'client', 'kunde', 'customer'
        ]

        # Personal keywords
        personal_keywords = [
            'familie', 'family', 'familia', 'freund', 'friend', 'amigo', 'onkel', 'uncle',
            'tío', 'termin', 'appointment', 'cita', 'persönlich', 'personal', 'geburtstag',
            'birthday', 'cumpleaños'
        ]

        # Check patterns (highest priority first)
        for keyword in sensitive_keywords:
            if keyword in text_lower:
                return 'SENSITIVE', 0.8

        for keyword in proprietary_keywords:
            if keyword in text_lower:
                return 'PROPRIETARY', 0.7

        for keyword in personal_keywords:
            if keyword in text_lower:
                return 'PERSONAL', 0.7

        return 'PUBLIC', 0.6

    def detect_intent(self, text: str) -> Tuple[str, float]:
        """Detect STORAGE vs QUERY intent"""
        text_lower = text.lower()

        storage_patterns = [
            # German
            'speichere', 'merke dir', 'notiere', 'schreibe auf', 'behalte', 'ist', 'bin', 'heißt', 'lautet',
            # English
            'save', 'remember', 'note', 'store', 'keep', 'is', 'am', 'called', 'my',
            # Spanish
            'guarda', 'recuerda', 'apunta', 'almacena', 'es', 'soy', 'se llama', 'mi'
        ]

        query_patterns = [
            # German
            'wie ist', 'was ist', 'zeige', 'gib mir', 'welche', 'was weißt du', 'erkläre',
            # English
            'what is', 'how is', 'show me', 'give me', 'which', 'what do you know', 'explain',
            # Spanish
            'qué es', 'cómo es', 'muestra', 'dame', 'cuál', 'qué sabes', 'explica'
        ]

        delete_patterns = [
            # German
            'lösche', 'entferne', 'vergiss', 'löschen', 'entfernen', 'vergessen', 'delete',
            # English
            'delete', 'remove', 'forget', 'clear', 'erase',
            # Spanish
            'elimina', 'borra', 'olvida', 'borrar', 'eliminar'
        ]

        storage_score = sum(1 for pattern in storage_patterns if pattern in text_lower)
        query_score = sum(1 for pattern in query_patterns if pattern in text_lower)
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