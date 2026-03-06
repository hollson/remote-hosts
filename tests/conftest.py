#!/usr/bin/env python3
"""Pytest configuration file."""

import pytest
import tempfile
import os
import json


@pytest.fixture
def temp_config_file():
    """Create a temporary configuration file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        config_data = {
            "hosts": [
                {
                    "id": 1,
                    "host": "test1.com",
                    "user": "root",
                    "port": 22,
                    "os": "ubuntu",
                    "arch": "x86_64",
                    "region": "Beijing",
                    "mark": "test",
                },
                {"id": 2, "host": "192.168.1.1", "user": "admin", "port": 2222, "mark": "local"},
            ]
        }
        json.dump(config_data, f)
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


@pytest.fixture
def empty_config_file():
    """Create an empty configuration file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"hosts": []}, f)
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


@pytest.fixture
def invalid_config_file():
    """Create an invalid configuration file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write('{"invalid json')
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)
