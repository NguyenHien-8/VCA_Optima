########################################################
# @file App/Models/Controllers/HardwareConnector.py
# Author: TRAN NGUYEN HIEN
# Email: trannguyenhien29085@gmail.com
########################################################
import sys
import threading
import time

import serial
import serial.tools.list_ports


class HardwareConnector:
    """Thread-safe owner of the application's single serial connection."""

    _instance = None
    _instance_lock = threading.Lock()

    def __new__(cls):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self.serial_connection = None
        self._lock = threading.RLock()
        self._connection_generation = 0
        self._initialized = True
        print("[HardwareConnector] Singleton Instance Created")

    def get_available_ports(self):
        try:
            return sorted(
                (port.device for port in serial.tools.list_ports.comports()),
                key=str.casefold,
            )
        except Exception as exc:
            print(f"[HardwareConnector] Port scan failed: {exc}")
            return []

    def connect(self, port_name, baud_rate):
        target_port = str(port_name).strip()
        if sys.platform.startswith("win"):
            target_port = target_port.upper()
        if not target_port:
            return False, "Serial port is required."

        try:
            target_baud = int(baud_rate)
            if target_baud <= 0:
                raise ValueError
        except (TypeError, ValueError):
            return False, "Baud rate must be a positive integer."

        print(f"[HardwareConnector] Request connect: {target_port} @ {target_baud}")
        with self._lock:
            self._connection_generation += 1
            generation = self._connection_generation
            previous_connection = self.serial_connection
            self.serial_connection = None
        self._close_candidate(previous_connection)
        time.sleep(0.1)

        max_retries = 3
        for attempt in range(max_retries):
            connection = None
            try:
                connection = serial.Serial(
                    port=target_port,
                    baudrate=target_baud,
                    timeout=0.1,
                    write_timeout=0.1,
                    dsrdtr=False,
                    rtscts=False,
                )
                if not connection.is_open:
                    raise serial.SerialException("Port did not open.")
                connection.reset_input_buffer()
                connection.reset_output_buffer()

                with self._lock:
                    cancelled = generation != self._connection_generation
                    if not cancelled:
                        self.serial_connection = connection
                if cancelled:
                    self._close_candidate(connection)
                    return False, "Connection request was cancelled."
                print(
                    f"[HardwareConnector] Connection successful to {target_port}"
                )
                return True, f"Connected to {target_port}"
            except serial.SerialException as exc:
                self._close_candidate(connection)
                message = str(exc)
                print(
                    f"[HardwareConnector] Attempt {attempt + 1} failed: {message}"
                )
                access_denied = (
                    "Access is denied" in message
                    or "PermissionError" in message
                )
                if attempt < max_retries - 1 and access_denied:
                    time.sleep(0.5)
                    with self._lock:
                        if generation != self._connection_generation:
                            return False, "Connection request was cancelled."
                    continue
                return False, f"Serial Error: {message}"
            except Exception as exc:
                self._close_candidate(connection)
                return False, f"Error: {exc}"

        return False, (
            f"Could not open port {target_port} after {max_retries} attempts."
        )

    @staticmethod
    def _close_candidate(connection):
        if connection is not None:
            try:
                connection.close()
            except Exception:
                pass

    def disconnect(self):
        with self._lock:
            self._connection_generation += 1
            connection = self.serial_connection
            self.serial_connection = None
        if connection is None:
            return True, "No active connection"
        try:
            if connection.is_open:
                for method_name in ("cancel_read", "cancel_write"):
                    try:
                        getattr(connection, method_name)()
                    except (
                        AttributeError,
                        OSError,
                        serial.SerialException,
                    ):
                        pass
                connection.close()
            print("[HardwareConnector] Disconnected")
            return True, "Disconnected"
        except Exception as exc:
            return False, str(exc)

    def is_connected(self):
        with self._lock:
            return (
                self.serial_connection is not None
                and self.serial_connection.is_open
            )

    def write_data(self, data_str):
        if not isinstance(data_str, str) or not data_str:
            return False, "Data must be a non-empty string."
        with self._lock:
            try:
                if self.serial_connection and self.serial_connection.is_open:
                    self.serial_connection.write(data_str.encode("utf-8"))
                    return True, "Sent"
                return False, "Not connected"
            except serial.SerialTimeoutException:
                return False, "Write Timeout"
            except Exception as exc:
                self.disconnect()
                return False, str(exc)
