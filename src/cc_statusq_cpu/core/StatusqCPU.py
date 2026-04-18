import time
from typing import List, Optional

from .CPUObserver import CPUObserver
from .CPUProvider import CPUProvider
from .CPUStatus import CPUStatus


class StatusqCPU:
    def __init__(self, provider: CPUProvider):
        """
        Initializes the status monitor with a specific CPU data provider.
        """
        self._provider = provider
        self._observers: List[CPUObserver] = []

    def attach(self, observer: CPUObserver):
        """
        Registers a new observer interested in CPU status events.
        """
        self._observers.append(observer)

    def _notify(self, event_name: str, *args, **kwargs):
        """
        Internal method to propagate events to all registered observers using reflection.
        """
        for observer in self._observers:
            method = getattr(observer, event_name, None)
            if method:
                method(*args, **kwargs)

    def run_single_check(self) -> Optional[CPUStatus]:
        """
        Executes a single data capture cycle.
        """
        self._notify("on_capture_start", mode="single")
        try:
            data = self._provider.capture_once()
            self._notify("on_data_received", status=data)
            return data
        except Exception as e:
            self._notify("on_error", message="Error during single capture", error=e)
        finally:
            self._notify("on_finished")

    def run_continuous_monitoring(self, interval: float, iterations: int = None):
        """
        Executes capture cycles in a loop at a specific interval.
        
        Note: A loop is used to trigger events for each individual reading,
        providing granular updates instead of waiting for a batch process.
        """
        self._notify("on_capture_start", mode="continuous")
        count = 0
        try:
            while iterations is None or count < iterations:
                # Use capture_once inside the loop for granular event notification
                data = self._provider.capture_once() 
                self._notify("on_data_received", status=data)
                count += 1
                time.sleep(interval)
        except KeyboardInterrupt:
            self._notify("on_error", message="Monitoring interrupted by user")
        except Exception as e:
            self._notify("on_error", message="Continuous monitoring failure", error=e)
        finally:
            self._notify("on_finished")