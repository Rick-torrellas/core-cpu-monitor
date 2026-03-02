from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

TARGET_MODULE = "core_cpu_monitor.domain"




@pytest.fixture
def mock_psutil():
    with patch(f"{TARGET_MODULE}.psutil") as mocked:
        # Usamos PropertyMock o objetos simples para mayor claridad
        mocked.cpu_times.return_value = MagicMock(user=10.0, system=5.0, idle=100.0)
        mocked.cpu_freq.return_value = MagicMock(current=2500.0, min=800.0, max=3500.0)

        # Mejoramos la lógica de cpu_count
        mocked.cpu_count.side_effect = lambda logical: 4 if not logical else 8

        # Evitamos fragilidad en cpu_percent usando una función inteligente
        def cpu_percent_mock(interval=None, percpu=False):
            return [10.0, 30.0] if percpu else 20.5

        mocked.cpu_percent.side_effect = cpu_percent_mock

        mocked.getloadavg.return_value = (1.0, 0.5, 0.2)
        yield mocked

@pytest.fixture
def mock_platform():
    with patch(f"{TARGET_MODULE}.platform") as mocked:
        mocked.processor.return_value = "Intel"
        mocked.machine.return_value = "x86_64"
        yield mocked

@pytest.fixture
def mock_datetime():
    fixed_now = datetime(2024, 1, 1)
    with patch(f"{TARGET_MODULE}.datetime") as mock_date:
        mock_date.now.return_value = fixed_now
        yield mock_date