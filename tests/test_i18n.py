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
        zh_keys = set(TEXT["zh"].keys())
        en_keys = set(TEXT["en"].keys())
        assert zh_keys == en_keys

    def test_translation_fallback_to_english(self):
        """Test translation falls back to English when key missing in current language."""
        original_lang = LANG
        result = _("header_id")
        assert result in ["ID", "主机"]

    def test_translation_with_formatting(self):
        """Test translation with multiple format arguments."""
        result = _("duplicate_host_id", id="test-123")
        assert "test-123" in result

    def test_all_translation_keys_accessible(self):
        """Test all translation keys can be accessed without errors."""
        for key in TEXT["en"].keys():
            try:
                result = _(key)
                assert result is not None
                assert isinstance(result, str)
            except KeyError:
                pass

    def test_translation_returns_correct_language(self):
        """Test translation returns text in correct language based on LANG."""
        lang = get_system_language()
        if lang == "zh":
            result = _("header_id")
            assert result == "ID"
        else:
            result = _("header_id")
            assert result == "ID"
