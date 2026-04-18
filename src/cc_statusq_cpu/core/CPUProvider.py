from typing import List, Protocol, runtime_checkable

from .CPUStatus import CPUStatus


@runtime_checkable
class CPUProvider(Protocol):
    """
    Defines the contract for any CPU data source.
    Allows swapping psutil for mocks or other libraries.
    """
    
    def capture_once(self) -> CPUStatus:
        """
        Captures the current CPU state and returns a CPUStatus object.
        Used for single-point telemetry snapshots.
        """
        ...

    def capture_continuous(self, interval: float) -> List[CPUStatus]:
        """
        Captures CPU state at regular intervals and returns a list of CPUStatus objects.
        Useful for monitoring trends over a specific time window.
        """
        ...