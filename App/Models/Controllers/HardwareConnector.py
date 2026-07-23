import serial
import serial.tools.list_ports
import time

class HardwareConnector:
    _instance = None 

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HardwareConnector, cls).__new__(cls)
            cls._instance._initialized = False 
        return cls._instance

    def __init__(self):
        if getattr(self, '_initialized', False):
            return
            
        self.serial_connection = None
        self._initialized = True 
        print("[HardwareConnector] Singleton Instance Created")

    def get_available_ports(self):
        ports = serial.tools.list_ports.comports()
        port_list = []
        for port in ports:
            port_list.append(port.device)
        return sorted(port_list)

    def connect(self, port_name, baud_rate):
        """
        Always close the old connection and open a new one completely.
        """
        target_port = str(port_name).strip().upper()
        try:
            target_baud = int(baud_rate)
        except ValueError:
            target_baud = 115200

        print(f"[HardwareConnector] Request connect: {target_port} @ {target_baud}")

        # 1. DISCONNECT THE OLD CONNECTION 
        if self.serial_connection:
            if self.serial_connection.is_open:
                print(f"[HardwareConnector] Closing existing connection on {self.serial_connection.port}...")
                self.serial_connection.close()
            self.serial_connection = None
            time.sleep(0.1)

        # 2. NEW CONNECT
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.serial_connection = serial.Serial(
                    port=target_port,
                    baudrate=target_baud,
                    timeout=0.1,       # Read timeout quickly
                    write_timeout=0.1, # Write timeout nhanh tránh treo UI
                    dsrdtr=False,      
                    rtscts=False       
                )
                
                # Double check
                if self.serial_connection.is_open:
                    # Empty the trash buffer when first connecting.
                    self.serial_connection.reset_input_buffer()
                    self.serial_connection.reset_output_buffer()
                    print(f"[HardwareConnector] Connection successful to {target_port}")
                    return True, f"Connected to {target_port}"
            
            except serial.SerialException as e:
                err_msg = str(e)
                print(f"[HardwareConnector] Attempt {attempt + 1} failed: {err_msg}")
                
                if self.serial_connection:
                    self.serial_connection = None
                
                # If you get an "Access Denied" error, it's usually because the OS hasn't released the port yet; wait a little longer.
                if "Access is denied" in err_msg or "PermissionError" in err_msg:
                    time.sleep(0.5) 
                else:
                    return False, f"Serial Error: {err_msg}"
            except Exception as e:
                self.serial_connection = None
                return False, f"Error: {str(e)}"

        return False, f"Could not open port {target_port} after {max_retries} attempts."

    def disconnect(self):
        try:
            if self.serial_connection:
                if self.serial_connection.is_open:
                    self.serial_connection.cancel_read()
                    self.serial_connection.cancel_write()
                    self.serial_connection.close()
                self.serial_connection = None
                print("[HardwareConnector] Disconnected")
                return True, "Disconnected"
            return True, "No active connection"
        except Exception as e:
            self.serial_connection = None
            return False, str(e)

    def is_connected(self):
        return self.serial_connection is not None and self.serial_connection.is_open
    
    def write_data(self, data_str):
        try:
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.write(data_str.encode('utf-8'))
                return True, "Sent"
            return False, "Not connected"
        except serial.SerialTimeoutException:
            return False, "Write Timeout"
        except Exception as e:
            # If there is an error during sending, consider the connection lost.
            self.disconnect()
            return False, str(e)