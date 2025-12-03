"""
Enhanced Authentication Handler for diyHue
This patches the original restful.py to add 3-LED security

INTEGRATION INSTRUCTIONS:
1. Place this file at: diyhue-enhanced/rootfs/opt/hue-emulator/flaskUI/restful_enhanced.py
2. Modify the original HueEmulator3.py to import this module
3. The security module will be automatically loaded
"""
import logging
from datetime import datetime
import uuid
import hashlib

_LOGGER = logging.getLogger(__name__)

# Import the enhanced security module
try:
    from services.security import enhanced_security
    ENHANCED_SECURITY_AVAILABLE = True
    _LOGGER.info("✅ Enhanced Security Module Loaded")
except ImportError:
    ENHANCED_SECURITY_AVAILABLE = False
    _LOGGER.warning("⚠️  Enhanced Security Module not found - using fallback")


def patch_authentication(original_auth_function):
    """
    Decorator to patch the original authentication function.
    This wraps the original diyHue authentication with enhanced security.
    """
    def enhanced_auth_wrapper(data, bridge_config):
        """Enhanced authentication with 3-LED security check."""
        device_type = data.get("devicetype", "unknown#unknown")
        generate_client_key = data.get("generateclientkey", False)
        
        _LOGGER.info(f"🔐 Authentication request from: {device_type}")
        
        # Check enhanced security if available
        if ENHANCED_SECURITY_AVAILABLE:
            if not enhanced_security.is_button_pressed():
                _LOGGER.warning(f"❌ Link button not pressed for: {device_type}")
                _LOGGER.info("💡 User must press link button (all 3 LEDs must be blinking)")
                _LOGGER.info("   Go to: http://YOUR_IP/#linkbutton and click ACTIVATE")
                
                return [{
                    "error": {
                        "type": 101,
                        "address": "",
                        "description": "link button not pressed"
                    }
                }]
            
            # Get LED status for logging
            status = enhanced_security.get_status()
            _LOGGER.info(f"✅ Link button active!")
            _LOGGER.info(f"💡 LED 1: {'ON' if status['leds']['led1'] else 'OFF'}")
            _LOGGER.info(f"💡 LED 2: {'ON' if status['leds']['led2'] else 'OFF'}")
            _LOGGER.info(f"💡 LED 3: {'ON' if status['leds']['led3'] else 'OFF'}")
            _LOGGER.info(f"⏱️  Time remaining: {status['time_remaining']}s")
        else:
            # Fallback to original behavior if enhanced security not available
            _LOGGER.info("⚠️  Using fallback authentication (enhanced security disabled)")
            
        # Generate username
        username = hashlib.md5((device_type + str(uuid.uuid4())).encode()).hexdigest()
        
        # Create whitelist entry
        if "whitelist" not in bridge_config:
            bridge_config["whitelist"] = {}
        
        whitelist_entry = {
            "last use date": str(datetime.now()),
            "create date": str(datetime.now()),
            "name": device_type
        }
        
        # Add client key if requested (for entertainment mode)
        if generate_client_key:
            client_key = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:32]
            whitelist_entry["clientkey"] = client_key
            _LOGGER.info(f"🔑 Generated client key for entertainment mode")
        
        bridge_config["whitelist"][username] = whitelist_entry
        
        # Build response
        response = {
            "success": {
                "username": username
            }
        }
        
        if generate_client_key:
            response["success"]["clientkey"] = client_key
        
        _LOGGER.info(f"✅ Authentication successful!")
        _LOGGER.info(f"   Username: {username}")
        _LOGGER.info(f"   Device: {device_type}")
        
        return [response]
    
    return enhanced_auth_wrapper


def add_enhanced_routes(app, bridge_config):
    """
    Add enhanced routes to Flask app for LED status and button control.
    Call this from HueEmulator3.py after Flask app is created.
    """
    from flask import jsonify, request
    
    if not ENHANCED_SECURITY_AVAILABLE:
        _LOGGER.warning("⚠️  Enhanced security not available - routes not added")
        return
    
    @app.route('/api/linkbutton/press', methods=['POST', 'GET'])
    def handle_linkbutton_press():
        """Handle link button press from web UI or API."""
        result = enhanced_security.press_button()
        
        return jsonify({
            'success': result['success'],
            'message': result['message'],
            'leds': result['leds'],
            'timeout': result['timeout'],
            'time_remaining': result.get('time_remaining', result['timeout'])
        }), 200
    
    @app.route('/api/linkbutton/status', methods=['GET'])
    def handle_linkbutton_status():
        """Get current link button and LED status."""
        status = enhanced_security.get_status()
        return jsonify(status), 200
    
    @app.route('/api/linkbutton/reset', methods=['POST'])
    def handle_linkbutton_reset():
        """Reset link button state (for testing)."""
        enhanced_security.reset()
        return jsonify({
            'success': True,
            'message': 'Link button reset'
        }), 200
    
    _LOGGER.info("✅ Enhanced routes added:")
    _LOGGER.info("   - POST /api/linkbutton/press")
    _LOGGER.info("   - GET  /api/linkbutton/status")
    _LOGGER.info("   - POST /api/linkbutton/reset")


