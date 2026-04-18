from datetime import datetime
from unittest.mock import MagicMock

import pytest

from cc_statusq_cpu.core import CPUObserver, CPUProvider, CPUStatus


@pytest.fixture
def sample_cpu_status():
    """Proporciona un objeto CPUStatus con datos estáticos para validaciones."""
    return CPUStatus(
        name="Mock Processor @ 3.50GHz",
        architecture="x86_64",
        physical_cores=4,
        logical_cores=8,
        current_frequency=3500.0,
        min_frequency=800.0,
        max_frequency=4000.0,
        total_usage_percentage=25.5,
        usage_per_core=[20.0, 30.0, 25.0, 27.0, 22.0, 28.0, 26.0, 26.0],
        average_load=[1.5, 1.2, 1.1],
        user_time=1234.5,
        system_time=567.8,
        idle_time=9000.0,
        current_temperature=45.0,
        timestamp=datetime(2026, 4, 18, 12, 0, 0)
    )

@pytest.fixture
def mock_provider(sample_cpu_status):
    """
    Crea un mock que cumple con el protocolo CPUProvider.
    Configurado para devolver sample_cpu_status por defecto.
    """
    provider = MagicMock(spec=CPUProvider)
    provider.capture_once.return_value = sample_cpu_status
    return provider

@pytest.fixture
def mock_observer():
    """
    Crea un mock de un CPUObserver para verificar que 
    los métodos de notificación se llamen correctamente.
    """
    return MagicMock(spec=CPUObserver)

@pytest.fixture
def statusq_instance(mock_provider):
    """
    Instancia de StatusqCPU lista para usar con un provider mockeado.
    """
    from core.StatusqCPU import StatusqCPU
    return StatusqCPU(provider=mock_provider)