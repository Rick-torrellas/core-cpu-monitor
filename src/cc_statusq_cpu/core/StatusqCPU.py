import time
from typing import Optional

from .CPUEventBus import CPUEventBus
from .CPUEvents import DataReceivedEvent, MonitoringErrorEvent, MonitoringFinishedEvent, MonitoringStartedEvent
from .CPUProvider import CPUProvider
from .CPUStatus import CPUStatus


class StatusqCPU:
    def __init__(self, provider: CPUProvider, event_bus: CPUEventBus):
        """
        StatusqCPU now depends on a provider and an event bus.
        It no longer manages observers directly.
        """
        self._provider = provider
        self._event_bus = event_bus

    def run_single_check(self) -> Optional[CPUStatus]:
        """Executes a single capture and publishes the events to the bus."""
        self._event_bus.publish(MonitoringStartedEvent(mode="single"))
        try:
            data = self._provider.capture_once()
            self._event_bus.publish(DataReceivedEvent(status=data))
            return data
        except Exception as e:
            self._event_bus.publish(MonitoringErrorEvent(
                message="Error during single capture", 
                exception=e
            ))
        finally:
            self._event_bus.publish(MonitoringFinishedEvent())

    def run_continuous_monitoring(self, interval: float, iterations: int = None):
        """
        Monitors CPU in a loop. Every step is an event published to the bus.
        """
        self._event_bus.publish(MonitoringStartedEvent(mode="continuous"))
        count = 0
        try:
            while iterations is None or count < iterations:
                data = self._provider.capture_once() 
                self._event_bus.publish(DataReceivedEvent(status=data))
                count += 1
                time.sleep(interval)
        except KeyboardInterrupt:
            self._event_bus.publish(MonitoringErrorEvent(
                message="Monitoring interrupted by user"
            ))
        except Exception as e:
            self._event_bus.publish(MonitoringErrorEvent(
                message="Continuous monitoring failure", 
                exception=e
            ))
        finally:
            self._event_bus.publish(MonitoringFinishedEvent())