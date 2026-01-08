import pyvisa

class PowerSupply:
    def __init__(self, ip: str):
        self.ip = ip
        rm = pyvisa.ResourceManager()
        # Add error handling for connection
        try:
            self.dev = rm.open_resource(f"TCPIP::{self.ip}::INSTR")
            self.dev.timeout = 3000  # ms
            
            # Safe initialization
            for ch in [1, 2, 3]:
                self.disable(ch)
        except Exception as e:
            print(f"Failed to connect to Power Supply at {ip}: {e}")
            raise

    def enable(self, channel: int):
        self.dev.write(f":OUTP CH{channel}, ON")

    def disable(self, channel: int):
        self.dev.write(f":OUTP CH{channel}, OFF")

    def set_voltage(self, channel: int, volts: float):
        self.dev.write(f":SOUR{channel}:VOLT {volts}")

    # --- FIX: Added 'channel' argument here ---
    def read_voltage(self, channel: int) -> float:
        return float(self.dev.query(f":MEAS:VOLT? CH{channel}"))

    # --- FIX: Added 'channel' argument here ---
    def read_current(self, channel: int) -> float:
        return float(self.dev.query(f":MEAS:CURR? CH{channel}"))

    def close(self):
        if hasattr(self, 'dev'):
            self.dev.close()
