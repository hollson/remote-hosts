#!/usr/bin/env python3

"""
Temporary test script to check English i18n functionality
without modifying existing code
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the i18n module
from remote_hosts import i18n

# Temporarily override the LANG variable for testing
i18n.LANG = 'en'

print("Testing English i18n translations...")
print("=" * 50)

# Test some translations
test_keys = [
    'help_title',
    'enter_host_id', 
    'connecting',
    'header_host',
    'header_user',
    'option_list',
    'option_edit'
]

for key in test_keys:
    if key == 'connecting':
        # Test with format parameters
        result = i18n._(key, user='test', host='example.com', port=22)
    else:
        result = i18n._(key)
    print(f"{key}: {result}")

print("=" * 50)
print("English i18n test completed!")
