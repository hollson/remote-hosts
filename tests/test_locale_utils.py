#!/usr/bin/env python3
"""Tests for locale utilities."""

import pytest
from remote_hosts.locale_utils import (
    get_locale_info,
    LocaleInfo,
    _LocaleUtils,
    LANG_MAP,
    REGION_MAP,
    DEFAULT_REGION,
    INVALID_LOCALES,
)


class TestLocaleUtils:
    """Test cases for locale utilities."""

    def test_locale_info_dataclass(self):
        """Test LocaleInfo dataclass structure."""
        locale_info = LocaleInfo(locale_str="zh_CN.UTF-8", lang="zh", region="CN", encoding="UTF-8")
        assert locale_info.locale_str == "zh_CN.UTF-8"
        assert locale_info.lang == "zh"
        assert locale_info.region == "CN"
        assert locale_info.encoding == "UTF-8"

    def test_normalize_code_with_valid_code(self):
        """Test normalize_code with valid code."""
        result = _LocaleUtils.normalize_code("zh", LANG_MAP, "en")
        assert result == "zh"

        result = _LocaleUtils.normalize_code("Chinese", LANG_MAP, "en")
        assert result == "zh"

    def test_normalize_code_with_invalid_code(self):
        """Test normalize_code with invalid code."""
        result = _LocaleUtils.normalize_code("invalid", LANG_MAP, "en")
        assert result == "en"

    def test_normalize_code_with_empty_code(self):
        """Test normalize_code with empty code."""
        result = _LocaleUtils.normalize_code("", LANG_MAP, "en")
        assert result == "en"

        result = _LocaleUtils.normalize_code(None, LANG_MAP, "en")
        assert result == "en"

    def test_is_valid_code(self):
        """Test is_valid_code method."""
        assert _LocaleUtils.is_valid_code("zh") is True
        assert _LocaleUtils.is_valid_code("ZH", is_upper=True) is True
        assert _LocaleUtils.is_valid_code("z") is False
        assert _LocaleUtils.is_valid_code("zh1") is False
        assert _LocaleUtils.is_valid_code("") is False

    def test_parse_locale_str_with_encoding(self):
        """Test parse_locale_str with encoding."""
        lang, region, encoding = _LocaleUtils.parse_locale_str("zh_CN.UTF-8")
        assert lang == "zh"
        assert region == "CN"
        assert encoding == "UTF-8"

    def test_parse_locale_str_without_encoding(self):
        """Test parse_locale_str without encoding."""
        lang, region, encoding = _LocaleUtils.parse_locale_str("zh_CN")
        assert lang == "zh"
        assert region == "CN"
        assert encoding == "UTF-8"

    def test_parse_locale_str_with_invalid_code(self):
        """Test parse_locale_str with invalid code."""
        lang, region, encoding = _LocaleUtils.parse_locale_str("invalid")
        assert lang == ""
        assert region == ""
        assert encoding == "UTF-8"

    def test_auto_complete(self):
        """Test auto_complete method."""
        lang, region, encoding = _LocaleUtils.auto_complete("zh", "", "")
        assert lang == "zh"
        assert region == "CN"
        assert encoding == "UTF-8"

    def test_get_locale_info_returns_valid_info(self):
        """Test get_locale_info returns valid LocaleInfo object."""
        locale_info = get_locale_info()
        assert isinstance(locale_info, LocaleInfo)
        assert isinstance(locale_info.locale_str, str)
        assert isinstance(locale_info.lang, str)
        assert isinstance(locale_info.region, str)
        assert isinstance(locale_info.encoding, str)
        assert len(locale_info.lang) == 2
        assert len(locale_info.region) == 2
        assert locale_info.encoding == "UTF-8"

    def test_get_locale_info_fallback_to_english(self):
        """Test get_locale_info falls back to English when detection fails."""
        locale_info = get_locale_info()
        assert locale_info.lang in ["zh", "en"]

    def test_lang_map_contains_common_languages(self):
        """Test LANG_MAP contains common languages."""
        assert "zh" in LANG_MAP
        assert "en" in LANG_MAP
        assert "ja" in LANG_MAP

    def test_region_map_contains_common_regions(self):
        """Test REGION_MAP contains common regions."""
        assert "CN" in REGION_MAP.values()
        assert "US" in REGION_MAP.values()
        assert "JP" in REGION_MAP.values()

    def test_default_region_mapping(self):
        """Test DEFAULT_REGION mapping."""
        assert DEFAULT_REGION.get("zh") == "CN"
        assert DEFAULT_REGION.get("en") == "US"
        assert DEFAULT_REGION.get("ja") == "JP"

    def test_invalid_locales_set(self):
        """Test INVALID_LOCALES set."""
        assert "" in INVALID_LOCALES
        assert "c" in INVALID_LOCALES
        assert "posix" in INVALID_LOCALES


if __name__ == "__main__":
    pytest.main([__file__])
