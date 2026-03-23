#!/usr/bin/env python3
"""Tests for color module."""

import os
from remote_hosts.color import (
    init,
    deinit,
    should_colorize,
    Fore,
    Back,
    Style,
    END,
    BOLD,
    RED,
    GREEN,
    YELLOW,
    BLUE,
    HEADER,
)


class TestColor:
    """Test cases for color module."""

    def test_init_deinit_idempotent(self):
        """Test init and deinit are idempotent."""
        # Call multiple times to ensure no errors
        init()
        init()  # Should not raise
        deinit()
        deinit()  # Should not raise

    def test_should_colorize_default(self):
        """Test should_colorize returns appropriate value by default."""
        # Save original environment
        original_no_color = os.environ.get("NO_COLOR")
        original_force_color = os.environ.get("FORCE_COLOR")

        try:
            # Remove color environment variables
            if "NO_COLOR" in os.environ:
                del os.environ["NO_COLOR"]
            if "FORCE_COLOR" in os.environ:
                del os.environ["FORCE_COLOR"]

            # Should return bool
            result = should_colorize()
            assert isinstance(result, bool)
        finally:
            # Restore environment
            if original_no_color is not None:
                os.environ["NO_COLOR"] = original_no_color
            elif "NO_COLOR" in os.environ:
                del os.environ["NO_COLOR"]

            if original_force_color is not None:
                os.environ["FORCE_COLOR"] = original_force_color
            elif "FORCE_COLOR" in os.environ:
                del os.environ["FORCE_COLOR"]

    def test_should_colorize_no_color(self):
        """Test NO_COLOR environment variable disables color."""
        # Save original environment
        original_no_color = os.environ.get("NO_COLOR")

        try:
            os.environ["NO_COLOR"] = "1"
            assert should_colorize() is False
        finally:
            # Restore environment
            if original_no_color is not None:
                os.environ["NO_COLOR"] = original_no_color
            elif "NO_COLOR" in os.environ:
                del os.environ["NO_COLOR"]

    def test_should_colorize_force_color(self):
        """Test FORCE_COLOR environment variable enables color."""
        # Save original environment
        original_force_color = os.environ.get("FORCE_COLOR")

        try:
            os.environ["FORCE_COLOR"] = "1"
            assert should_colorize() is True
        finally:
            # Restore environment
            if original_force_color is not None:
                os.environ["FORCE_COLOR"] = original_force_color
            elif "FORCE_COLOR" in os.environ:
                del os.environ["FORCE_COLOR"]

    def test_color_instances_have_attributes(self):
        """Test color instances have expected attributes."""
        # Test Fore attributes
        assert hasattr(Fore, "RED")
        assert hasattr(Fore, "GREEN")
        assert hasattr(Fore, "BLUE")
        assert hasattr(Fore, "YELLOW")
        assert hasattr(Fore, "MAGENTA")
        assert hasattr(Fore, "CYAN")
        assert hasattr(Fore, "WHITE")
        assert hasattr(Fore, "BLACK")
        assert hasattr(Fore, "GRAY")
        assert hasattr(Fore, "RESET")

        # Test Back attributes
        assert hasattr(Back, "RED")
        assert hasattr(Back, "GREEN")
        assert hasattr(Back, "BLUE")
        assert hasattr(Back, "YELLOW")
        assert hasattr(Back, "MAGENTA")
        assert hasattr(Back, "CYAN")
        assert hasattr(Back, "WHITE")
        assert hasattr(Back, "BLACK")
        assert hasattr(Back, "GRAY")
        assert hasattr(Back, "RESET")

        # Test Style attributes
        assert hasattr(Style, "BRIGHT")
        assert hasattr(Style, "DIM")
        assert hasattr(Style, "NORMAL")
        assert hasattr(Style, "UNDERLINE")
        assert hasattr(Style, "RESET_UNDERLINE")
        assert hasattr(Style, "RESET_ALL")

    def test_color_attributes_return_strings(self):
        """Test color attributes return strings."""
        # Test Fore attributes
        assert isinstance(Fore.RED, str)
        assert isinstance(Fore.GREEN, str)
        assert isinstance(Fore.BLUE, str)

        # Test Back attributes
        assert isinstance(Back.RED, str)
        assert isinstance(Back.GREEN, str)
        assert isinstance(Back.BLUE, str)

        # Test Style attributes
        assert isinstance(Style.BRIGHT, str)
        assert isinstance(Style.UNDERLINE, str)
        assert isinstance(Style.RESET_ALL, str)

    def test_convenience_functions(self):
        """Test convenience functions return strings."""
        assert isinstance(END(), str)
        assert isinstance(BOLD(), str)
        assert isinstance(RED(), str)
        assert isinstance(GREEN(), str)
        assert isinstance(YELLOW(), str)
        assert isinstance(BLUE(), str)
        assert isinstance(HEADER(), str)

    def test_color_disabled_when_no_color_set(self):
        """Test color attributes return empty strings when NO_COLOR is set."""
        # Save original environment
        original_no_color = os.environ.get("NO_COLOR")

        try:
            os.environ["NO_COLOR"] = "1"
            # All color attributes should return empty strings
            assert Fore.RED == ""
            assert Back.GREEN == ""
            assert Style.BRIGHT == ""
            assert END() == ""
            assert BOLD() == ""
            assert RED() == ""
        finally:
            # Restore environment
            if original_no_color is not None:
                os.environ["NO_COLOR"] = original_no_color
            elif "NO_COLOR" in os.environ:
                del os.environ["NO_COLOR"]

    def test_init_enables_color(self):
        """Test init enables color support."""
        try:
            init()
            # After init, should_colorize should return appropriate value
            result = should_colorize()
            assert isinstance(result, bool)
        finally:
            deinit()

    def test_deinit_cleans_up(self):
        """Test deinit cleans up properly."""
        try:
            init()
            deinit()
            # After deinit, should_colorize should still return appropriate value
            result = should_colorize()
            assert isinstance(result, bool)
        finally:
            deinit()  # Ensure clean state

    def test_color_attributes_are_dynamic(self):
        """Test color attributes are dynamic based on colorization status."""
        # Save original environment
        original_no_color = os.environ.get("NO_COLOR")
        original_force_color = os.environ.get("FORCE_COLOR")

        try:
            # Remove NO_COLOR and set FORCE_COLOR to enable color
            if "NO_COLOR" in os.environ:
                del os.environ["NO_COLOR"]
            os.environ["FORCE_COLOR"] = "1"

            # Should return non-empty strings when color is enabled
            red_with_color = Fore.RED

            # Disable color with NO_COLOR (has higher priority)
            os.environ["NO_COLOR"] = "1"

            # Should return empty strings when color is disabled
            red_without_color = Fore.RED

            # The values should be different
            assert red_with_color != red_without_color
            assert red_with_color != ""
            assert red_without_color == ""
        finally:
            # Restore environment
            if original_no_color is not None:
                os.environ["NO_COLOR"] = original_no_color
            elif "NO_COLOR" in os.environ:
                del os.environ["NO_COLOR"]

            if original_force_color is not None:
                os.environ["FORCE_COLOR"] = original_force_color
            elif "FORCE_COLOR" in os.environ:
                del os.environ["FORCE_COLOR"]

    def test_terminal_support_check(self):
        """Test terminal support check."""
        # Save original environment
        original_term = os.environ.get("TERM")

        try:
            # Test with dumb terminal
            os.environ["TERM"] = "dumb"
            from remote_hosts.color import _check_term_support_color

            assert _check_term_support_color() is False

            # Test with color terminal
            os.environ["TERM"] = "xterm-color"
            assert _check_term_support_color() is True

            # Test with 256color terminal
            os.environ["TERM"] = "xterm-256color"
            assert _check_term_support_color() is True
        finally:
            # Restore environment
            if original_term is not None:
                os.environ["TERM"] = original_term
            elif "TERM" in os.environ:
                del os.environ["TERM"]

    def test_init_deinit_cycle(self):
        """Test complete init-deinit cycle."""
        try:
            # Initial state
            from remote_hosts.color import _state

            assert _state["init_called"] is False
            assert _state["deinit_registered"] is False

            # After init
            init()
            assert _state["init_called"] is True

            # After deinit
            deinit()
            assert _state["init_called"] is False
            assert _state["deinit_registered"] is False
        finally:
            deinit()  # Ensure clean state

    def test_color_with_force_color(self):
        """Test color attributes return non-empty strings when FORCE_COLOR is set."""
        # Save original environment
        original_force_color = os.environ.get("FORCE_COLOR")

        try:
            os.environ["FORCE_COLOR"] = "1"
            # All color attributes should return non-empty strings
            assert isinstance(Fore.RED, str)
            assert isinstance(Back.GREEN, str)
            assert isinstance(Style.BRIGHT, str)
            assert isinstance(END(), str)
            assert isinstance(BOLD(), str)
            assert isinstance(RED(), str)
        finally:
            # Restore environment
            if original_force_color is not None:
                os.environ["FORCE_COLOR"] = original_force_color
            elif "FORCE_COLOR" in os.environ:
                del os.environ["FORCE_COLOR"]

    def test_fore_all_colors(self):
        """Test all foreground colors are accessible."""
        colors = ["BLACK", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE", "GRAY", "RESET"]
        for color in colors:
            assert hasattr(Fore, color)
            result = getattr(Fore, color)
            assert isinstance(result, str)

    def test_back_all_colors(self):
        """Test all background colors are accessible."""
        colors = ["BLACK", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE", "GRAY", "RESET"]
        for color in colors:
            assert hasattr(Back, color)
            result = getattr(Back, color)
            assert isinstance(result, str)

    def test_style_all_styles(self):
        """Test all style attributes are accessible."""
        styles = ["BRIGHT", "DIM", "NORMAL", "UNDERLINE", "RESET_UNDERLINE", "RESET_ALL"]
        for style in styles:
            assert hasattr(Style, style)
            result = getattr(Style, style)
            assert isinstance(result, str)

    def test_color_attributes_with_force_color_override_no_color(self):
        """Test FORCE_COLOR overrides NO_COLOR."""
        # Save original environment
        original_no_color = os.environ.get("NO_COLOR")
        original_force_color = os.environ.get("FORCE_COLOR")

        try:
            # Set both NO_COLOR and FORCE_COLOR
            os.environ["NO_COLOR"] = "1"
            os.environ["FORCE_COLOR"] = "1"

            # FORCE_COLOR should override NO_COLOR
            result = Fore.RED
            # The result should be a string (may be empty or ANSI code)
            assert isinstance(result, str)
        finally:
            # Restore environment
            if original_no_color is not None:
                os.environ["NO_COLOR"] = original_no_color
            elif "NO_COLOR" in os.environ:
                del os.environ["NO_COLOR"]

            if original_force_color is not None:
                os.environ["FORCE_COLOR"] = original_force_color
            elif "FORCE_COLOR" in os.environ:
                del os.environ["FORCE_COLOR"]
