#!/usr/bin/env python3

"""Test that the scan result fixes work properly"""

import json
import sys
import os
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_module_configuration():
    """Test that modules are properly configured"""
    print("Testing module configuration fixes...")
    
    try:
        from bbot import Preset
        
        preset = Preset()
        preset.add_module('httpx')
        
        print(f"✓ Module added successfully: {preset.modules}")
        print(f"  Scan modules: {preset.scan_modules}")
        
        return 'httpx' in preset.modules
        
    except Exception as e:
        print(f"✗ Module configuration error: {e}")
        return False

def test_scan_with_results():
    """Test that scans now return results properly"""
    print("\nTesting scan with result fixes...")
    
    try:
        from bbot_mcp.server import start_bbot_scan, get_scan_results, get_scan_status
        
        # Start scan with httpx module
        result = start_bbot_scan(
            targets="scanme.nmap.org",
            modules="httpx",
            no_deps=True
        )
        
        data = json.loads(result)
        if not data.get('success'):
            print(f"✗ Failed to start scan: {data.get('error')}")
            return False
        
        scan_id = data.get('scan_id')
        print(f"✓ Scan started: {scan_id}")
        
        # Wait for scan to complete
        max_wait = 30
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status_result = get_scan_status(scan_id)
            status_data = json.loads(status_result)
            
            if status_data.get('success'):
                scan_info = status_data.get('scan', {})
                status = scan_info.get('status')
                result_count = scan_info.get('result_count', 0)
                
                print(f"  Status: {status}, Results: {result_count}")
                
                if status in ['completed', 'error']:
                    break
            
            time.sleep(2)
        
        # Test getting results (this should not fail with JSON serialization error)
        results_result = get_scan_results(scan_id, limit=10)
        results_data = json.loads(results_result)
        
        if results_data.get('success'):
            results = results_data.get('results', [])
            total_count = results_data.get('total_count', 0)
            
            print(f"✓ Results retrieved successfully: {total_count} total results")
            
            # Show sample results
            for i, result in enumerate(results[:3]):
                print(f"  Result {i+1}: {result.get('type')} - {result.get('data')}")
                print(f"           Tags: {result.get('tags')}, Module: {result.get('module')}")
            
            return total_count > 0
        else:
            print(f"✗ Failed to get results: {results_data.get('error')}")
            return False
            
    except Exception as e:
        print(f"✗ Scan test error: {e}")
        return False

def test_httpx_specific():
    """Test specifically with httpx module which should produce results"""
    print("\nTesting httpx module specifically...")
    
    try:
        from bbot import Scanner, Preset
        
        preset = Preset()
        preset.add_module('httpx')
        
        config = {'deps': {'behavior': 'ignore'}}
        scanner = Scanner('scanme.nmap.org', preset=preset, config=config)
        
        print(f"Scanner modules: {scanner.preset.scan_modules}")
        
        # Run a quick scan to see if httpx actually runs
        event_count = 0
        httpx_events = 0
        
        for event in scanner.start():
            event_count += 1
            module_str = str(getattr(event, 'module', ''))
            
            if 'httpx' in module_str.lower():
                httpx_events += 1
                print(f"  HTTPX Event: {event.type} - {event.data}")
            
            # Stop after reasonable number for testing
            if event_count >= 20:
                break
        
        print(f"✓ Total events: {event_count}, HTTPX events: {httpx_events}")
        return event_count > 0
        
    except Exception as e:
        print(f"✗ HTTPX test error: {e}")
        return False

def main():
    """Run all fix tests"""
    print("BBOT Scan Fixes Test Suite")
    print("=" * 40)
    
    tests = [
        test_module_configuration,
        test_httpx_specific,
        test_scan_with_results
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✓ PASSED\n" + "-" * 40)
            else:
                print("✗ FAILED\n" + "-" * 40)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            print("-" * 40)
    
    print(f"\nScan Fixes Tests: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All scan fixes are working!")
        print("✓ MCP server should now return proper scan results!")
        return 0
    else:
        print("✗ Some scan fixes failed.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
