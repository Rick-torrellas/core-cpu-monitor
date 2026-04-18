import platform
import time
from datetime import datetime
from typing import List, Optional

import psutil

from ..core.CPUStatus import CPUStatus


class PsutilCPUProvider:
    """Concrete implementation using psutil that fulfills the CPUProvider contract."""

    def capture_once(self) -> CPUStatus:
        """Captures the current CPU state and returns a CPUStatus object."""
        
        # Frequency metrics
        freq = psutil.cpu_freq()
        if freq is not None:
            current_freq: float = float(freq.current)
            min_freq: float = float(freq.min)
            max_freq: float = float(freq.max)
        else:
            current_freq = min_freq = max_freq = 0.0

        times = psutil.cpu_times()

        avg_load: Optional[List[float]] = None
        try:
            load_tuple = psutil.getloadavg()
            avg_load = [float(x) for x in load_tuple]
        except (AttributeError, OSError):
            pass

        temp: Optional[float] = None
        try:
            temps = psutil.sensors_temperatures()
            if temps and isinstance(temps, dict):
                # Access the first available temperature sensor
                first_sensor_list = next(iter(temps.values()))
                if first_sensor_list and len(first_sensor_list) > 0:
                    first_sensor = first_sensor_list[0]
                    if hasattr(first_sensor, "current"):
                        temp = float(first_sensor.current)
        except Exception:
            temp = None

        # Core counts
        physical_cores: Optional[int] = psutil.cpu_count(logical=False)
        logical_cores: Optional[int] = psutil.cpu_count(logical=True)

        # Usage percentages
        # Note: interval=None returns usage since the last call (non-blocking)
        total_usage: float = psutil.cpu_percent(interval=None)
        per_core_usage_raw = psutil.cpu_percent(interval=None, percpu=True)
        per_core_usage: List[float] = [float(x) for x in per_core_usage_raw]

        return CPUStatus(
            name=platform.processor() or "Unknown",
            architecture=platform.machine() or "Unknown",
            physical_cores=physical_cores,
            logical_cores=logical_cores,
            current_frequency=current_freq,
            min_frequency=min_freq,
            max_frequency=max_freq,
            total_usage_percentage=total_usage,
            usage_per_core=per_core_usage,
            average_load=avg_load,
            user_time=float(times.user),
            system_time=float(times.system),
            idle_time=float(times.idle),
            current_temperature=temp,
            timestamp=datetime.now(),
        )

    def capture_continuous(self, interval: float) -> List[CPUStatus]:
        """
        Implementation of the method required by the CPUProvider contract.
        Captures the state at regular intervals and returns a list.
        """
        results = []
        try:
            # Iterates 3 times to collect samples
            for _ in range(3): 
                results.append(self.capture_once())
                time.sleep(interval)
        except Exception:
            pass
        return results