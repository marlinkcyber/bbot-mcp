#!/usr/bin/env python3

"""Test script to verify bbot imports work correctly"""

import sys

def test_bbot_imports():
    """Test that we can import bbot correctly"""
    try:
        print("Testing bbot imports...")
        import bbot
        print(f"✓ bbot imported successfully, version: {getattr(bbot, '__version__', 'unknown')}")
        
        from bbot import Scanner
        print("✓ Scanner imported successfully")
        
        from bbot import Preset
        print("✓ Preset imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_mcp_imports():
    """Test that we can import MCP correctly"""
    try:
        print("\nTesting MCP imports...")
        from mcp.server.fastmcp import FastMCP
        print("✓ FastMCP imported successfully")
        
        # Try creating a simple MCP instance
        mcp = FastMCP("Test Server")
        print("✓ FastMCP instance created successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ MCP import error: {e}")
        return False
    except Exception as e:
        print(f"✗ MCP unexpected error: {e}")
        return False

def test_preset_functionality():
    """Test basic preset functionality"""
    try:
        print("\nTesting Preset functionality...")
        from bbot import Preset
        
        preset = Preset()
        print("✓ Preset instance created")
        
        # Test getting all presets
        all_presets = preset.all_presets
        print(f"✓ Found {len(all_presets)} presets")
        
        # Test getting module choices
        all_modules = list(preset.module_loader.all_module_choices)
        print(f"✓ Found {len(all_modules)} modules")
        
        return True
        
    except Exception as e:
        print(f"✗ Preset functionality error: {e}")
        return False

def main():
    """Run all tests"""
    print("BBOT MCP Server Import Test")
    print("=" * 40)
    
    tests = [
        test_bbot_imports,
        test_mcp_imports,
        test_preset_functionality
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
    print(f"Import Tests: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All imports working correctly!")
        return 0
    else:
        print("✗ Some imports failed.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)