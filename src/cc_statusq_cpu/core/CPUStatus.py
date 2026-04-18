from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class CPUStatus:
    """Data transfer object representing a snapshot of CPU state and metrics."""

    name: str  # CPU model name/identifier
    architecture: str  # System architecture (e.g., x86_64, ARM)
    physical_cores: Optional[int]  # Number of physical CPU cores
    logical_cores: Optional[int]  # Number of logical cores (including hyperthreading)
    current_frequency: float  # Current CPU frequency in MHz
    min_frequency: float  # Minimum supported CPU frequency in MHz
    max_frequency: float  # Maximum supported CPU frequency in MHz
    total_usage_percentage: float  # Overall CPU usage percentage across all cores
    usage_per_core: List[float]  # Individual usage percentage for each core
    average_load: Optional[List[float]]  # System load average over 1, 5, and 15 minutes
    user_time: float  # Time spent executing user processes
    system_time: float  # Time spent executing kernel processes
    idle_time: float  # Time spent idle
    current_temperature: Optional[float]  # Current CPU temperature in Celsius (if available)
    timestamp: datetime  # Timestamp of the measurement