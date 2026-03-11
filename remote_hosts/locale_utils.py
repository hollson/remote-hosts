import locale
import os
import platform
from dataclasses import dataclass
from typing import Optional, Tuple

LANG_MAP = {
    "chinese (simplified)": "zh",
    "chinese (traditional)": "zh",
    "chinese": "zh",
    "zh": "zh",
    "chinese simplified": "zh",
    "chinese traditional": "zh",
    "english (united states)": "en",
    "english (united kingdom)": "en",
    "english": "en",
    "en": "en",
    "english united states": "en",
    "english united kingdom": "en",
    "japanese": "ja",
    "ja": "ja",
    "korean": "ko",
    "ko": "ko",
    "french": "fr",
    "fr": "fr",
    "german": "de",
    "de": "de",
    "spanish": "es",
    "es": "es",
    "italian": "it",
    "it": "it",
    "portuguese": "pt",
    "pt": "pt",
    "russian": "ru",
    "ru": "ru",
}

REGION_MAP = {
    "china": "CN",
    "taiwan": "TW",
    "hong kong": "HK",
    "cn": "CN",
    "tw": "TW",
    "hk": "HK",
    "united states": "US",
    "united kingdom": "GB",
    "uk": "GB",
    "us": "US",
    "gb": "GB",
    "japan": "JP",
    "jp": "JP",
    "korea": "KR",
    "kr": "KR",
    "france": "FR",
    "fr": "FR",
    "germany": "DE",
    "de": "DE",
    "spain": "ES",
    "es": "ES",
    "italy": "IT",
    "it": "IT",
    "portugal": "PT",
    "pt": "PT",
    "russia": "RU",
    "ru": "RU",
}

DEFAULT_REGION = {
    "zh": "CN",
    "en": "US",
    "ja": "JP",
    "ko": "KR",
    "fr": "FR",
    "de": "DE",
    "es": "ES",
    "it": "IT",
    "pt": "PT",
    "ru": "RU",
}

INVALID_LOCALES = {"c", "posix", ""}


@dataclass
class LocaleInfo:
    locale_str: str
    lang: str
    region: str
    encoding: str


class _LocaleUtils:
    """Internal utility class for locale handling functions"""

    @staticmethod
    def normalize_code(code: Optional[str], map_dict: dict, default: str) -> str:
        if not code or not code.strip():
            return default
        clean_code = str(code).lower().replace("(", "").replace(")", "").replace("_", "-").strip()
        result = map_dict.get(clean_code, map_dict.get(clean_code.split(".", maxsplit=1)[0], default))
        return str(result)

    @staticmethod
    def is_valid_code(code: str, is_upper: bool = False) -> bool:
        return bool(code) and len(code) == 2 and code.isalpha() and (code.isupper() if is_upper else code.islower())

    @staticmethod
    def parse_locale_str(locale_str: str) -> Tuple[str, str, str]:
        if not locale_str or not locale_str.strip():
            return "", "", ""

        if "." in locale_str:
            lang_region, encoding = locale_str.rsplit(".", 1)
            encoding = encoding.replace("cp65001", "UTF-8").replace("utf8", "UTF-8").replace("utf-8", "UTF-8")
            if encoding.upper() not in ("UTF-8", "UTF8"):
                encoding = "UTF-8"
        else:
            lang_region, encoding = locale_str, "UTF-8"

        lang_region = lang_region.replace("-", "_")
        parts = lang_region.split("_")
        raw_lang = parts[0].strip() if parts else ""
        raw_region = parts[1].strip() if len(parts) >= 2 else ""

        lang = _LocaleUtils.normalize_code(raw_lang, LANG_MAP, "")
        if not _LocaleUtils.is_valid_code(lang, is_upper=False):
            lang = ""

        region = _LocaleUtils.normalize_code(raw_region, REGION_MAP, "")
        if not _LocaleUtils.is_valid_code(region, is_upper=True):
            region = ""

        return lang, region, encoding

    @staticmethod
    def auto_complete(lang: str, region: str, encoding: str) -> Tuple[str, str, str]:
        if not region and lang:
            region = DEFAULT_REGION.get(lang, "US")
        if not encoding:
            encoding = "UTF-8"
        return lang, region, encoding


