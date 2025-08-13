#!/usr/bin/env python3

import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bbot_mcp.server import mcp

def test_list_modules():
    """Test listing bbot modules"""
    print("Testing list_bbot_modules...")
    try:
        from bbot_mcp.server import list_bbot_modules
        result = list_bbot_modules()
        data = json.loads(result)
        print(f"✓ Modules listed successfully: {len(data.get('modules', {}).get('scan_modules', []))} scan modules found")
        return True
    except Exception as e:
        print(f"✗ Error listing modules: {e}")
        return False

def test_list_presets():
    """Test listing bbot presets"""
    print("Testing list_bbot_presets...")
    try:
        from bbot_mcp.server import list_bbot_presets
        result = list_bbot_presets()
        data = json.loads(result)
        print(f"✓ Presets listed successfully: {len(data.get('presets', []))} presets found")
        return True
    except Exception as e:
        print(f"✗ Error listing presets: {e}")
        return False

def test_scan_management():
    """Test scan management functions"""
    print("Testing scan management...")
    try:
        from bbot_mcp.server import list_active_scans, start_bbot_scan, get_scan_status
        
        # Test listing active scans (should be empty initially)
        result = list_active_scans()
        data = json.loads(result)
        print(f"✓ Active scans listed: {len(data.get('scans', []))} scans")
        
        # Test starting a scan (dry run with simple target)
        print("Testing scan start (this may take a moment)...")
        result = start_bbot_scan(
            targets="example.com",
            modules="httpx",
            presets="",
            flags=""
        )
        data = json.loads(result)
        
        if data.get('success'):
            scan_id = data.get('scan_id')
            print(f"✓ Scan started successfully with ID: {scan_id}")
            
            # Test getting scan status
            result = get_scan_status(scan_id)
            status_data = json.loads(result)
            if status_data.get('success'):
                print(f"✓ Scan status retrieved: {status_data['scan']['status']}")
            else:
                print(f"✗ Error getting scan status: {status_data.get('error')}")
                
        else:
            print(f"✗ Error starting scan: {data.get('error')}")
            
        return True
    except Exception as e:
        print(f"✗ Error in scan management test: {e}")
        return False

def main():
    """Run all tests"""
    print("BBOT MCP Server Test Suite")
    print("=" * 40)
    
    tests = [
        test_list_modules,
        test_list_presets,
        test_scan_management
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
        print()
    
    print("=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)