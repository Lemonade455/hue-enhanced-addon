"""
Enhanced Security Module for diyHue
Implements 3-LED button press authentication like official Philips Hue Bridge
"""
import time
import threading
import logging
import os

_LOGGER = logging.getLogger(__name__)

class EnhancedSecurity:
    """Handle enhanced button press security with LED indicators."""
    
    def __init__(self):
        self.button_pressed = False
        self.button_press_time = 0
        self.button_timeout = int(os.getenv('BUTTON_TIMEOUT', 30))
        self.led_indicator_enabled = os.getenv('LED_INDICATOR', 'true').lower() == 'true'
        self.security_enabled = os.getenv('BUTTON_SECURITY', 'true').lower() == 'true'
        self.led_state = {
            'led1': False,
            'led2': False,
            'led3': False
        }
        self._cleanup_thread = None
        
    def press_button(self):
        """
        Simulate physical button press with LED indicators.
        Returns dict with LED states and timing info.
        """
        if not self.security_enabled:
            self.button_pressed = True
            self.button_press_time = time.time()
            _LOGGER.info("⚡ Link button activated (security disabled)")
            return {
                'success': True,
                'timeout': self.button_timeout,
                'leds': self.led_state,
                'message': 'Link button activated'
            }
        
        self.button_pressed = True
        self.button_press_time = time.time()
        
        # Activate LED indicators (simulate 3 LEDs blinking)
        self.led_state = {
            'led1': True,
            'led2': True,
            'led3': True
        }
        
        _LOGGER.info("🔘 Link button pressed!")
        _LOGGER.info("💡 All 3 LEDs now blinking")
        _LOGGER.info(f"⏱️  {self.button_timeout} seconds to complete pairing")
        
        # Start cleanup timer
        if self._cleanup_thread:
            self._cleanup_thread.cancel()
        
        self._cleanup_thread = threading.Timer(self.button_timeout, self._button_timeout)
        self._cleanup_thread.start()
        
        return {
            'success': True,
            'timeout': self.button_timeout,
            'leds': self.led_state,
            'time_remaining': self.button_timeout,
            'message': f'Link button activated. All 3 LEDs blinking. Complete pairing within {self.button_timeout} seconds.'
        }
    
    def is_button_pressed(self):
        """
        Check if button is currently in pressed state.
        Returns True if pressed and not expired.
        """
        if not self.button_pressed:
            return False
        
        elapsed = time.time() - self.button_press_time
        
        if elapsed > self.button_timeout:
            self._button_timeout()
            return False
        
        return True
    
    def get_status(self):
        """Get current button and LED status."""
        if not self.button_pressed:
            return {
                'button_pressed': False,
                'leds': {'led1': False, 'led2': False, 'led3': False},
                'time_remaining': 0,
                'message': 'Link button not pressed'
            }
        
        elapsed = time.time() - self.button_press_time
        remaining = max(0, self.button_timeout - elapsed)
        
        if remaining == 0:
            self._button_timeout()
            return {
                'button_pressed': False,
                'leds': {'led1': False, 'led2': False, 'led3': False},
                'time_remaining': 0,
                'message': 'Link button timeout expired'
            }
        
        return {
            'button_pressed': True,
            'leds': self.led_state,
            'time_remaining': int(remaining),
            'message': f'Link button active. {int(remaining)} seconds remaining.'
        }
    
    def _button_timeout(self):
        """Handle button press timeout."""
        _LOGGER.info("⏱️  Link button timeout expired")
        _LOGGER.info("💡 All LEDs off")
        
        self.button_pressed = False
        self.button_press_time = 0
        self.led_state = {
            'led1': False,
            'led2': False,
            'led3': False
        }
    
    def reset(self):
        """Reset button state (for testing or manual reset)."""
        if self._cleanup_thread:
            self._cleanup_thread.cancel()
        self._button_timeout()
        _LOGGER.info("🔄 Link button state reset")

# Global instance
enhanced_security = EnhancedSecurity()
