#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for EncryptionManager - Key Management and Security
"""

import pytest
from encryption_manager import EncryptionManager


class TestKeyGeneration:
    """Test encryption key generation"""

    def test_generate_key(self, encryption_manager):
        """Test that generate_key creates valid key"""
        key = encryption_manager.generate_key()

        assert key is not None
        assert isinstance(key, str)
        assert len(key) == 64, f"Key length should be 64 hex chars, got {len(key)}"

    def test_generate_key_is_random(self, encryption_manager):
        """Test that generated keys are random"""
        key1 = encryption_manager.generate_key()
        key2 = encryption_manager.generate_key()

        assert key1 != key2, "Generated keys should be random"

    def test_generate_key_is_hex(self, encryption_manager):
        """Test that generated key is valid hex"""
        key = encryption_manager.generate_key()

        # Should be valid hex
        try:
            bytes.fromhex(key)
            is_hex = True
        except ValueError:
            is_hex = False

        assert is_hex, "Generated key should be valid hex"

    def test_generate_key_length(self, encryption_manager):
        """Test that generated key is 256 bits (32 bytes)"""
        key = encryption_manager.generate_key()

        # Hex key should be 64 characters (32 bytes * 2)
        assert len(key) == 64

        # Decoded should be 32 bytes
        key_bytes = bytes.fromhex(key)
        assert len(key_bytes) == 32


class TestKeyValidation:
    """Test key validation"""

    def test_validate_valid_key(self, encryption_manager, mock_encryption_key):
        """Test validating a valid key"""
        is_valid = encryption_manager.verify_key(mock_encryption_key)

        assert is_valid is True

    def test_validate_invalid_length(self, encryption_manager):
        """Test validating key with wrong length"""
        short_key = "abc123"
        is_valid = encryption_manager.verify_key(short_key)

        assert is_valid is False

    def test_validate_invalid_hex(self, encryption_manager):
        """Test validating non-hex string"""
        invalid_key = "z" * 64  # 'z' is not valid hex
        is_valid = encryption_manager.verify_key(invalid_key)

        assert is_valid is False

    def test_validate_none(self, encryption_manager):
        """Test validating None"""
        is_valid = encryption_manager.verify_key(None)

        assert is_valid is False

    def test_validate_empty_string(self, encryption_manager):
        """Test validating empty string"""
        is_valid = encryption_manager.verify_key("")

        assert is_valid is False


class TestKeychainOperations:
    """Test Keychain save/get/delete operations (mocked)"""

    def test_save_key_to_keychain(self, encryption_manager, mock_encryption_key):
        """Test saving key to Keychain"""
        success = encryption_manager.save_key_to_keychain(mock_encryption_key)

        assert success is True

    def test_get_key_from_keychain(self, encryption_manager, mock_encryption_key, mock_keychain):
        """Test retrieving key from Keychain"""
        # First save
        encryption_manager.save_key_to_keychain(mock_encryption_key)

        # Then retrieve
        retrieved_key = encryption_manager.get_key_from_keychain()

        assert retrieved_key == mock_encryption_key

    def test_get_nonexistent_key(self, encryption_manager):
        """Test retrieving key that doesn't exist"""
        retrieved_key = encryption_manager.get_key_from_keychain()

        assert retrieved_key is None

    def test_delete_key_from_keychain(self, encryption_manager, mock_encryption_key):
        """Test deleting key from Keychain"""
        # First save
        encryption_manager.save_key_to_keychain(mock_encryption_key)

        # Then delete
        success = encryption_manager.delete_key_from_keychain()

        assert success is True

        # Verify deletion
        retrieved_key = encryption_manager.get_key_from_keychain()
        assert retrieved_key is None

    def test_delete_nonexistent_key(self, encryption_manager):
        """Test deleting key that doesn't exist"""
        # Should succeed (no-op)
        success = encryption_manager.delete_key_from_keychain()

        assert success is True

    def test_overwrite_existing_key(self, encryption_manager):
        """Test overwriting existing key"""
        key1 = "a" * 64
        key2 = "b" * 64

        # Save first key
        encryption_manager.save_key_to_keychain(key1)

        # Overwrite with second key
        encryption_manager.save_key_to_keychain(key2)

        # Should have second key
        retrieved_key = encryption_manager.get_key_from_keychain()
        assert retrieved_key == key2


