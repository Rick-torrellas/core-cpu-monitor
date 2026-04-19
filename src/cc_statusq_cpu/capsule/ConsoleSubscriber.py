from ..core import CPUEventBus, DataReceivedEvent, MonitoringStartedEvent


class ConsoleSubscriber: # Antes ConsoleObserver
    def __init__(self, bus: CPUEventBus):
        # El propio objeto sabe a qué eventos quiere reaccionar
        bus.subscribe(MonitoringStartedEvent, self._handle_start)
        bus.subscribe(DataReceivedEvent, self._handle_data)

    def _handle_start(self, event: MonitoringStartedEvent):
        print(f"🚀 Started: {event.mode}")

    def _handle_data(self, event: DataReceivedEvent):
        print(f"Usage: {event.status.total_usage_percentage}%")