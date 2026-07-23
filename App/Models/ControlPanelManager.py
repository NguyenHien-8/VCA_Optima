# App/Models/ControlPanelManager.py
class ControlPanelManager:
    def __init__(self, hardware_manager):
        self.hardware_manager = hardware_manager

    # --- INTERNAL HELPERS (DATA STANDARDIZATION) ---
    def _normalize_speed(self, speed_input):
        """Converts speed input (text/int) to protocol value."""
        txt = str(speed_input).strip().lower()
        mapping = {
            "slow": 50,
            "medium": 150,
            "fast": 300
        }
        if txt in mapping:
            return mapping[txt]
        
        try:
            val = int(float(txt))
            return max(0, val)
        except ValueError:
            return 100 

    def _normalize_distance(self, dist_input):
        """Converts a space input (text/int) to a protocol value."""
        try:
            return int(float(dist_input))
        except ValueError:
            return 0

    def _send_packet(self, direction: str, distance: int, speed: int, stop_step: int):
        """
        Protocol: #{direction},{distance},{speed},{stop_step}!
        """
        # 1. Check if Hardware Manager exists
        if not self.hardware_manager:
            return False, "HardwareManager system is not initialized."

        # 2. Check the physical connection
        if not self.hardware_manager.is_connected():
            return False, "Device is not connected. Please check USB connection."
        
        # 3. Encapsulate commands
        # Format: #CCW,50,150,0!
        packet = f"#{direction},{distance},{speed},{stop_step}!"
        
        # 4. Send command
        try:
            print(f"[ControlPanelManager] Sending Packet: {packet}")
            return self.hardware_manager.send_serial_command(packet)
        except Exception as e:
            print(f"[ControlPanelManager] Error sending packet: {e}")
            return False, f"Transmission Error: {str(e)}"

    # --- PUBLIC API FOR DIALOGS ---  
    def request_move_up(self, height_raw, speed_raw):
        """Handling Upward Requests (CCW)"""
        dist = self._normalize_distance(height_raw)
        speed = self._normalize_speed(speed_raw)
        return self._send_packet("CCW", dist, speed, 0)

    def request_move_down(self, height_raw, speed_raw):
        """Handling Downward Requests (CW)"""
        dist = self._normalize_distance(height_raw)
        speed = self._normalize_speed(speed_raw)
        return self._send_packet("CW", dist, speed, 0)

    def request_stop(self):
        """Send an emergency stop order."""
        # Stop Protocol: CW, 0, 0, -1
        return self._send_packet("CW", 0, 0, -1)
