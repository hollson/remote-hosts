#!/usr/bin/env python3
"""Tests for main function."""

import pytest
import sys
from unittest.mock import patch, MagicMock
from remote_hosts.cli import main


class TestMain:
    """Test cases for main function."""

    @patch("sys.argv", ["remote-hosts", "-h"])
    @patch("builtins.print")
    def test_main_help(self, mock_print):
        """Test -h/--help option."""
        main()
        mock_print.assert_called()

    @patch("sys.argv", ["remote-hosts", "-v"])
    @patch("builtins.print")
    def test_main_version(self, mock_print):
        """Test -v/--version option."""
        main()
        mock_print.assert_called()

    @patch("sys.argv", ["remote-hosts", "-m"])
    @patch("remote_hosts.cli.show_manual")
    def test_main_manual(self, mock_show_manual):
        """Test -m/--manual option."""
        main()
        mock_show_manual.assert_called_once()

    @patch("sys.argv", ["remote-hosts", "-e"])
    @patch("remote_hosts.cli.edit_config")
    def test_main_edit(self, mock_edit_config):
        """Test -e/--edit option."""
        main()
        mock_edit_config.assert_called_once()

    @patch("sys.argv", ["remote-hosts", "-e", "vim"])
    @patch("remote_hosts.cli.edit_config")
    def test_main_edit_with_editor(self, mock_edit_config):
        """Test -e/--edit option with editor."""
        main()
        mock_edit_config.assert_called_once()

    @patch("sys.argv", ["remote-hosts", "invalid"])
    @patch("builtins.print")
    def test_main_invalid_arg(self, mock_print):
        """Test invalid argument."""
        main()
        mock_print.assert_called()

    @patch("sys.argv", ["remote-hosts", "-l"])
    @patch("os.path.exists")
    @patch("remote_hosts.cli.load_hosts")
    @patch("remote_hosts.cli.print_hosts")
    @patch("builtins.open")
    @patch("builtins.input")
    @patch("subprocess.run")
    def test_main_list_with_host_selection(
        self, mock_subprocess, mock_input, mock_open, mock_print_hosts, mock_load_hosts, mock_exists
    ):
        """Test -l/--list option with host selection."""
        # Setup mocks
        mock_exists.return_value = True
        mock_load_hosts.return_value = [{"id": 1, "host": "test.com", "user": "root", "port": 22}]
        mock_input.return_value = "1"
        mock_subprocess.return_value = MagicMock(returncode=0)

        # Mock open file object
        mock_file = MagicMock()
        mock_file.read.return_value = b'{"hosts":[]}'  # Return bytes
        mock_open.return_value.__enter__.return_value = mock_file

        main()

        mock_load_hosts.assert_called_once()
        mock_print_hosts.assert_called_once()
        mock_subprocess.assert_called_once()

    @patch("sys.argv", ["remote-hosts", "-l"])
    @patch("os.path.exists")
    @patch("remote_hosts.cli.Config._create_sample")
    @patch("remote_hosts.cli.load_hosts")
    @patch("remote_hosts.cli.print_hosts")
    @patch("builtins.open")
    @patch("builtins.input")
    def test_main_list_new_config(
        self, mock_input, mock_open, mock_print_hosts, mock_load_hosts, mock_create_sample, mock_exists
    ):
        """Test -l/--list option with new config file."""
        # Setup mocks
        mock_exists.return_value = False
        mock_load_hosts.return_value = []
        mock_input.return_value = "q"

        # Mock open file object
        mock_file = MagicMock()
        mock_file.read.return_value = b'{"hosts":[]}'  # Return bytes
        mock_open.return_value.__enter__.return_value = mock_file

        main()

        mock_create_sample.assert_called_once()
        mock_load_hosts.assert_called_once()
        mock_print_hosts.assert_called_once()

    @patch("sys.argv", ["remote-hosts", "-l"])
    @patch("os.path.exists")
    @patch("remote_hosts.cli.load_hosts")
    @patch("remote_hosts.cli.print_hosts")
    @patch("builtins.open")
    @patch("builtins.input")
    def test_main_list_quit(self, mock_input, mock_open, mock_print_hosts, mock_load_hosts, mock_exists):
        """Test -l/--list option with quit."""
        # Setup mocks
        mock_exists.return_value = True
        mock_load_hosts.return_value = [{"id": 1, "host": "test.com", "user": "root"}]
        mock_input.return_value = "q"

        # Mock open file object
        mock_file = MagicMock()
        mock_file.read.return_value = b'{"hosts":[{"id": 1, "host": "test.com", "user": "root"}]}'  # Return bytes
        mock_open.return_value.__enter__.return_value = mock_file

        main()

        mock_load_hosts.assert_called_once()
        mock_print_hosts.assert_called_once()

    @patch("sys.argv", ["remote-hosts", "-l"])
    @patch("os.path.exists")
    @patch("remote_hosts.cli.load_hosts")
    @patch("remote_hosts.cli.print_hosts")
    @patch("builtins.open")
    @patch("builtins.input")
    def test_main_list_invalid_id(self, mock_input, mock_open, mock_print_hosts, mock_load_hosts, mock_exists):
        """Test -l/--list option with invalid ID."""
        # Setup mocks
        mock_exists.return_value = True
        mock_load_hosts.return_value = [{"id": 1, "host": "test.com", "user": "root"}]
        mock_input.return_value = "abc"

        # Mock open file object
        mock_file = MagicMock()
        mock_file.read.return_value = b'{"hosts":[{"id": 1, "host": "test.com", "user": "root"}]}'  # Return bytes
        mock_open.return_value.__enter__.return_value = mock_file

        main()

        mock_load_hosts.assert_called_once()
        mock_print_hosts.assert_called_once()
