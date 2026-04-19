from typing import Callable, Dict, List, Type, TypeVar

from .CPUEvents import CPUEvent

T = TypeVar("T", bound=CPUEvent)

class CPUEventBus:
    """
    A simple Event Bus that decouples Event Publishers from Event Subscribers.
    Instead of calling methods on observers, it broadcasts event objects.
    """

    def __init__(self):
        # Maps event types to a list of callback functions
        self._subscribers: Dict[Type[CPUEvent], List[Callable]] = {}

    def subscribe(self, event_type: Type[T], callback: Callable[[T], None]):
        """Registers a callback to be executed when a specific event type is published."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def publish(self, event: CPUEvent):
        """Broadcasts an event to all interested subscribers."""
        event_type = type(event)
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                callback(event)