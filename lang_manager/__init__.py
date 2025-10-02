#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Language Manager Package
Centralized multilingual string management
Loads and formats strings from lang/*.conf files
"""

import os
import re

class LangManager:
    """Centralized language string management"""

    def __init__(self, config_dir: str, language: str = 'en'):
        """
        Initialize language manager

        Args:
            config_dir: Configuration directory containing lang/ folder
            language: Language code (de, en, es, etc.)
        """
        self.config_dir = config_dir
        self.language = language
        self.lang_dir = os.path.join(config_dir, 'lang')
        self.strings = self._load_language_file(language)

    def _load_language_file(self, language: str) -> dict:
        """
        Load language file from lang/*.conf

        Args:
            language: Language code

        Returns:
            Dictionary of key-value pairs

        Raises:
            FileNotFoundError: If language file not found
        """
        lang_file = os.path.join(self.lang_dir, f"{language}.conf")

        if not os.path.exists(lang_file):
            # Fallback to English if language not found
            print(f"⚠️  Language file {language}.conf not found, falling back to en.conf")
            lang_file = os.path.join(self.lang_dir, "en.conf")

            if not os.path.exists(lang_file):
                raise FileNotFoundError(f"No language files found in {self.lang_dir}")

        strings = {}

        with open(lang_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                # Parse key="value" format
                match = re.match(r'^(\w+)="(.+)"$', line)
                if match:
                    key, value = match.groups()
                    strings[key] = value

        return strings

    def get(self, key: str, default: str = None) -> str:
        """
        Get translated string by key

        Args:
            key: String key
            default: Default value if key not found

        Returns:
            Translated string or default
        """
        value = self.strings.get(key)

        if value is None:
            if default:
                return default
            else:
                # Return key in brackets to show it's missing
                return f"[Missing: {key}]"

        return value

    def format(self, key: str, **kwargs) -> str:
        """
        Get and format string with variables

        Args:
            key: String key
            **kwargs: Variables to substitute in template

        Returns:
            Formatted string

        Example:
            lang.format('msg_delete_confirmation', count=5, target='Email')
            → "5 Email-Einträge wurden gelöscht"
        """
        template = self.get(key)

        # Simple {var} replacement
        result = template
        for var_key, var_value in kwargs.items():
            result = result.replace(f"{{{var_key}}}", str(var_value))

        return result

    def reload(self, language: str = None):
        """
        Reload language file

        Args:
            language: New language code (optional, uses current if not provided)
        """
        if language:
            self.language = language

        self.strings = self._load_language_file(self.language)
