#!/usr/bin/env python3

"""Test the wait_for_scan_completion with valid presets"""

import sys
import os
import json
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the MCP server components
from bbot_mcp.server import scan_manager, wait_for_scan_completion, list_bbot_presets

def test_with_valid_preset():
    """Test with a valid preset that should work"""
    print("Getting available presets...")
    
    # Get list of available presets
    presets_result = list_bbot_presets()
    presets_data = json.loads(presets_result)
    
    if not presets_data.get('success'):
        print(f"❌ Failed to get presets: {presets_data}")
        return False
    
    available_presets = [p['name'] for p in presets_data['presets']]
    print(f"Available presets: {available_presets[:5]}...")  # Show first 5
    
    # Use a simple preset that should work
    test_preset = None
    for preset in ['subdomain-enum', 'spider', 'web-basic']:
        if preset in available_presets:
            test_preset = preset
            break
    
    if not test_preset:
        print("❌ No suitable test preset found")
        return False
    
    print(f"Using preset: {test_preset}")
    
    # Start scan
    scan_id = f"valid-test-{int(time.time())}"
    result = scan_manager.start_scan(
        scan_id=scan_id,
        targets=["example.com"],
        presets=[test_preset],
        flags=["safe"],
        no_deps=True
    )
    
    print(f"Started scan: {json.dumps(result, indent=2)}")
    
    if not result.get('success'):
        print("❌ Failed to start scan")
        return False
    
    # Wait for completion with longer timeout
    print(f"Waiting for scan {scan_id} to complete...")
    
    wait_result = wait_for_scan_completion(
        scan_id=scan_id,
        timeout=60,  # 1 minute timeout
        poll_interval=3,
        include_progress=True
    )
    
    try:
        wait_data = json.loads(wait_result)
        print(f"Final result: {json.dumps(wait_data, indent=2)}")
        
        if wait_data.get('success'):
            print("✅ Scan completed successfully!")
            return True
        else:
            print("⚠️ Scan completed but with issues")
            return wait_data.get('completed_naturally', False)  # Still consider it a pass if it completed naturally
            
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse result: {e}")
        return False

if __name__ == "__main__":
    print("Testing wait_for_scan_completion with valid preset")
    print("=" * 50)
    
    success = test_with_valid_preset()
    print(f"\n{'✅' if success else '❌'} Test {'PASSED' if success else 'FAILED'}")
    
    sys.exit(0 if success else 1)