# Monkey-patch the linkbutton in bridge config
def patch_bridge_linkbutton(bridge_config):
    """
    Patch the bridge config linkbutton to use enhanced security.
    This makes the existing webUI button work with enhanced security.
    """
    if not ENHANCED_SECURITY_AVAILABLE:
        return
    
    # Store original linkbutton if it exists
    if "linkbutton" not in bridge_config:
        bridge_config["linkbutton"] = {"lastpress": 0}
    
    # Create a property-like wrapper
    class EnhancedLinkButton:
        def __getitem__(self, key):
            if key == "lastpress":
                # Check if enhanced security button is pressed
                if enhanced_security.is_button_pressed():
                    import time
                    return int(time.time())  # Return current time if button pressed
                return 0  # Return 0 if not pressed (expired)
            return bridge_config["linkbutton"].get(key, 0)
        
        def __setitem__(self, key, value):
            if key == "lastpress":
                # When webUI sets lastpress, activate enhanced security
                _LOGGER.info("🔘 Link button activated via webUI")
                enhanced_security.press_button()
            bridge_config["linkbutton"][key] = value
        
        def get(self, key, default=None):
            return self[key] if key in ["lastpress"] else default
    
    # Replace linkbutton with enhanced version
    bridge_config["linkbutton"] = EnhancedLinkButton()
    _LOGGER.info("✅ Bridge linkbutton patched with enhanced security")


# ============================================================================
# INTEGRATION HELPER FUNCTION
# ============================================================================

def initialize_enhanced_security(app, bridge_config):
    """
    Main initialization function to call from HueEmulator3.py
    
    Usage in HueEmulator3.py:
    
    from flaskUI.restful_enhanced import initialize_enhanced_security
    
    # After Flask app is created and bridge_config is loaded:
    initialize_enhanced_security(app, bridge_config)
    """
    if not ENHANCED_SECURITY_AVAILABLE:
        _LOGGER.warning("=" * 60)
        _LOGGER.warning("⚠️  ENHANCED SECURITY NOT AVAILABLE")
        _LOGGER.warning("   security.py not found in services/")
        _LOGGER.warning("   Falling back to standard diyHue authentication")
        _LOGGER.warning("=" * 60)
        return False
    
    _LOGGER.info("=" * 60)
    _LOGGER.info("🔐 INITIALIZING ENHANCED SECURITY")
    _LOGGER.info("=" * 60)
    
    # Add enhanced routes
    add_enhanced_routes(app, bridge_config)
    
    # Patch linkbutton behavior
    patch_bridge_linkbutton(bridge_config)
    
    _LOGGER.info("=" * 60)
    _LOGGER.info("✅ ENHANCED SECURITY INITIALIZED")
    _LOGGER.info("   - 3-LED indicator system active")
    _LOGGER.info("   - Button timeout: {}s".format(
        enhanced_security.button_timeout
    ))
    _LOGGER.info("   - Security: {}".format(
        "ENABLED" if enhanced_security.security_enabled else "DISABLED"
    ))
    _LOGGER.info("=" * 60)
    _LOGGER.info("")
    _LOGGER.info("🔗 Link Button Access:")
    _LOGGER.info("   Web UI: http://YOUR_IP/#linkbutton")
    _LOGGER.info("   API: POST http://YOUR_IP/api/linkbutton/press")
    _LOGGER.info("   Status: GET http://YOUR_IP/api/linkbutton/status")
    _LOGGER.info("")
    
    return True


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

"""
To integrate this into diyHue, add to HueEmulator3.py:

# Near the top, after imports:
try:
    from flaskUI.restful_enhanced import initialize_enhanced_security
    ENHANCED_SECURITY = True
except ImportError:
    ENHANCED_SECURITY = False

# After Flask app is created (around line where app = Flask(__name__)):
if ENHANCED_SECURITY:
    initialize_enhanced_security(app, bridge_config)

# That's it! The enhanced security will now be active.
"""
