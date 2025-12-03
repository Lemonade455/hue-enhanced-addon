#!/usr/bin/env python3
"""
Automatic integration patcher for Enhanced Security
This patches diyHue's HueEmulator3.py to enable 3-LED security
"""
import os
import sys

def patch_hue_emulator():
    """Patch HueEmulator3.py with enhanced security."""
    
    emulator_path = "/opt/hue-emulator/HueEmulator3.py"
    
    if not os.path.exists(emulator_path):
        print(f"❌ HueEmulator3.py not found at {emulator_path}")
        return False
    
    print("📝 Reading HueEmulator3.py...")
    with open(emulator_path, 'r') as f:
        content = f.read()
    
    # Check if already patched
    if "initialize_enhanced_security" in content:
        print("✅ Already patched!")
        return True
    
    print("🔧 Patching HueEmulator3.py...")
    
    # Add import at the top (after other imports)
    import_patch = """
# Enhanced Security Integration
try:
    from flaskUI.restful_enhanced import initialize_enhanced_security
    ENHANCED_SECURITY = True
    print("✅ Enhanced Security Module Loaded")
except ImportError as e:
    ENHANCED_SECURITY = False
    print(f"⚠️  Enhanced Security not available: {e}")
"""
    
    # Find where to insert import (after main imports)
    lines = content.split('\n')
    import_index = 0
    for i, line in enumerate(lines):
        if line.startswith('from') or line.startswith('import'):
            import_index = i + 1
    
    lines.insert(import_index, import_patch)
    
    # Add initialization after Flask app creation
    init_patch = """
    # Initialize Enhanced Security
    if ENHANCED_SECURITY:
        try:
            initialize_enhanced_security(app, bridgeConfig)
        except Exception as e:
            print(f"⚠️  Failed to initialize enhanced security: {e}")
"""
    
    # Find where Flask app is created
    for i, line in enumerate(lines):
        if 'app = Flask' in line or 'Flask(__name__)' in line:
            # Insert after app creation
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith('#'):
                j += 1
            lines.insert(j, init_patch)
            break
    
    # Write patched content
    content_patched = '\n'.join(lines)
    
    # Backup original
    backup_path = emulator_path + ".original"
    if not os.path.exists(backup_path):
        print(f"💾 Creating backup: {backup_path}")
        with open(backup_path, 'w') as f:
            f.write(content)
    
    print(f"✍️  Writing patched file...")
    with open(emulator_path, 'w') as f:
        f.write(content_patched)
    
    print("✅ HueEmulator3.py patched successfully!")
    print("")
    print("Enhanced Security Features:")
    print("  - 3-LED indicator system")
    print("  - Configurable timeout")
    print("  - Real-time status API")
    print("")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("diyHue Enhanced Security Patcher")
    print("=" * 60)
    print("")
    
    if patch_hue_emulator():
        print("✅ Patching complete!")
        sys.exit(0)
    else:
        print("❌ Patching failed!")
        sys.exit(1)
