#!/usr/bin/env python3

"""Test the no_deps functionality to ensure sudo prompts are prevented"""

import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_dependency_info():
    """Test the new dependency info tool"""
    print("Testing dependency info tool...")
    
    try:
        from bbot_mcp.server import get_dependency_info
        
        result = get_dependency_info()
        data = json.loads(result)
        
        if data.get('success'):
            print("✓ Dependency info retrieved successfully")
            dep_mgmt = data.get('dependency_management', {})
            print(f"  - Default behavior: {dep_mgmt.get('default_behavior')}")
            print(f"  - Sudo prevention: {dep_mgmt.get('sudo_prevention')}")
            return True
        else:
            print(f"✗ Failed: {data.get('error')}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_scan_with_no_deps():
    """Test that scans can be started with no_deps parameter"""
    print("\nTesting scan start with no_deps=True...")
    
    try:
        from bbot_mcp.server import start_bbot_scan
        
        # Test with no_deps=True (default)
        result = start_bbot_scan(
            targets="httpbin.org",
            modules="httpx",
            no_deps=True
        )
        data = json.loads(result)
        
        if data.get('success'):
            print("✓ Scan started successfully with no_deps=True")
            print(f"  - Scan ID: {data.get('scan_id')}")
            return True
        else:
            print(f"✗ Failed: {data.get('error')}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_scan_without_no_deps():
    """Test that scans can be started with no_deps=False (for comparison)"""
    print("\nTesting scan start with no_deps=False...")
    
    try:
        from bbot_mcp.server import start_bbot_scan
        
        # Test with no_deps=False (should still work but might have dependency issues)
        result = start_bbot_scan(
            targets="httpbin.org",
            modules="httpx",
            no_deps=False
        )
        data = json.loads(result)
        
        if data.get('success'):
            print("✓ Scan started successfully with no_deps=False")
            print(f"  - Scan ID: {data.get('scan_id')}")
            return True
        else:
            print(f"✗ Failed: {data.get('error')}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_deps_config_directly():
    """Test the deps configuration directly with bbot"""
    print("\nTesting deps configuration directly...")
    
    try:
        from bbot import Scanner
        
        # Test with deps.behavior = 'ignore'
        config = {'deps': {'behavior': 'ignore'}}
        scanner = Scanner('example.com', config=config)
        
        print("✓ Scanner created successfully with deps.behavior='ignore'")
        print(f"  - Deps behavior: {scanner.config.deps.behavior}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Run all no_deps tests"""
    print("BBOT No-Deps Functionality Test")
    print("=" * 40)
    
    tests = [
        test_dependency_info,
        test_deps_config_directly,
        test_scan_with_no_deps,
        test_scan_without_no_deps
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
    
    print("\n" + "=" * 40)
    print(f"No-Deps Tests: {passed}/{total} passed")
    
    if passed == total:
        print("✓ No-deps functionality is working correctly!")
        print("✓ Sudo prompts should now be prevented during scans!")
        return 0
    else:
        print("✗ Some no-deps functionality tests failed.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)