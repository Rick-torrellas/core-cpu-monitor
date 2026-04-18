from abc import ABC

from .CPUStatus import CPUStatus


class CPUObserver(ABC):
    """Interface to observe CPU monitoring lifecycle events."""
    
    def on_capture_start(self, mode: str):
        """Triggered before starting any capture (once or continuous)."""
        pass

    def on_data_received(self, status: CPUStatus):
        """Triggered every time a capture is successful."""
        pass

    def on_error(self, message: str, error: Exception = None):
        """Error sink to keep the business logic clean."""
        pass

    def on_finished(self):
        """Triggered when the monitoring session finishes."""
        pass