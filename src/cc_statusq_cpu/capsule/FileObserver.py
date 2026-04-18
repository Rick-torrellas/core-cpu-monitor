from ..core.CPUObserver import CPUObserver
from ..core.CPUStatus import CPUStatus


class FileObserver(CPUObserver):
    """Observer that saves logs to a file in the background."""
    
    def on_data_received(self, status: CPUStatus):
        # Logic to write to a .log or CSV file
        pass