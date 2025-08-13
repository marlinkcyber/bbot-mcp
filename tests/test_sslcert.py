
import os
os.environ["SUDO_ASKPASS"] = "/bin/false"
os.environ["DEBIAN_FRONTEND"] = "noninteractive"

from bbot import Scanner, Preset

preset = Preset()
preset.add_module("sslcert")

try:
    # Try with most aggressive no-deps config
    config = {
        "deps": {"behavior": "ignore"},
        "force": True,
        "install_deps": False,
        "check_deps": False,
        "retry_deps": False
    }
    scanner = Scanner("example.com", preset=preset, config=config)
    print(f"SUCCESS: Scanner created with {len(scanner.preset.scan_modules)} modules")
    
    if len(scanner.preset.scan_modules) == 0:
        print("Module failed to load - checking why...")
        # Check if module is in available modules
        all_modules = list(preset.module_loader.all_module_choices)
        if "sslcert" in all_modules:
            print("sslcert is available but failed to load")
        else:
            print("sslcert not found in available modules")
            
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
