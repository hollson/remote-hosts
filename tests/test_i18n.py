#!/usr/bin/env python3
"""Tests for internationalization."""

import pytest
from remote_hosts.i18n import _, get_system_language, TEXT, LANG


class TestI18n:
    """Test cases for internationalization."""

    def test_get_system_language_returns_valid_lang(self):
        """Test get_system_language returns valid language code."""
        lang = get_system_language()
        assert lang in ["zh", "en"]

    def test_translation_function_exists(self):
        """Test translation function exists and works."""
        # Test with a known key
        result = _("header_id")
        assert result in ["ID", "主机"]

    def test_translation_with_kwargs(self):
        """Test translation with format arguments."""
        result = _("connecting", user="root", host="test.com", port=22)
        assert "root" in result
        assert "test.com" in result
        assert "22" in result

    def test_translation_missing_key(self):
        """Test translation returns key for missing translation."""
        result = _("nonexistent_key_xyz")
        assert result == "nonexistent_key_xyz"

    def test_text_dict_structure(self):
        """Test TEXT dictionary has expected structure."""
        assert "zh" in TEXT
        assert "en" in TEXT
        # Both should have same keys
        zh_keys = set(TEXT["zh"].keys())
        en_keys = set(TEXT["en"].keys())
        assert zh_keys == en_keys
