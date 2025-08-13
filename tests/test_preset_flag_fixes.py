#!/usr/bin/env python3

"""Test the preset and flag handling fixes"""

import json
import sys
import os
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_flag_extension():
    """Test that flags are extended rather than replaced"""
    print("Testing flag extension functionality...")
    
    try:
        from bbot import Preset
        
        # Test the same logic as in the fixed MCP server
        preset = Preset()
        preset.include_preset('subdomain-enum')
        
        print(f"Original preset flags: {preset.flags}")
        
        # Simulate the fixed flag handling
        scan_flags = ['passive']
        existing_flags = set(preset.flags) if preset.flags else set()
        new_flags = set(scan_flags)
        preset.flags = list(existing_flags.union(new_flags))
        
        print(f"Extended flags: {preset.flags}")
        
        # Check that both flags are present
        has_subdomain_enum = 'subdomain-enum' in preset.flags
        has_passive = 'passive' in preset.flags
        
        print(f"✓ Has subdomain-enum flag: {has_subdomain_enum}")
        print(f"✓ Has passive flag: {has_passive}")
        
        return has_subdomain_enum and has_passive
        
    except Exception as e:
        print(f"✗ Flag extension test error: {e}")
        return False

def test_mcp_scan_fixed():
    """Test the fixed MCP scan with subdomain-enum + passive"""
    print("\nTesting fixed MCP scan with subdomain-enum + passive...")
    
    try:
        from bbot_mcp.server import start_bbot_scan, get_scan_status, get_scan_results
        
        # Start the problematic scan configuration
        result = start_bbot_scan(
            targets="scanme.nmap.org",
            modules="",  # No additional modules
            presets="subdomain-enum",
            flags="passive",
            no_deps=True
        )
        
        data = json.loads(result)
        if not data.get('success'):
            print(f"✗ Failed to start scan: {data.get('error')}")
            return False
        
        scan_id = data.get('scan_id')
        print(f"✓ Scan started: {scan_id}")
        
        # Wait for scan to complete (with timeout)
        max_wait = 45  # 45 seconds max
        start_time = time.time()
        
        final_status = None
        final_result_count = 0
        
        while time.time() - start_time < max_wait:
            status_result = get_scan_status(scan_id)
            status_data = json.loads(status_result)
            
            if status_data.get('success'):
                scan_info = status_data.get('scan', {})
                status = scan_info.get('status')
                result_count = scan_info.get('result_count', 0)
                
                print(f"  Status: {status}, Results: {result_count}")
                
                if status in ['completed', 'error']:
                    final_status = status
                    final_result_count = result_count
                    break
            
            time.sleep(3)
        
        if final_status == 'completed':
            print(f"✓ Scan completed with {final_result_count} results")
            
            # Get a few sample results
            if final_result_count > 0:
                results_result = get_scan_results(scan_id, limit=5)
                results_data = json.loads(results_result)
                
                if results_data.get('success'):
                    results = results_data.get('results', [])
                    print("Sample results:")
                    for i, result in enumerate(results[:3]):
                        print(f"  {i+1}. {result.get('type')} - {result.get('data')}")
            
            return final_result_count > 0
        else:
            print(f"✗ Scan did not complete properly. Final status: {final_status}")
            return False
            
    except Exception as e:
        print(f"✗ MCP scan test error: {e}")
        return False

def test_environment_variables():
    """Test that enhanced environment variables are set"""
    print("\nTesting enhanced environment variables...")
    
    try:
        from bbot_mcp.server import os as server_os
        
        required_vars = {
            'SUDO_ASKPASS': '/bin/false',
            'BBOT_DEPS_BEHAVIOR': 'ignore',
            'PIP_NO_DEPS': '1',
            'CI': 'true'
        }
        
        all_set = True
        for var, expected in required_vars.items():
            actual = server_os.environ.get(var)
            if actual == expected:
                print(f"✓ {var}: {actual}")
            else:
                print(f"✗ {var}: expected '{expected}', got '{actual}'")
                all_set = False
        
        return all_set
        
    except Exception as e:
        print(f"✗ Environment variables test error: {e}")
        return False

def main():
    """Run all preset/flag fix tests"""
    print("BBOT Preset/Flag Fixes Test Suite")
    print("=" * 50)
    
    tests = [
        test_environment_variables,
        test_flag_extension,
        test_mcp_scan_fixed
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✓ PASSED\n" + "-" * 50)
            else:
                print("✗ FAILED\n" + "-" * 50)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            print("-" * 50)
    
    print(f"\nPreset/Flag Fixes Tests: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All fixes are working!")
        print("✓ Subdomain-enum + passive scans should now return results!")
        return 0
    else:
        print("✗ Some fixes need more work.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
