from ..core.CPUObserver import CPUObserver
from ..core.CPUStatus import CPUStatus


class FileObserver(CPUObserver):
    """Observer that saves logs to a file in the background."""
    def __init__(self, file_path: str = "cpu_log.txt"):
        # This allows the class to receive the file_path argument
        self.file_path = file_path

    def on_capture_start(self, mode: str):
        print(f"FileObserver: Starting capture in {mode} mode.")

    
    def on_data_received(self, status: CPUStatus):
        # Logic to write to a .log or CSV file
        pass

    def on_finished(self):
        print(f"FileObserver: Data saved to {self.file_path}")