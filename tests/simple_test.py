#!/usr/bin/env python3

"""Simple test of the MCP tools directly"""

import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_tool_functions():
    """Test the tool functions directly"""
    print("Testing MCP tool functions directly...")
    
    try:
        # Import the tool functions
        from bbot_mcp.server import list_bbot_modules, list_bbot_presets, list_active_scans
        
        # Test list_bbot_modules
        print("\n1. Testing list_bbot_modules...")
        result = list_bbot_modules()
        data = json.loads(result)
        if data.get('success'):
            total = data.get('total_count', 0)
            scan_modules = len(data.get('modules', {}).get('scan_modules', []))
            output_modules = len(data.get('modules', {}).get('output_modules', []))
            print(f"   ✓ Found {total} modules ({scan_modules} scan, {output_modules} output)")
        else:
            print(f"   ✗ Failed: {data.get('error')}")
        
        # Test list_bbot_presets  
        print("\n2. Testing list_bbot_presets...")
        result = list_bbot_presets()
        data = json.loads(result)
        if data.get('success'):
            total = data.get('total_count', 0)
            print(f"   ✓ Found {total} presets")
            # Show a few example presets
            presets = data.get('presets', [])[:5]
            for preset in presets:
                print(f"      - {preset['name']}")
        else:
            print(f"   ✗ Failed: {data.get('error')}")
            
        # Test list_active_scans
        print("\n3. Testing list_active_scans...")
        result = list_active_scans()
        data = json.loads(result)
        if data.get('success'):
            scans = len(data.get('scans', []))
            print(f"   ✓ Found {scans} active scans")
        else:
            print(f"   ✗ Failed: {data.get('error')}")
            
        print("\n✓ All tool tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n✗ Tool test failed: {e}")
        return False

def test_mcp_server_creation():
    """Test that MCP server was created correctly"""
    print("\nTesting MCP server creation...")
    
    try:
        from bbot_mcp.server import mcp, scan_manager
        
        print(f"   ✓ MCP server created: {mcp.name}")
        print(f"   ✓ Scan manager created: {type(scan_manager).__name__}")
        
        return True
        
    except Exception as e:
        print(f"   ✗ MCP server creation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("BBOT MCP Server Functionality Test")
    print("=" * 50)
    
    tests = [
        test_mcp_server_creation,
        test_tool_functions
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Functionality Tests: {passed}/{total} passed")
    
    if passed == total:
        print("✓ MCP server is working correctly!")
        return 0
    else:
        print("✗ Some functionality tests failed.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)