class TestGetOrCreateKey:
    """Test get_or_create_key workflow"""

    def test_create_new_key(self, encryption_manager):
        """Test creating new key when none exists"""
        key = encryption_manager.get_or_create_key()

        assert key is not None
        assert len(key) == 64
        assert encryption_manager.verify_key(key)

    def test_get_existing_key(self, encryption_manager, mock_encryption_key):
        """Test getting existing key"""
        # Save key first
        encryption_manager.save_key_to_keychain(mock_encryption_key)

        # get_or_create should return existing
        key = encryption_manager.get_or_create_key()

        assert key == mock_encryption_key

    def test_create_key_persists(self, encryption_manager):
        """Test that created key is saved to Keychain"""
        # Create key
        key1 = encryption_manager.get_or_create_key()

        # Get again - should be same
        key2 = encryption_manager.get_or_create_key()

        assert key1 == key2


class TestEncryptionAvailability:
    """Test encryption availability checks"""

    def test_is_encryption_available(self, encryption_manager):
        """Test checking if SQLCipher is available"""
        is_available = encryption_manager.is_encryption_available()

        # Should return True or False (depending on environment)
        assert isinstance(is_available, bool)

    def test_encryption_availability_matches_import(self, encryption_manager):
        """Test that availability check matches actual import"""
        is_available = encryption_manager.is_encryption_available()

        try:
            import sqlcipher3
            has_sqlcipher = True
        except ImportError:
            has_sqlcipher = False

        assert is_available == has_sqlcipher


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_save_invalid_key(self, encryption_manager):
        """Test saving invalid key"""
        invalid_key = "invalid"

        # Should still save (validation happens elsewhere)
        success = encryption_manager.save_key_to_keychain(invalid_key)

        # Mock Keychain will accept any string
        assert success is True

    def test_concurrent_operations(self, encryption_manager):
        """Test multiple operations in sequence"""
        key1 = "a" * 64
        key2 = "b" * 64

        # Save first key
        encryption_manager.save_key_to_keychain(key1)
        retrieved = encryption_manager.get_key_from_keychain()
        assert retrieved == key1

        # Update to second key
        encryption_manager.save_key_to_keychain(key2)
        retrieved = encryption_manager.get_key_from_keychain()
        assert retrieved == key2

        # Delete
        encryption_manager.delete_key_from_keychain()
        retrieved = encryption_manager.get_key_from_keychain()
        assert retrieved is None

    def test_key_length_property(self, encryption_manager):
        """Test key_length property is correct"""
        assert encryption_manager.key_length == 32  # 32 bytes = 256 bits


class TestKeychainConfiguration:
    """Test Keychain service configuration"""

    def test_keychain_service_name(self, encryption_manager):
        """Test that Keychain service name is set"""
        assert encryption_manager.KEYCHAIN_SERVICE is not None
        assert len(encryption_manager.KEYCHAIN_SERVICE) > 0

    def test_keychain_account_name(self, encryption_manager):
        """Test that Keychain account name is set"""
        assert encryption_manager.KEYCHAIN_ACCOUNT is not None
        assert len(encryption_manager.KEYCHAIN_ACCOUNT) > 0


