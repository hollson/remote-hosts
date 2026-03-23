#!/usr/bin/env python3
"""Tests for CLI functionality."""

import pytest
import json
import os
import tempfile
from io import StringIO
from unittest.mock import patch, MagicMock
from remote_hosts.cli import print_hosts, Config, DEFAULT_SAMPLE_MD5, _compute_md5, load_hosts
from remote_hosts.color import RED, GREEN, YELLOW, BLUE, END, BOLD


class TestColor:
    """Test cases for Color constants."""

    def test_color_constants(self):
        """Test color constants are defined (empty in non-TTY environment)."""
        # 颜色函数返回动态值，可能是空字符串或ANSI码
        from remote_hosts.color import Fore, Style

        # 调用颜色函数获取实际值
        assert RED() in ("", "\033[91m")
        assert GREEN() in ("", "\033[92m")
        assert YELLOW() in ("", "\033[93m")
        assert BLUE() in ("", "\033[94m")
        assert END() in ("", "\033[0m")
        assert BOLD() in ("", "\033[1m")
        # Fore.MAGENTA 替代 HEADER
        assert Fore.MAGENTA in ("", "\033[95m")


class TestPrintHosts:
    """Test cases for print_hosts function."""

    def test_print_hosts_with_data(self, capsys):
        """Test printing hosts table with data."""
        hosts = [
            {
                "id": 1,
                "host": "test.com",
                "user": "root",
                "os": "ubuntu",
                "arch": "x86_64",
                "region": "Beijing",
                "mark": "test",
            }
        ]
        print_hosts(hosts, "/tmp/test.json")
        captured = capsys.readouterr()
        assert "test.com" in captured.out
        assert "root" in captured.out
        assert "1" in captured.out

    def test_print_hosts_empty(self, capsys):
        """Test printing empty hosts list."""
        hosts = []
        print_hosts(hosts, "/tmp/test.json")
        captured = capsys.readouterr()
        # Empty list shows error message
        assert "所有行都为空" in captured.out or "All rows are empty" in captured.out


class TestVersion:
    """Test cases for version information."""

    def test_version_import(self):
        """Test version can be imported."""
        from remote_hosts.cli import __version__

        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_version_format(self):
        """Test version follows semantic versioning."""
        from remote_hosts.cli import __version__

        parts = __version__.split(".")
        assert len(parts) >= 2
        # Check major and minor are numbers
        assert parts[0].isdigit()
        assert parts[1].isdigit()


