#!/usr/bin/env python3

"""Test the wait_for_scan_completion functionality"""

import sys
import os
import json
import time
import threading

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the MCP server components
from bbot_mcp.server import scan_manager, wait_for_scan_completion

def test_wait_for_completion():
    """Test the wait_for_scan_completion tool"""
    print("Testing wait_for_scan_completion functionality...")
    
    # Start a simple scan
    scan_id = "test-wait-" + str(int(time.time()))
    
    # Start scan with a basic preset that should complete quickly
    result = scan_manager.start_scan(
        scan_id=scan_id,
        targets=["example.com"],
        presets=["passive"],
        flags=["safe"],
        no_deps=True
    )
    
    print(f"Started scan: {json.dumps(result, indent=2)}")
    
    if not result.get('success'):
        print("❌ Failed to start scan")
        return False
    
    # Test wait_for_scan_completion with short timeout for testing
    print(f"\nWaiting for scan {scan_id} to complete (30 second timeout)...")
    
    wait_result = wait_for_scan_completion(
        scan_id=scan_id,
        timeout=30,
        poll_interval=2,
        include_progress=True
    )
    
    print(f"Wait result: {wait_result}")
    
    # Parse the JSON result
    try:
        wait_data = json.loads(wait_result)
        
        if wait_data.get('success'):
            print("✅ Scan completed successfully!")
            print(f"  - Final status: {wait_data.get('final_status')}")
            print(f"  - Total results: {wait_data.get('total_results')}")
            print(f"  - Elapsed time: {wait_data.get('elapsed_seconds')}s")
            
            if wait_data.get('progress_updates'):
                print(f"  - Progress updates: {len(wait_data['progress_updates'])}")
                for update in wait_data['progress_updates'][-3:]:  # Show last 3 updates
                    print(f"    {update['elapsed_seconds']}s: {update['status']} - {update['result_count']} results")
            
            return True
        else:
            print("⚠️ Scan did not complete or timed out")
            print(f"  - Error: {wait_data.get('error', 'Unknown')}")
            print(f"  - Final status: {wait_data.get('final_status', 'unknown')}")
            print(f"  - Timeout reached: {not wait_data.get('completed_naturally', True)}")
            return False
            
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse wait result: {e}")
        print(f"Raw result: {wait_result}")
        return False

def test_invalid_scan_id():
    """Test wait_for_scan_completion with invalid scan ID"""
    print("\nTesting with invalid scan ID...")
    
    result = wait_for_scan_completion(
        scan_id="invalid-scan-id",
        timeout=5,
        poll_interval=1,
        include_progress=False
    )
    
    try:
        data = json.loads(result)
        if not data.get('success') and 'not found' in data.get('error', '').lower():
            print("✅ Correctly handled invalid scan ID")
            return True
        else:
            print(f"❌ Unexpected result for invalid scan ID: {data}")
            return False
    except json.JSONDecodeError:
        print(f"❌ Failed to parse result: {result}")
        return False

def main():
    """Run all tests"""
    print("BBOT wait_for_scan_completion Tool Tests")
    print("=" * 50)
    
    tests = [
        test_wait_for_completion,
        test_invalid_scan_id
    ]
    
    results = []
    for test in tests:
        try:
            success = test()
            results.append(success)
            print(f"{'✅' if success else '❌'} {test.__name__}: {'PASSED' if success else 'FAILED'}")
        except Exception as e:
            print(f"❌ {test.__name__}: ERROR - {e}")
            results.append(False)
        print("-" * 30)
    
    # Summary
    passed = sum(results)
    total = len(results)
    print(f"\nTest Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)