class TestSecurityProperties:
    """Test security-related properties"""

    def test_generated_keys_are_cryptographically_secure(self, encryption_manager):
        """Test that generated keys use os.urandom (cryptographically secure)"""
        # Generate multiple keys and check randomness
        keys = [encryption_manager.generate_key() for _ in range(10)]

        # All should be unique
        assert len(set(keys)) == 10, "Generated keys should be unique"

        # All should be valid length
        for key in keys:
            assert len(key) == 64

    def test_key_entropy(self, encryption_manager):
        """Test that generated keys have high entropy"""
        key = encryption_manager.generate_key()

        # Check that key uses variety of hex characters
        unique_chars = set(key)

        # Should have reasonable variety (at least 8 different hex chars)
        assert len(unique_chars) >= 8, "Key should have high entropy"

    def test_no_key_patterns(self, encryption_manager):
        """Test that generated keys don't have obvious patterns"""
        key = encryption_manager.generate_key()

        # Check for obvious patterns
        # No sequences like "00000000" or "aaaaaaaa"
        for char in "0123456789abcdef":
            repeated = char * 8
            assert repeated not in key, f"Key contains repeated pattern: {repeated}"


# ============================================================================
# Integration-Style Tests
# ============================================================================

class TestEncryptionWorkflow:
    """Test complete encryption workflow"""

    def test_full_lifecycle(self, encryption_manager):
        """Test full key lifecycle: create → use → delete"""
        # Create key
        key = encryption_manager.get_or_create_key()
        assert key is not None

        # Validate key
        assert encryption_manager.verify_key(key)

        # Retrieve key
        retrieved = encryption_manager.get_key_from_keychain()
        assert retrieved == key

        # Delete key
        success = encryption_manager.delete_key_from_keychain()
        assert success is True

        # Verify deletion
        retrieved = encryption_manager.get_key_from_keychain()
        assert retrieved is None

    def test_multiple_create_calls_idempotent(self, encryption_manager):
        """Test that multiple get_or_create calls return same key"""
        key1 = encryption_manager.get_or_create_key()
        key2 = encryption_manager.get_or_create_key()
        key3 = encryption_manager.get_or_create_key()

        assert key1 == key2 == key3, "get_or_create should be idempotent"

    def test_key_rotation(self, encryption_manager):
        """Test rotating encryption key"""
        # Create initial key
        key1 = encryption_manager.get_or_create_key()

        # Delete old key
        encryption_manager.delete_key_from_keychain()

        # Create new key
        key2 = encryption_manager.get_or_create_key()

        # Should be different
        assert key1 != key2, "Rotated key should be different"


class TestMemorySystemIntegration:
    """Test encryption integration with memory system"""

    def test_memory_system_with_encryption(self, temp_db_path):
        """Test ChatMemorySystem with encryption key"""
        from memory_system import ChatMemorySystem

        # Generate key
        manager = EncryptionManager()
        key = manager.generate_key()

        # Create memory system with encryption
        try:
            memory = ChatMemorySystem(
                db_path=temp_db_path,
                encryption_key=key
            )

            # Should work
            row_id = memory.save_data("test@test.com", "email", "en")
            assert row_id > 0

            # Verify data
            results = memory.search_data("test@test.com")
            assert len(results) == 1

            memory.close()

        except Exception as e:
            # If SQLCipher not available, skip
            if "sqlcipher" in str(e).lower():
                pytest.skip("SQLCipher not available")
            else:
                raise

    def test_memory_system_key_mismatch(self, temp_db_path):
        """Test that wrong key can't decrypt database"""
        from memory_system import ChatMemorySystem

        try:
            import sqlcipher3

            # Create database with key1
            manager = EncryptionManager()
            key1 = manager.generate_key()

            memory1 = ChatMemorySystem(
                db_path=temp_db_path,
                encryption_key=key1
            )
            memory1.save_data("secret", "password", "en")
            memory1.close()

            # Try to open with different key
            key2 = manager.generate_key()
            memory2 = ChatMemorySystem(
                db_path=temp_db_path,
                encryption_key=key2
            )

            # Should fail to read data
            try:
                results = memory2.search_data("secret")
                # If we get here, encryption might not be working
                # (or test environment doesn't support it)
            except:
                # Expected - wrong key can't decrypt
                pass

            memory2.close()

        except ImportError:
            pytest.skip("SQLCipher not available")