class TestSampleDataMD5:
    """Test cases for sample data MD5 verification."""

    def test_default_sample_md5_constant(self):
        """Test that DEFAULT_SAMPLE_MD5 constant is correctly defined."""
        assert DEFAULT_SAMPLE_MD5 == "5FACF518B4AD006EA238A27BD60B7BD7"
        assert isinstance(DEFAULT_SAMPLE_MD5, str)

    def test_sample_data_md5_matches_constant(self):
        """Test that sample_data generates the expected MD5 hash.

        This test creates a sample config file and verifies its MD5 hash
        matches the DEFAULT_SAMPLE_MD5 constant.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            temp_path = f.name
            sample_data = [
                {
                    "id": 1,
                    "host": "example.com",
                    "port": 22,
                    "user": "root",
                    "key": "~/.ssh/id_rsa",
                    "os": "ubuntu22.04",
                    "arch": "x86_64",
                    "region": "Beijing",
                    "mark": "example",
                },
                {"id": 2, "host": "192.168.1.1", "user": "root", "mark": "example"},
            ]
            json.dump(sample_data, f, indent="\t", ensure_ascii=False)

        try:
            with open(temp_path, "rb") as f:
                calculated_md5 = _compute_md5(f.read())

            assert calculated_md5 == DEFAULT_SAMPLE_MD5, (
                f"Sample data MD5 mismatch. Expected: {DEFAULT_SAMPLE_MD5}, " f"Got: {calculated_md5}"
            )
        finally:
            os.unlink(temp_path)

    def test_config_creates_sample_with_expected_md5(self):
        """Test that Config._create_sample generates file with expected MD5."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_config.json")
            config = Config(config_path)
            config._create_sample()

            assert os.path.exists(config_path), "Sample config file should be created"

            with open(config_path, "rb") as f:
                file_md5 = _compute_md5(f.read())

            assert file_md5 == DEFAULT_SAMPLE_MD5, (
                f"Config._create_sample MD5 mismatch. Expected: {DEFAULT_SAMPLE_MD5}, " f"Got: {file_md5}"
            )

    def test_md5_cross_platform_consistency(self):
        """Test that MD5 calculation is consistent across different line endings.

        This test verifies that _compute_md5 produces the same hash regardless
        of whether the file uses Windows (CRLF) or Unix (LF) line endings.
        """
        sample_data = [
            {
                "id": 1,
                "host": "example.com",
                "port": 22,
                "user": "root",
                "key": "~/.ssh/id_rsa",
                "os": "ubuntu22.04",
                "arch": "x86_64",
                "region": "Beijing",
                "mark": "example",
            },
            {"id": 2, "host": "192.168.1.1", "user": "root", "mark": "example"},
        ]
        content = json.dumps(sample_data, indent="\t", ensure_ascii=False)

        # Simulate Windows line endings (CRLF)
        windows_content = content.encode("utf-8").replace(b"\n", b"\r\n")
        # Simulate Linux line endings (LF)
        linux_content = content.encode("utf-8")

        windows_md5 = _compute_md5(windows_content)
        linux_md5 = _compute_md5(linux_content)

        assert windows_md5 == linux_md5, (
            f"MD5 should be consistent across platforms. " f"Windows: {windows_md5}, Linux: {linux_md5}"
        )
        assert windows_md5 == DEFAULT_SAMPLE_MD5, (
            f"Cross-platform MD5 should match DEFAULT_SAMPLE_MD5. "
            f"Expected: {DEFAULT_SAMPLE_MD5}, Got: {windows_md5}"
        )


