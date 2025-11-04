#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pytest configuration and fixtures for AI Chat Terminal tests
"""

import os
import sys
import sqlite3
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))


# ============================================================================
# FIXTURES: Test Directories
# ============================================================================

@pytest.fixture
def temp_config_dir(tmp_path):
    """
    Create temporary .aichat config directory with lang files

    Returns:
        Path to temporary config directory
    """
    config_dir = tmp_path / ".aichat"
    config_dir.mkdir()

    # Create lang directory
    lang_dir = config_dir / "lang"
    lang_dir.mkdir()

    # Copy language files from project
    project_lang_dir = Path(__file__).parent.parent / "lang"
    if project_lang_dir.exists():
        for lang_file in project_lang_dir.glob("*.conf"):
            shutil.copy(lang_file, lang_dir / lang_file.name)

    return config_dir


@pytest.fixture
def temp_db_path(tmp_path):
    """
    Create temporary database path

    Returns:
        Path to temporary database file
    """
    return tmp_path / "test_memory.db"


# ============================================================================
# FIXTURES: Mock Encryption
# ============================================================================

@pytest.fixture
def mock_encryption_key():
    """
    Generate mock encryption key (256-bit)

    Returns:
        Hex-encoded 64-character key
    """
    return "a" * 64  # Simple test key (32 bytes = 64 hex chars)


@pytest.fixture
def mock_keychain():
    """
    Mock macOS Keychain operations

    Yields:
        Mock object with get/set/delete methods
    """
    keychain = Mock()
    keychain.key_storage = {}  # In-memory key storage

    def get_key(service, account):
        return keychain.key_storage.get(f"{service}:{account}")

    def save_key(service, account, key):
        keychain.key_storage[f"{service}:{account}"] = key
        return True

    def delete_key(service, account):
        key = f"{service}:{account}"
        if key in keychain.key_storage:
            del keychain.key_storage[key]
        return True

    keychain.get_key = get_key
    keychain.save_key = save_key
    keychain.delete_key = delete_key

    yield keychain


# ============================================================================
# FIXTURES: Database Instances
# ============================================================================

@pytest.fixture
def memory_system(temp_db_path):
    """
    Create ChatMemorySystem instance with temporary database

    Args:
        temp_db_path: Temporary database path fixture

    Returns:
        ChatMemorySystem instance
    """
    from memory_system import ChatMemorySystem

    # Use sqlite3 (not encrypted) for testing simplicity
    memory = ChatMemorySystem(db_path=temp_db_path, encryption_key=None)

    yield memory

    # Cleanup
    memory.close()
    if temp_db_path.exists():
        temp_db_path.unlink()


@pytest.fixture
def memory_system_with_data(memory_system):
    """
    ChatMemorySystem with pre-populated test data

    Args:
        memory_system: Base memory system fixture

    Returns:
        ChatMemorySystem with test data
    """
    # Add test data
    test_data = [
        ("test@test.com", "email", "en"),
        ("669686832", "phone", "es"),
        ("Secret123", "password", "en"),
        ("Hiruela 3, 7-5", "address", "es"),
        ("15/03/1990", "birthday", "de"),
    ]

    for content, meta, lang in test_data:
        memory_system.save_data(content, meta, lang)

    return memory_system


# ============================================================================
# FIXTURES: Component Instances
# ============================================================================

@pytest.fixture
def encryption_manager(mock_keychain):
    """
    Create EncryptionManager instance with mocked Keychain

    Args:
        mock_keychain: Mocked Keychain fixture

    Returns:
        EncryptionManager instance
    """
    from encryption_manager import EncryptionManager

    manager = EncryptionManager()

    # Patch Keychain operations
    def mock_save_key(key):
        return mock_keychain.save_key(
            manager.KEYCHAIN_SERVICE,
            manager.KEYCHAIN_ACCOUNT,
            key
        )

    def mock_get_key():
        return mock_keychain.get_key(
            manager.KEYCHAIN_SERVICE,
            manager.KEYCHAIN_ACCOUNT
        )

    def mock_delete_key():
        return mock_keychain.delete_key(
            manager.KEYCHAIN_SERVICE,
            manager.KEYCHAIN_ACCOUNT
        )

    with patch.object(manager, 'save_key_to_keychain', side_effect=mock_save_key):
        with patch.object(manager, 'get_key_from_keychain', side_effect=mock_get_key):
            with patch.object(manager, 'delete_key_from_keychain', side_effect=mock_delete_key):
                yield manager


# ============================================================================
# FIXTURES: Cleanup Helpers
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_env():
    """
    Cleanup environment variables after each test
    """
    yield

    # Reset environment variables that might have been set during tests
    env_vars = ['PYTHONWARNINGS', 'AICHAT_CONFIG_DIR']
    for var in env_vars:
        if var in os.environ:
            del os.environ[var]


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
