from ..core.CPUObserver import CPUObserver
from ..core.CPUStatus import CPUStatus


class ConsoleObserver(CPUObserver):
    """Observer that prints to the console in an elegant format."""
    
    def on_capture_start(self, mode: str):
        # Notify the start of the monitoring process with the specified mode
        print(f"🚀 Starting monitoring in mode: {mode}")

    def on_data_received(self, status: CPUStatus):
        # Display a formatted timestamp, total CPU usage, and current temperature
        print(f"[{status.timestamp.strftime('%H:%M:%S')}] "
              f"Total Usage: {status.total_usage_percentage}% | Temp: {status.current_temperature}°C")

    def on_error(self, message: str, error: Exception = None):
        # Report errors encountered during the monitoring process
        print(f"❌ ERROR: {message} -> {error}")