class TestConfig:
    """Test cases for Config class."""

    def test_config_load_valid_file(self):
        """Test loading valid configuration file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_config.json")
            sample_data = [
                {
                    "id": 1,
                    "host": "example.com",
                    "port": 22,
                    "user": "root",
                    "key": "~/.ssh/id_rsa",
                    "os": "ubuntu22.04",
                    "arch": "x86_64",
                    "region": "Beijing",
                    "mark": "example",
                },
                {"id": 2, "host": "192.168.1.1", "user": "root", "mark": "example"},
            ]
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(sample_data, f, indent="\t", ensure_ascii=False)

            config = Config(config_path)
            hosts = config.load()

            assert len(hosts) == 2
            assert hosts[0]["id"] == 1
            assert hosts[0]["host"] == "example.com"
            assert hosts[1]["id"] == 2
            assert hosts[1]["host"] == "192.168.1.1"

    def test_config_load_empty_hosts(self):
        """Test loading configuration with empty hosts list."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_config.json")
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent="\t", ensure_ascii=False)

            config = Config(config_path)
            hosts = config.load()

            assert len(hosts) == 0

    def test_config_load_file_not_found(self, capsys):
        """Test loading non-existent configuration file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "subdir", "nonexistent_config.json")
            config = Config(config_path)

            with pytest.raises(SystemExit) as exc_info:
                config.load()

            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert "已初始化配置文件" in captured.out or "Configuration file initialized" in captured.out

    def test_config_load_invalid_json(self, capsys):
        """Test loading invalid JSON file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_config.json")
            with open(config_path, "w", encoding="utf-8") as f:
                f.write("invalid json content")

            config = Config(config_path)

            with pytest.raises(SystemExit) as exc_info:
                config.load()

            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "配置文件错误" in captured.out or "Configuration file error" in captured.out

    def test_config_validate_duplicate_ids(self, capsys):
        """Test validation of duplicate host IDs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_config.json")
            sample_data = [
                {"id": 1, "host": "example.com", "user": "root"},
                {"id": 1, "host": "example2.com", "user": "root"},
            ]
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(sample_data, f, indent="\t", ensure_ascii=False)

            config = Config(config_path)

            with pytest.raises(SystemExit) as exc_info:
                config.load()

            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "重复的主机ID" in captured.out or "Duplicate host ID" in captured.out

    def test_config_validate_missing_required_fields(self, capsys):
        """Test validation of missing required fields."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_config.json")
            sample_data = [
                {"id": 1, "host": "example.com"},
                {"id": 2, "user": "root"},
            ]
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(sample_data, f, indent="\t", ensure_ascii=False)

            config = Config(config_path)

            with pytest.raises(SystemExit) as exc_info:
                config.load()

            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "主机配置错误" in captured.out or "Host configuration error" in captured.out

    def test_config_create_sample(self):
        """Test creating sample configuration file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_config.json")
            config = Config(config_path)
            config._create_sample()

            assert os.path.exists(config_path)

            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert isinstance(data, list)
            assert len(data) == 2
            assert data[0]["id"] == 1
            assert data[1]["id"] == 2


class TestLoadHosts:
    """Test cases for load_hosts function."""

    def test_load_hosts_success(self):
        """Test loading hosts successfully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_config.json")
            sample_data = [
                {"id": 1, "host": "example.com", "user": "root"},
                {"id": 2, "host": "192.168.1.1", "user": "root"},
            ]
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(sample_data, f, indent="\t", ensure_ascii=False)

            hosts = load_hosts(config_path)

            assert len(hosts) == 2
            assert hosts[0]["id"] == 1
            assert hosts[1]["id"] == 2


class TestPrintHostsAdditional:
    """Additional test cases for print_hosts function."""

    def test_print_hosts_with_multiple_hosts(self, capsys):
        """Test printing multiple hosts."""
        hosts = [
            {
                "id": 1,
                "host": "test1.com",
                "user": "root",
                "os": "ubuntu",
                "arch": "x86_64",
                "region": "Beijing",
                "mark": "test1",
            },
            {
                "id": 2,
                "host": "test2.com",
                "user": "root",
                "os": "ubuntu",
                "arch": "x86_64",
                "region": "Shanghai",
                "mark": "test2",
            },
            {
                "id": 3,
                "host": "test3.com",
                "user": "root",
                "os": "ubuntu",
                "arch": "x86_64",
                "region": "Guangzhou",
                "mark": "test3",
            },
        ]
        print_hosts(hosts, "/tmp/test.json")
        captured = capsys.readouterr()
        assert "test1.com" in captured.out
        assert "test2.com" in captured.out
        assert "test3.com" in captured.out

    def test_print_hosts_with_minimal_data(self, capsys):
        """Test printing hosts with minimal data."""
        hosts = [
            {"id": 1, "host": "test.com", "user": "root"},
        ]
        print_hosts(hosts, "/tmp/test.json")
        captured = capsys.readouterr()
        assert "test.com" in captured.out
        assert "root" in captured.out
        assert "-" in captured.out  # Missing fields should show "-"

    def test_print_hosts_with_unicode(self, capsys):
        """Test printing hosts with unicode characters."""
        hosts = [
            {
                "id": 1,
                "host": "测试.com",
                "user": "root",
                "os": "ubuntu",
                "arch": "x86_64",
                "region": "北京",
                "mark": "测试",
            },
        ]
        print_hosts(hosts, "/tmp/test.json")
        captured = capsys.readouterr()
        assert "测试.com" in captured.out
        assert "北京" in captured.out

    def test_print_hosts_with_keyerror(self, capsys):
        """Test printing hosts with missing required fields."""
        hosts = [
            {"id": 1, "user": "root"},
        ]
        print_hosts(hosts, "/tmp/test.json")
        captured = capsys.readouterr()
        # Missing host field means row won't be added, but no error
        assert "所有行都为空" in captured.out or "All rows are empty" in captured.out