def get_locale_info() -> LocaleInfo:
    """
    Get standardized system locale information

    Returns a LocaleInfo object containing:
    - locale_str: Full locale string in format lang_region.encoding (e.g., zh_CN.UTF-8)
    - lang: Language code for i18n (e.g., zh)
    - region: Region code for i18n (e.g., CN)
    - encoding: Character encoding (e.g., UTF-8)

    Falls back to en_US.UTF-8 if detection fails
    """
    final_lang, final_region, final_encoding = "en", "US", "UTF-8"
    locale_detected = False

    try:
        env_locale = ""
        for var in ["LC_ALL", "LC_MESSAGES", "LANG", "LANGUAGE"]:
            val = os.environ.get(var, "").strip()
            if val and val.lower() not in INVALID_LOCALES:
                env_locale = val
                break

        if not env_locale:
            apple_locale = os.environ.get("AppleLocale", "").strip()
            if apple_locale and apple_locale.lower() not in INVALID_LOCALES:
                env_locale = apple_locale

        if env_locale:
            lang, region, encoding = _LocaleUtils.parse_locale_str(env_locale)
            if lang:
                if region and encoding:
                    final_lang, final_region, final_encoding = lang, region, encoding
                else:
                    lang, region, encoding = _LocaleUtils.auto_complete(lang, region, encoding)
                    final_lang, final_region, final_encoding = lang, region, encoding
                locale_detected = True
    except Exception:
        pass

    if not locale_detected:
        system = platform.system()
        if system == "Windows":
            locale_name = _get_windows_locale_name()
            if locale_name and "-" in locale_name:
                lang_win, region_win = locale_name.split("-", 1)
                lang = _LocaleUtils.normalize_code(lang_win, LANG_MAP, "")
                region = _LocaleUtils.normalize_code(region_win, REGION_MAP, "")
                if lang:
                    final_lang, final_region = lang, region if region else DEFAULT_REGION.get(lang, "US")
                    final_encoding = "UTF-8"
                    locale_detected = True

        elif system in ("Darwin", "Linux"):
            try:
                lang_raw, region_raw = locale.getlocale() or (None, None)
                if lang_raw or region_raw:
                    lang = _LocaleUtils.normalize_code(lang_raw, LANG_MAP, "")
                    region = _LocaleUtils.normalize_code(region_raw, REGION_MAP, "")
                    if lang:
                        final_lang, final_region = lang, region if region else DEFAULT_REGION.get(lang, "US")
                        final_encoding = "UTF-8"
                        locale_detected = True
            except Exception:
                pass

    if locale_detected:
        lang_region_bind = {
            "zh": "CN",
            "ja": "JP",
            "ko": "KR",
            "fr": "FR",
            "de": "DE",
            "en": "US",
            "es": "ES",
            "ru": "RU",
        }
        if final_lang in lang_region_bind and final_region == "US":
            final_region = lang_region_bind[final_lang]

    if not locale_detected:
        final_lang, final_region, final_encoding = "en", "US", "UTF-8"

    final_lang = final_lang if final_lang else "en"
    final_region = final_region if final_region else "US"
    final_encoding = final_encoding if final_encoding else "UTF-8"

    locale_str = f"{final_lang}_{final_region}.{final_encoding}"
    return LocaleInfo(locale_str=locale_str, lang=final_lang, region=final_region, encoding=final_encoding)


def _get_windows_locale_name() -> Optional[str]:
    """Get Windows locale name from registry or system API"""
    locale_name = None

    # Try to get from registry
    try:
        import winreg

        for hkey in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
            try:
                reg_key = winreg.OpenKey(hkey, r"Control Panel\International")
                locale_name = winreg.QueryValueEx(reg_key, "LocaleName")[0]
                winreg.CloseKey(reg_key)
                if locale_name:
                    return str(locale_name)
            except winreg.error:
                continue
    except (ImportError, Exception):
        pass

    # Fallback to ctypes
    if not locale_name:
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            lcid = kernel32.GetUserDefaultUILanguage()
            buf = ctypes.create_unicode_buffer(100)
            kernel32.GetLocaleInfoW(lcid, 0x0000005C, buf, 100)
            locale_name = buf.value
        except Exception:
            pass

    return locale_name


# locale standardization
if __name__ == "__main__":
    locale_info = get_locale_info()
    print(f"Standardized locale: {locale_info.locale_str}")
    print(f"Language code (for i18n): {locale_info.lang}")
    print(f"Region code (for i18n): {locale_info.region}")
    print(f"Character encoding: {locale_info.encoding}")
