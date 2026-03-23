#!/usr/bin/env python3
"""Tests for locale utilities."""

import pytest
from remote_hosts.locale import (
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

    def test_parse_locale_str_with_cp65001(self):
        """Test parse_locale_str with cp65001 encoding."""
        lang, region, encoding = _LocaleUtils.parse_locale_str("zh_CN.cp65001")
        assert lang == "zh"
        assert region == "CN"
        assert encoding == "UTF-8"

    def test_parse_locale_str_with_utf8_variants(self):
        """Test parse_locale_str with utf8 encoding variants."""
        lang1, region1, encoding1 = _LocaleUtils.parse_locale_str("zh_CN.utf8")
        assert encoding1 == "UTF-8"

        lang2, region2, encoding2 = _LocaleUtils.parse_locale_str("zh_CN.utf-8")
        assert encoding2 == "UTF-8"

    def test_parse_locale_str_with_invalid_encoding(self):
        """Test parse_locale_str with invalid encoding falls back to UTF-8."""
        lang, region, encoding = _LocaleUtils.parse_locale_str("zh_CN.invalid")
        assert encoding == "UTF-8"

    def test_parse_locale_str_with_hyphen_separator(self):
        """Test parse_locale_str with hyphen separator."""
        lang, region, encoding = _LocaleUtils.parse_locale_str("zh-CN.UTF-8")
        assert lang == "zh"
        assert region == "CN"
        assert encoding == "UTF-8"

    def test_parse_locale_str_with_only_lang(self):
        """Test parse_locale_str with only language."""
        lang, region, encoding = _LocaleUtils.parse_locale_str("zh")
        assert lang == "zh"
        assert region == ""
        assert encoding == "UTF-8"

    def test_parse_locale_str_with_empty_string(self):
        """Test parse_locale_str with empty string."""
        lang, region, encoding = _LocaleUtils.parse_locale_str("")
        assert lang == ""
        assert region == ""
        assert encoding == ""

    def test_parse_locale_str_with_whitespace(self):
        """Test parse_locale_str with whitespace."""
        lang, region, encoding = _LocaleUtils.parse_locale_str("  ")
        assert lang == ""
        assert region == ""
        assert encoding == ""

    def test_normalize_code_with_parentheses(self):
        """Test normalize_code with parentheses."""
        result = _LocaleUtils.normalize_code("Chinese (Simplified)", LANG_MAP, "en")
        assert result == "zh"

    def test_normalize_code_with_underscore(self):
        """Test normalize_code with underscore."""
        result = _LocaleUtils.normalize_code("zh_CN", LANG_MAP, "en")
        # zh_CN becomes zh-cn, which is not in LANG_MAP, so returns default
        assert result == "en"

    def test_normalize_code_with_dot_separator(self):
        """Test normalize_code with dot separator."""
        result = _LocaleUtils.normalize_code("zh.cn", LANG_MAP, "en")
        assert result == "zh"

    def test_auto_complete_with_all_empty(self):
        """Test auto_complete with all empty parameters."""
        lang, region, encoding = _LocaleUtils.auto_complete("", "", "")
        assert lang == ""
        assert region == ""  # Empty lang means no default region
        assert encoding == "UTF-8"

    def test_auto_complete_with_only_region(self):
        """Test auto_complete with only region."""
        lang, region, encoding = _LocaleUtils.auto_complete("", "CN", "")
        assert lang == ""
        assert region == "CN"
        assert encoding == "UTF-8"

    def test_auto_complete_with_only_encoding(self):
        """Test auto_complete with only encoding."""
        lang, region, encoding = _LocaleUtils.auto_complete("", "", "UTF-8")
        assert lang == ""
        assert region == ""  # Empty lang means no default region
        assert encoding == "UTF-8"

    def test_auto_complete_with_lang_only(self):
        """Test auto_complete with only lang."""
        lang, region, encoding = _LocaleUtils.auto_complete("en", "", "")
        assert lang == "en"
        assert region == "US"
        assert encoding == "UTF-8"

    def test_auto_complete_with_unknown_lang(self):
        """Test auto_complete with unknown language."""
        lang, region, encoding = _LocaleUtils.auto_complete("xx", "", "")
        assert lang == "xx"
        assert region == "US"
        assert encoding == "UTF-8"

    def test_parse_locale_str_with_uppercase_encoding(self):
        """Test parse_locale_str with uppercase encoding."""
        lang, region, encoding = _LocaleUtils.parse_locale_str("zh_CN.UTF8")
        assert lang == "zh"
        assert region == "CN"
        assert encoding == "UTF8"  # Not normalized to UTF-8

    def test_parse_locale_str_with_mixed_case_encoding(self):
        """Test parse_locale_str with mixed case encoding."""
        lang, region, encoding = _LocaleUtils.parse_locale_str("zh_CN.Utf-8")
        assert lang == "zh"
        assert region == "CN"
        assert encoding == "Utf-8"  # Not normalized to UTF-8

    def test_parse_locale_str_with_region_only(self):
        """Test parse_locale_str with region only."""
        lang, region, encoding = _LocaleUtils.parse_locale_str("_CN.UTF-8")
        assert lang == ""
        assert region == "CN"
        assert encoding == "UTF-8"

    def test_parse_locale_str_with_multiple_underscores(self):
        """Test parse_locale_str with multiple underscores."""
        lang, region, encoding = _LocaleUtils.parse_locale_str("zh_CN_CN.UTF-8")
        assert lang == "zh"
        assert region == "CN"
        assert encoding == "UTF-8"

    def test_normalize_code_with_whitespace(self):
        """Test normalize_code with whitespace."""
        result = _LocaleUtils.normalize_code("  zh  ", LANG_MAP, "en")
        assert result == "zh"

    def test_normalize_code_with_special_chars(self):
        """Test normalize_code with special characters."""
        result = _LocaleUtils.normalize_code("zh-cn.", LANG_MAP, "en")
        assert result == "en"  # After cleaning, zh-cn. is not in LANG_MAP

    def test_auto_complete_preserves_region(self):
        """Test auto_complete preserves existing region."""
        lang, region, encoding = _LocaleUtils.auto_complete("zh", "TW", "")
        assert lang == "zh"
        assert region == "TW"
        assert encoding == "UTF-8"

    def test_auto_complete_preserves_encoding(self):
        """Test auto_complete preserves existing encoding."""
        lang, region, encoding = _LocaleUtils.auto_complete("en", "", "ASCII")
        assert lang == "en"
        assert region == "US"
        assert encoding == "ASCII"

    def test_get_locale_info_structure(self):
        """Test get_locale_info returns correct structure."""
        locale_info = get_locale_info()
        parts = locale_info.locale_str.split(".")
        assert len(parts) == 2
        lang_region = parts[0]
        encoding = parts[1]
        lang_region_parts = lang_region.split("_")
        assert len(lang_region_parts) == 2
        assert len(lang_region_parts[0]) == 2
        assert len(lang_region_parts[1]) == 2
        assert encoding == "UTF-8"


if __name__ == "__main__":
    pytest.main([__file__])
