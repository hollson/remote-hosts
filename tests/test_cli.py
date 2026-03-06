#!/usr/bin/env python3
"""Tests for CLI functionality."""

import pytest
import sys
import json
import hashlib
import os
import tempfile
from io import StringIO
from unittest.mock import patch, MagicMock
from remote_hosts.cli import Color, print_hosts, Config, DEFAULT_SAMPLE_MD5


class TestColor:
    """Test cases for Color class."""

    def test_color_constants(self):
        """Test color constants are defined."""
        assert Color.RED == "\033[91m"
        assert Color.GREEN == "\033[92m"
        assert Color.YELLOW == "\033[93m"
        assert Color.BLUE == "\033[94m"
        assert Color.HEADER == "\033[95m"
        assert Color.END == "\033[0m"
        assert Color.BOLD == "\033[1m"


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
                if sys.version_info >= (3, 9):
                    calculated_md5 = hashlib.md5(f.read(), usedforsecurity=False).hexdigest().upper()
                else:
                    calculated_md5 = hashlib.md5(f.read()).hexdigest().upper()

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
                if sys.version_info >= (3, 9):
                    file_md5 = hashlib.md5(f.read(), usedforsecurity=False).hexdigest().upper()
                else:
                    file_md5 = hashlib.md5(f.read()).hexdigest().upper()

            assert file_md5 == DEFAULT_SAMPLE_MD5, (
                f"Config._create_sample MD5 mismatch. Expected: {DEFAULT_SAMPLE_MD5}, " f"Got: {file_md5}"
            )
