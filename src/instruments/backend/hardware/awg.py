# tg2511a_controller.py
# Python class for controlling Tektronix TG2511A AWG via PyVISA

import pyvisa
import time
import numpy as np
from typing import Optional, Union

AWG_RESSOURCE = "TCPIP0::192.168.1.209::9221::SOCKET"

class TG2511A:
    """
    Controller class for Tektronix TG2511A Function/Arbitrary Generator
    
    Supports control via USB, LAN, or GPIB interfaces using PyVISA.
    Provides methods for waveform generation, modulation, sweep, and burst modes.
    """
    
    # Waveform types
    WAVEFORMS = ['SINE', 'SQUARE', 'RAMP', 'PULSE', 'NOISE', 
                 'PRBSPN7', 'PRBSPN9', 'PRBSPN11', 'PRBSPN15', 
                 'PRBSPN20', 'PRBSPN23', 'ARB1', 'ARB2', 'ARB3', 'ARB4']
    
    # Modulation types
    MOD_TYPES = ['OFF', 'AM', 'FM', 'PM', 'FSK', 'SUM', 'BPSK', 'PWM']
    
    def __init__(self, resource_string: str):
        """
        Initialize connection to TG2511A AWG
        
        Args:
            resource_string: VISA resource string, e.g.:
                - 'TCPIP0::192.168.1.100::9221::SOCKET' (LAN)
                - 'USB0::0x1234::0x5678::SN123456::INSTR' (USB)
                - 'GPIB0::5::INSTR' (GPIB, default address is 5)
        """
        self.rm = pyvisa.ResourceManager()
        try:
            self.instr = self.rm.open_resource(resource_string)
            
            # Configure for LAN socket communication if using TCPIP SOCKET
            if 'SOCKET' in resource_string:
                self.instr.read_termination = '\n'
                self.instr.write_termination = '\n'
            else:
                self.instr.read_termination = '\r\n'
                self.instr.write_termination = '\n'
            
            self.instr.timeout = 5000  # 5 second timeout
            
            # Verify connection
            idn = self.query('*IDN?')
            print(f"Connected to: {idn}")
            
        except Exception as e:
            print(f"Error connecting to instrument: {e}")
            raise
    
    def write(self, command: str):
        """Send command to instrument"""
        self.instr.write(command)
    
    def query(self, command: str) -> str:
        """Send query and return response"""
        return self.instr.query(command).strip()
    
    def close(self):
        """Close connection to instrument"""
        self.instr.close()
        self.rm.close()
    
    # Basic waveform control
    
    def set_waveform(self, waveform: str):
        """Set output waveform type"""
        if waveform.upper() not in self.WAVEFORMS:
            raise ValueError(f"Invalid waveform. Must be one of {self.WAVEFORMS}")
        self.write(f"WAVE {waveform.upper()}")
    
    def set_frequency(self, freq_hz: float):
        """Set output frequency in Hz (1µHz to 25MHz)"""
        self.write(f"FREQ {freq_hz}")
    
    def set_amplitude(self, amplitude_vpp: float):
        """Set output amplitude in Vpp (0.01 to 10 Vpp into 50Ω)"""
        self.write(f"AMPL {amplitude_vpp}")
    
    def set_offset(self, offset_v: float):
        """Set DC offset in volts (±10V)"""
        self.write(f"DCOFFS {offset_v}V")
    
    def set_phase(self, phase_deg: float):
        """Set waveform phase (-360 to +360 degrees)"""
        self.write(f"PHASE {phase_deg}DEG")
    
    def output_on(self):
        """Turn output ON"""
        self.write("OUTPUT ON")
    
    def output_off(self):
        """Turn output OFF"""
        self.write("OUTPUT OFF")
    
    # Sweep
    
    def enable_sweep(self, enable: bool = True):
        """Enable/disable frequency sweep"""
        self.write(f"SWP {'ON' if enable else 'OFF'}")
    
    def set_sweep_range(self, start_hz: float, stop_hz: float):
        """Set sweep start and stop frequencies"""
        self.write(f"SWPFRQSTA {start_hz}HZ")
        self.write(f"SWPFRQSTP {stop_hz}HZ")
    
    def set_sweep_time(self, time_sec: float):
        """Set sweep time (1ms to 500s)"""
        self.write(f"SWPTIM {time_sec}S")
    
    def set_sweep_mode(self, mode: str):
        """Set sweep mode: 'LINEAR' or 'LOG'"""
        self.write(f"SWPTYP {mode.upper()}")
    

    
    # System functions
    
    def reset(self):
        """Reset instrument to default state"""
        self.write("*RST")
        time.sleep(2)  # Wait for reset to complete
    
    def get_errors(self) -> list:
        """Query all errors from error queue (Max 20 to prevent infinite loop)"""
        errors = []
        max_errors = 20
        count = 0
        
        try:
            while count < max_errors:
                err = self.query("SYST:ERR?")
                # Standard SCPI "No error" response starts with +0 or 0
                if err.startswith("+0") or err.startswith("0"): 
                    break
                errors.append(err)
                count += 1
        except Exception as e:
            errors.append(f"Communication error reading logs: {e}")
            
        return errors
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
