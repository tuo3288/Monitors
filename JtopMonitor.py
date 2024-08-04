import threading
import time
from jtop import jtop

class JetsonGPUMonitor:
    def __init__(self, interval=1, filename=None):
        self.interval = interval
        self.__stop_event = threading.Event()
        self.filename = filename
        self.__monitor_thread = None
        if self.filename is not None:  # Clear the log file
            with open(filename, 'w') as f:
                f.write("")
        self.jetson = jtop()
        self.jetson.start()
        print("Initialized jtop")

    def write(self, message: str):
        if self.filename is not None:
            with open(self.filename, 'a') as f:
                f.write(message + '\n')
        else:
            print(message)

    def get_gpu_info(self):
        stats = self.jetson.stats
        gpu_util = stats['GPU']
        ram_info = stats['RAM']
        power = stats['power']['GPU']
        temperature = stats['Temp GPU']
        timestamp = time.time()
        info = {
            'GPU Utilization (%)': gpu_util,
            'Total Memory (bytes)': ram_info['tot'],
            'Used Memory (bytes)': ram_info['use'],
            'Free Memory (bytes)': ram_info['free'],
            'Power Usage (mW)': power,
            'Temperature (C)': temperature
        }
        return timestamp, info

    def monitor_gpu(self):
        _, base_info = self.get_gpu_info()
        self.write(f"Baseline: {base_info}")
        while not self.__stop_event.is_set():
            timestamp, info = self.get_gpu_info()
            self.write(f"{timestamp}: {info}")
            time.sleep(self.interval)

    def start_monitoring(self):
        self.__monitor_thread = threading.Thread(target=self.monitor_gpu)
        self.__monitor_thread.start()
        print("Monitoring started")

    def stop_monitoring(self):
        self.__stop_event.set()
        self.__monitor_thread.join()
        print("Monitoring stopped")

    def cleanup(self):
        self.jetson.close()
        print("Shutdown jtop")