class TestComputeMD5:
    """Test cases for _compute_md5 function."""

    def test_compute_md5_with_crlf(self):
        """Test _compute_md5 normalizes CRLF to LF."""
        data = b"line1\r\nline2\r\nline3\r\n"
        result = _compute_md5(data)
        assert isinstance(result, str)
        assert len(result) == 32

    def test_compute_md5_with_lf(self):
        """Test _compute_md5 handles LF correctly."""
        data = b"line1\nline2\nline3\n"
        result = _compute_md5(data)
        assert isinstance(result, str)
        assert len(result) == 32

    def test_compute_md5_empty_data(self):
        """Test _compute_md5 handles empty data."""
        data = b""
        result = _compute_md5(data)
        assert isinstance(result, str)
        assert len(result) == 32

    def test_compute_md5_uppercase(self):
        """Test _compute_md5 returns uppercase hash."""
        data = b"test data"
        result = _compute_md5(data)
        assert result == result.upper()


class TestConfigAdditional:
    """Additional test cases for Config class."""

    def test_config_expands_path(self):
        """Test Config expands user path."""
        config = Config("~/test_config.json")
        assert "~" not in config.config_path

    def test_config_initializes_empty_hosts(self):
        """Test Config initializes with empty hosts list."""
        config = Config("/tmp/test_config.json")
        assert config.hosts == []

    def test_config_load_with_dict_format(self, capsys):
        """Test loading config with dict format containing hosts key."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_config.json")
            sample_data = {
                "hosts": [
                    {"id": 1, "host": "example.com", "user": "root"},
                    {"id": 2, "host": "192.168.1.1", "user": "root"},
                ]
            }
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(sample_data, f, indent="\t", ensure_ascii=False)

            config = Config(config_path)
            hosts = config.load()

            assert len(hosts) == 2
            assert hosts[0]["id"] == 1
            assert hosts[1]["id"] == 2

    def test_config_load_with_invalid_format(self, capsys):
        """Test loading config with invalid format (not list or dict with hosts)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_config.json")
            sample_data = "invalid format"
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(sample_data)

            config = Config(config_path)

            with pytest.raises(SystemExit) as exc_info:
                config.load()

            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "配置文件错误" in captured.out or "Configuration file error" in captured.out

    def test_config_validate_with_none_id(self, capsys):
        """Test validation with None ID."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_config.json")
            sample_data = [
                {"host": "example.com", "user": "root"},
            ]
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(sample_data, f, indent="\t", ensure_ascii=False)

            config = Config(config_path)

            with pytest.raises(SystemExit) as exc_info:
                config.load()

            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "主机配置错误" in captured.out or "Host configuration error" in captured.out

    def test_config_validate_with_empty_host(self, capsys):
        """Test validation with empty host."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_config.json")
            sample_data = [
                {"id": 1, "host": "", "user": "root"},
            ]
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(sample_data, f, indent="\t", ensure_ascii=False)

            config = Config(config_path)

            with pytest.raises(SystemExit) as exc_info:
                config.load()

            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "主机配置错误" in captured.out or "Host configuration error" in captured.out

    def test_config_validate_with_empty_user(self, capsys):
        """Test validation with empty user."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_config.json")
            sample_data = [
                {"id": 1, "host": "example.com", "user": ""},
            ]
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(sample_data, f, indent="\t", ensure_ascii=False)

            config = Config(config_path)

            with pytest.raises(SystemExit) as exc_info:
                config.load()

            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "主机配置错误" in captured.out or "Host configuration error" in captured.out
