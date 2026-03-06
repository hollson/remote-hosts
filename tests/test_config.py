#!/usr/bin/env python3
"""Tests for configuration management."""

import pytest
import json
import os
from remote_hosts.cli import Config, load_hosts


class TestConfig:
    """Test cases for Config class."""

    def test_config_load_valid_file(self, temp_config_file):
        """Test loading a valid configuration file."""
        config = Config(temp_config_file)
        hosts = config.load()
        assert len(hosts) == 2
        assert hosts[0]["id"] == 1
        assert hosts[0]["host"] == "test1.com"
        assert hosts[1]["user"] == "admin"

    def test_config_load_empty_hosts(self, empty_config_file):
        """Test loading a configuration file with empty hosts."""
        config = Config(empty_config_file)
        hosts = config.load()
        assert len(hosts) == 0

    def test_config_load_file_not_found(self, tmp_path):
        """Test loading a non-existent configuration file creates a sample."""
        non_existent = str(tmp_path / "non_existent.json")
        config = Config(non_existent)
        with pytest.raises(SystemExit) as exc_info:
            config.load()
        assert exc_info.value.code == 0
        # Verify sample file was created
        assert os.path.exists(non_existent)
        with open(non_existent, "r") as f:
            data = json.load(f)
            assert len(data) == 2  # Sample has 2 hosts

    def test_config_load_invalid_json(self, invalid_config_file):
        """Test loading an invalid JSON file."""
        config = Config(invalid_config_file)
        with pytest.raises(SystemExit) as exc_info:
            config.load()
        assert exc_info.value.code == 1

    def test_config_validate_duplicate_ids(self, tmp_path):
        """Test validation catches duplicate host IDs."""
        config_file = tmp_path / "dup_id.json"
        with open(config_file, "w") as f:
            json.dump(
                {
                    "hosts": [
                        {"id": 1, "host": "host1.com", "user": "root"},
                        {"id": 1, "host": "host2.com", "user": "admin"},
                    ]
                },
                f,
            )

        config = Config(str(config_file))
        with pytest.raises(SystemExit) as exc_info:
            config.load()
        assert exc_info.value.code == 1

    def test_config_validate_missing_required_fields(self, tmp_path):
        """Test validation catches missing required fields."""
        config_file = tmp_path / "missing_fields.json"
        with open(config_file, "w") as f:
            json.dump({"hosts": [{"id": 1, "host": "host1.com"}]}, f)  # Missing user

        config = Config(str(config_file))
        with pytest.raises(SystemExit) as exc_info:
            config.load()
        assert exc_info.value.code == 1

    def test_config_create_sample(self, tmp_path):
        """Test creating a sample configuration file."""
        config_file = tmp_path / "sample.json"
        config = Config(str(config_file))
        config._create_sample()

        assert os.path.exists(config_file)
        with open(config_file, "r") as f:
            data = json.load(f)
            assert len(data) == 2
            assert data[0]["id"] == 1
            assert data[0]["host"] == "example.com"


class TestLoadHosts:
    """Test cases for load_hosts function."""

    def test_load_hosts_success(self, temp_config_file):
        """Test successful host loading."""
        hosts = load_hosts(temp_config_file)
        assert len(hosts) == 2
        assert hosts[0]["id"] == 1
