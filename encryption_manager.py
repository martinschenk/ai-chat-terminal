#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Chat Terminal - Encryption Manager
Manages database encryption keys via macOS Keychain
"""

import os
import sys
import subprocess
from typing import Optional

class EncryptionManager:
    """Manages encryption keys for SQLCipher database"""

    # Keychain configuration
    KEYCHAIN_SERVICE = "AI Chat Terminal DB"
    KEYCHAIN_ACCOUNT = "encryption-key"

    def __init__(self):
        """Initialize encryption manager"""
        self.key_length = 32  # 256 bits

    def is_encryption_available(self) -> bool:
        """
        Check if SQLCipher is available for encryption

        Returns:
            True if sqlcipher3 module can be imported
        """
        try:
            import sqlcipher3
            return True
        except ImportError:
            return False

    def generate_key(self) -> str:
        """
        Generate cryptographically secure random key

        Returns:
            Hex-encoded 256-bit key
        """
        random_bytes = os.urandom(self.key_length)
        return random_bytes.hex()

    def save_key_to_keychain(self, key: str) -> bool:
        """
        Save encryption key to macOS Keychain

        Args:
            key: Hex-encoded encryption key

        Returns:
            True if successful, False otherwise
        """
        try:
            # First, try to delete existing key (if any)
            subprocess.run([
                'security', 'delete-generic-password',
                '-s', self.KEYCHAIN_SERVICE,
                '-a', self.KEYCHAIN_ACCOUNT
            ], capture_output=True, text=True)

            # Add new key to Keychain
            result = subprocess.run([
                'security', 'add-generic-password',
                '-s', self.KEYCHAIN_SERVICE,
                '-a', self.KEYCHAIN_ACCOUNT,
                '-w', key,
                '-U'  # Update if exists
            ], capture_output=True, text=True, timeout=5)

            if result.returncode == 0:
                return True
            else:
                print(f"Error saving key to Keychain: {result.stderr}", file=sys.stderr)
                return False

        except subprocess.TimeoutExpired:
            print("Error: Keychain operation timed out", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Error saving key to Keychain: {e}", file=sys.stderr)
            return False

    def get_key_from_keychain(self) -> Optional[str]:
        """
        Retrieve encryption key from macOS Keychain

        Returns:
            Hex-encoded key if found, None otherwise
        """
        try:
            result = subprocess.run([
                'security', 'find-generic-password',
                '-s', self.KEYCHAIN_SERVICE,
                '-a', self.KEYCHAIN_ACCOUNT,
                '-w'  # Print password only
            ], capture_output=True, text=True, timeout=5)

            if result.returncode == 0:
                key = result.stdout.strip()
                return key if key else None
            else:
                return None

        except subprocess.TimeoutExpired:
            print("Error: Keychain operation timed out", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Error retrieving key from Keychain: {e}", file=sys.stderr)
            return None

    def get_or_create_key(self) -> Optional[str]:
        """
        Get existing key from Keychain or create new one

        Returns:
            Hex-encoded encryption key, or None if failed
        """
        # Try to get existing key
        key = self.get_key_from_keychain()

        if key:
            return key

        # No key found - generate new one
        print("🔐 Generating new encryption key...", file=sys.stderr)
        key = self.generate_key()

        # Save to Keychain
        if self.save_key_to_keychain(key):
            print("✅ Encryption key saved to Keychain", file=sys.stderr)
            return key
        else:
            print("❌ Failed to save encryption key", file=sys.stderr)
            return None

    def delete_key_from_keychain(self) -> bool:
        """
        Delete encryption key from Keychain (USE WITH CAUTION!)
        This will make encrypted databases permanently inaccessible

        Returns:
            True if successful or key didn't exist, False on error
        """
        try:
            result = subprocess.run([
                'security', 'delete-generic-password',
                '-s', self.KEYCHAIN_SERVICE,
                '-a', self.KEYCHAIN_ACCOUNT
            ], capture_output=True, text=True, timeout=5)

            # Success if deleted or didn't exist
            return result.returncode == 0 or "could not be found" in result.stderr

        except Exception as e:
            print(f"Error deleting key from Keychain: {e}", file=sys.stderr)
            return False

    def verify_key(self, key: str) -> bool:
        """
        Verify key format and length

        Args:
            key: Hex-encoded key to verify

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check if valid hex
            bytes.fromhex(key)
            # Check length (should be 64 hex chars for 32 bytes)
            return len(key) == self.key_length * 2
        except (ValueError, AttributeError):
            return False


def main():
    """Test encryption manager"""
    manager = EncryptionManager()

    print("🔐 Encryption Manager Test\n")

    # Check availability
    print(f"SQLCipher available: {manager.is_encryption_available()}")

    # Get or create key
    key = manager.get_or_create_key()
    if key:
        print(f"✅ Encryption key: {key[:16]}...{key[-16:]}")
        print(f"   Length: {len(key)} hex chars ({len(key)//2} bytes)")
        print(f"   Valid: {manager.verify_key(key)}")
    else:
        print("❌ Failed to get/create encryption key")

    # Test retrieval
    retrieved_key = manager.get_key_from_keychain()
    if retrieved_key:
        print(f"✅ Retrieved key from Keychain")
        print(f"   Keys match: {key == retrieved_key}")
    else:
        print("❌ Failed to retrieve key")


if __name__ == '__main__':
    main()
