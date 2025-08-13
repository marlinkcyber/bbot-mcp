#!/usr/bin/env python3

"""Test potential workarounds for sslcert module on macOS"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_environment_workarounds():
    """Test various environment variable workarounds"""
    print("Testing environment variable workarounds...")
    
    workarounds = [
        {'BBOT_SKIP_APT': '1'},
        {'BBOT_FORCE_DEPS': '1'},
        {'APT_AVAILABLE': '0'},
        {'OPENSSL_DIR': '/opt/homebrew/opt/openssl@3'},
        {'HOMEBREW_PREFIX': '/opt/homebrew'},
        {'DISABLE_DEPENDENCY_CHECK': '1'}
    ]
    
    for i, env_vars in enumerate(workarounds):
        print(f"\nWorkaround {i+1}: {env_vars}")
        
        # Set environment variables
        original_env = {}
        for key, value in env_vars.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value
        
        try:
            from bbot import Scanner, Preset
            preset = Preset()
            preset.add_module('sslcert')
            
            config = {
                'deps': {'behavior': 'ignore'},
                'force': True,
                'install_deps': False,
                'check_deps': False
            }
            
            scanner = Scanner('example.com', preset=preset, config=config)
            result = len(scanner.preset.scan_modules)
            print(f"  Result: {result} modules loaded")
            
            if result > 0:
                print(f"  ✓ SUCCESS with {env_vars}")
                return True
                
        except Exception as e:
            print(f"  ✗ Error: {str(e)[:100]}...")
        
        finally:
            # Restore environment
            for key in env_vars:
                if original_env[key] is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = original_env[key]
    
    return False

def test_config_workarounds():
    """Test various configuration workarounds"""
    print("\nTesting configuration workarounds...")
    
    configs = [
        {
            'deps': {'behavior': 'ignore'},
            'force': True,
            'dry_run': True
        },
        {
            'deps': {'behavior': 'ignore'}, 
            'skip_setup': True,
            'force': True
        },
        {
            'deps': {'behavior': 'skip'},
            'force_all_modules': True,
            'ignore_setup_errors': True
        }
    ]
    
    from bbot import Scanner, Preset
    
    for i, config in enumerate(configs):
        print(f"Config {i+1}: {config}")
        try:
            preset = Preset()
            preset.add_module('sslcert')
            
            scanner = Scanner('example.com', preset=preset, config=config)
            result = len(scanner.preset.scan_modules)
            print(f"  Result: {result} modules loaded")
            
            if result > 0:
                print(f"  ✓ SUCCESS with config {i+1}")
                return True
                
        except Exception as e:
            print(f"  ✗ Error: {str(e)[:50]}...")
    
    return False

def test_module_modification():
    """Test if we can modify how sslcert dependencies are handled"""
    print("\nTesting module modification approach...")
    
    try:
        # Try to import the module class directly
        from bbot.modules.sslcert import sslcert
        
        print(f"Original deps_apt: {sslcert.deps_apt}")
        print(f"Original deps_pip: {sslcert.deps_pip}")
        
        # Temporarily modify the class to remove APT dependency
        original_apt_deps = sslcert.deps_apt
        sslcert.deps_apt = []  # Remove APT dependency
        
        from bbot import Scanner, Preset
        preset = Preset()
        preset.add_module('sslcert')
        
        config = {'deps': {'behavior': 'ignore'}, 'force': True}
        scanner = Scanner('example.com', preset=preset, config=config)
        result = len(scanner.preset.scan_modules)
        
        print(f"  Result with modified deps_apt: {result} modules loaded")
        
        # Restore original
        sslcert.deps_apt = original_apt_deps
        
        return result > 0
        
    except Exception as e:
        print(f"  ✗ Module modification error: {e}")
        return False

def main():
    """Test all workarounds"""
    print("BBOT sslcert macOS Workaround Tests")
    print("=" * 50)
    
    tests = [
        test_environment_workarounds,
        test_config_workarounds,
        test_module_modification
    ]
    
    for test in tests:
        try:
            if test():
                print(f"\n✓ {test.__name__} found a working solution!")
                return 0
        except Exception as e:
            print(f"\n✗ {test.__name__} failed: {e}")
    
    print("\n✗ No workarounds successful")
    print("Recommendation: Keep sslcert in exclude_modules list")
    return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)