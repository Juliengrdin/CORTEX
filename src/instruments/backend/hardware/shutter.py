import time
import nidaqmx

class Shutter:
    def __init__(self, device="Dev1", channel="PFI2"):
        self.device = device
        self.channel = channel
        self.task_name = "shutter_red"
        
        # Use try/except to handle case where task name already exists
        try:
            self.task = nidaqmx.Task(self.task_name)
            self.task.do_channels.add_do_chan(f"{self.device}/{self.channel}")
            self.task.write(False)
        except nidaqmx.errors.DaqError as e:
            print(f"DAQ Error: {e}")
            raise

    def open_shutter(self):
        self.task.write(True)

    def close_shutter(self):
        self.task.write(False)
    
    def pulse(self, ms):
        # --- FIX: specific method names used ---
        self.open_shutter()
        time.sleep(ms / 1000.0)
        self.close_shutter()

    def cleanup(self):
        self.task.stop()
        self.task.close()

if __name__ == "__main__":
    # Wrap in try/finally to ensure cleanup happens even if pulse crashes
    try:
        shutter = Shutter(device="Dev1", channel="PFI2")
        print("Opening shutter for 1 second...")
        shutter.pulse(1000)
    finally:
        # Check if shutter exists before cleaning up
        if 'shutter' in locals():
            shutter.cleanup()
            print("Done.")
