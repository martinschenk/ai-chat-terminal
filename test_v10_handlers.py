#!/usr/bin/env python3
"""
Test v10.1.0 Handlers - ULTRA KISS + Llama 3.2!
"""

import os
import sys

# Add current dir to path
sys.path.insert(0, os.path.expanduser('~/.aichat'))

from llama_data_extractor import LlamaDataExtractor
from action_detector import ActionDetector
from lang_manager import LangManager
from db_actions.save_handler_v10 import SaveHandler
from db_actions.retrieve_handler_v10 import RetrieveHandler
from db_actions.delete_handler_v10 import DeleteHandler
from db_actions.list_handler_v10 import ListHandler

# Setup
config_dir = os.path.expanduser('~/.aichat')
db_path = os.path.join(config_dir, 'memory.db')

llama = LlamaDataExtractor()
detector = ActionDetector(config_dir, 'de')
lang = LangManager(config_dir, 'de')

save_handler = SaveHandler(db_path, llama, lang)
retrieve_handler = RetrieveHandler(db_path, llama, lang)
delete_handler = DeleteHandler(db_path, llama, lang)
list_handler = ListHandler(db_path, llama, lang)  # NOW uses Llama 3.2 for filtering!

print("🧪 Testing v10.1.0 Handlers (Llama 3.2)\n")
print("=" * 60)

# Test SAVE
print("\n1️⃣  SAVE Test")
action = detector.detect("speichere meine Email test@v10.com")
print(f"Action detected: {action}")
if action == 'SAVE':
    response, _ = save_handler.handle("speichere meine Email test@v10.com")
    print(f"Response: {response}")

# Test LIST
print("\n2️⃣  LIST Test")
action = detector.detect("zeig alle daten")
print(f"Action detected: {action}")
if action == 'LIST':
    response, _ = list_handler.handle("zeig alle daten")
    print(f"Response:\n{response}")

# Test RETRIEVE
print("\n3️⃣  RETRIEVE Test")
action = detector.detect("zeig meine email")
print(f"Action detected: {action}")
if action == 'RETRIEVE':
    response, _ = retrieve_handler.handle("zeig meine email")
    print(f"Response: {response}")

# Test DELETE
print("\n4️⃣  DELETE Test")
action = detector.detect("lösche meine email")
print(f"Action detected: {action}")
if action == 'DELETE':
    response, _ = delete_handler.handle("lösche meine email")
    print(f"Response: {response}")

# Verify deleted
print("\n5️⃣  VERIFY Deleted")
response, _ = retrieve_handler.handle("zeig meine email")
print(f"Response: {response}")

print("\n" + "=" * 60)
print("✅ Tests complete!")
