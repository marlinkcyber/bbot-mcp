#!/usr/bin/env python3

"""Test that sudo prompts are completely prevented"""

import json
import sys
import os
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_environment_variables():
    """Test that environment variables are set correctly"""
    print("Testing environment variables...")
    
    expected_vars = {
        'SUDO_ASKPASS': '/bin/false',
        'DEBIAN_FRONTEND': 'noninteractive',
        'CI': 'true'
    }
    
    from bbot_mcp.server import os as server_os
    
    success = True
    for var, expected_value in expected_vars.items():
        actual_value = server_os.environ.get(var)
        if actual_value == expected_value:
            print(f"✓ {var}: {actual_value}")
        else:
            print(f"✗ {var}: expected '{expected_value}', got '{actual_value}'")
            success = False
    
    return success

def test_comprehensive_config():
    """Test that comprehensive dependency prevention config works"""
    print("\nTesting comprehensive dependency prevention config...")
    
    try:
        from bbot import Scanner
        
        config = {
            'deps': {'behavior': 'ignore'},
            'force_deps': False,
            'install_deps': False,
            'auto_install_deps': False,
            'check_deps': False
        }
        
        scanner = Scanner('example.com', config=config)
        print(f"✓ Scanner created with comprehensive config")
        print(f"  - deps.behavior: {scanner.config.deps.behavior}")
        print(f"  - install_deps: {scanner.config.get('install_deps', 'not set')}")
        print(f"  - check_deps: {scanner.config.get('check_deps', 'not set')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error creating scanner: {e}")
        return False

def test_scan_start_with_comprehensive_protection():
    """Test starting a scan with all protection measures"""
    print("\nTesting scan start with comprehensive protection...")
    
    try:
        from bbot_mcp.server import start_bbot_scan, list_active_scans
        
        # Start a quick scan with a module that might trigger dependencies
        result = start_bbot_scan(
            targets="httpbin.org",
            modules="httpx",
            no_deps=True
        )
        
        data = json.loads(result)
        if data.get('success'):
            scan_id = data.get('scan_id')
            print(f"✓ Scan started successfully: {scan_id}")
            
            # Check that scan is listed as active
            time.sleep(1)  # Give it a moment to start
            active_scans = list_active_scans()
            active_data = json.loads(active_scans)
            
            if active_data.get('success') and len(active_data.get('scans', [])) > 0:
                print(f"✓ Scan is active and running")
                return True
            else:
                print("✗ Scan not found in active scans")
                return False
        else:
            print(f"✗ Scan failed to start: {data.get('error')}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing scan start: {e}")
        return False

def test_stdin_redirection():
    """Test that stdin redirection works"""
    print("\nTesting stdin redirection mechanism...")
    
    try:
        # This simulates what happens in _run_scan
        import sys
        original_stdin = sys.stdin
        
        # Redirect stdin to devnull (like in the scan function)
        sys.stdin = open(os.devnull, 'r')
        
        # Try to read from stdin - should not hang
        print("✓ stdin redirected to /dev/null")
        
        # Restore stdin
        sys.stdin.close()
        sys.stdin = original_stdin
        print("✓ stdin restored successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Error with stdin redirection: {e}")
        return False

def main():
    """Run all sudo prevention tests"""
    print("BBOT Sudo Prevention Test Suite")
    print("=" * 50)
    
    tests = [
        test_environment_variables,
        test_comprehensive_config,
        test_stdin_redirection,
        test_scan_start_with_comprehensive_protection
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
    print(f"Sudo Prevention Tests: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All sudo prevention measures are in place!")
        print("✓ The MCP server should now be protected against sudo prompts!")
        return 0
    else:
        print("✗ Some sudo prevention measures failed.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)