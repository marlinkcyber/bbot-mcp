#!/usr/bin/env python3

"""Simple test to verify MCP server functionality"""

import pytest
import json
from bbot_mcp.server import list_bbot_modules, list_bbot_presets, list_active_scans


def test_tools():
    """Test all MCP tools directly (non-async)"""
    print("Testing MCP server tools...")
    
    try:
        # Test list_bbot_modules
        print("Testing list_bbot_modules...")
        result = list_bbot_modules()
        data = json.loads(result)
        if data.get('success'):
            total = data.get('total_count', 0)
            print(f"✓ list_bbot_modules: {total} modules found")
        else:
            print(f"✗ list_bbot_modules failed: {data.get('error')}")
            assert False, f"list_bbot_modules failed: {data.get('error')}"
        
        # Test list_bbot_presets
        print("Testing list_bbot_presets...")
        result = list_bbot_presets()
        data = json.loads(result)
        if data.get('success'):
            total = data.get('total_count', 0)
            print(f"✓ list_bbot_presets: {total} presets found")
        else:
            print(f"✗ list_bbot_presets failed: {data.get('error')}")
            assert False, f"list_bbot_presets failed: {data.get('error')}"
            
        # Test list_active_scans
        print("Testing list_active_scans...")
        result = list_active_scans()
        data = json.loads(result)
        if data.get('success'):
            scans = len(data.get('scans', []))
            print(f"✓ list_active_scans: {scans} active scans")
        else:
            print(f"✗ list_active_scans failed: {data.get('error')}")
            assert False, f"list_active_scans failed: {data.get('error')}"
        
        print("\n✓ MCP server tools tested successfully!")
        
    except Exception as e:
        print(f"✗ MCP server test failed: {e}")
        assert False, f"MCP server test failed: {e}"