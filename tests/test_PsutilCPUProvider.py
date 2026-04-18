from unittest.mock import MagicMock, patch

import pytest

from cc_statusq_cpu.capsule.PsutilCPUProvider import PsutilCPUProvider
from cc_statusq_cpu.core.CPUStatus import CPUStatus


class TestPsutilCPUProvider:
    """
    Test suite for the PsutilCPUProvider implementation.
    Focuses on hardware data extraction logic using psutil mocks.
    """

    @pytest.fixture
    def provider(self):
        """Initializes the PsutilCPUProvider instance."""
        return PsutilCPUProvider()

    @patch('psutil.cpu_percent')
    @patch('psutil.cpu_count')
    @patch('psutil.cpu_freq')
    @patch('psutil.cpu_times')
    @patch('psutil.getloadavg')
    @patch('psutil.sensors_temperatures')
    def test_capture_once_mapping(
        self, mock_temp, mock_load, mock_times, mock_freq, mock_count, mock_percent, provider
    ):
        """
        Verifies that capture_once correctly maps psutil system calls 
        to the CPUStatus Data Transfer Object (DTO).
        """
        # --- Arrange ---
        # Mocking CPU core counts
        mock_count.side_effect = lambda logical: 8 if logical else 4
        
        # IMPORTANT: psutil.cpu_percent is called twice in capture_once:
        # 1st call: total usage (returns float)
        # 2nd call: per-cpu usage (returns list of floats)
        mock_percent.side_effect = [25.5, [20.0, 30.0, 25.0, 27.0]]
        
        # Mocking Frequency
        freq_mock = MagicMock(current=3200.0, min=800.0, max=4500.0)
        mock_freq.return_value = freq_mock
        
        # Mocking CPU Times
        times_mock = MagicMock(user=1200.0, system=400.0, idle=8000.0)
        mock_times.return_value = times_mock
        
        # Mocking Load Average (1m, 5m, 15m)
        mock_load.return_value = (1.5, 1.2, 0.8)
        
        # Mocking Temperature sensors
        sensor_mock = MagicMock(current=55.0)
        mock_temp.return_value = {'coretemp': [sensor_mock]}

        # --- Act ---
        status = provider.capture_once()

        # --- Assert ---
        assert isinstance(status, CPUStatus)
        assert status.total_usage_percentage == 25.5
        assert status.usage_per_core == [20.0, 30.0, 25.0, 27.0]
        assert status.physical_cores == 4
        assert status.logical_cores == 8
        assert status.current_temperature == 55.0
        assert status.average_load == [1.5, 1.2, 0.8]

    @patch('psutil.sensors_temperatures')
    @patch('psutil.cpu_percent')
    def test_temperature_none_when_sensors_missing(self, mock_percent, mock_temp, provider):
        """
        Ensures that if the system doesn't provide temperature data (like in some VMs),
        the provider returns None instead of crashing.
        """
        # Arrange
        mock_temp.return_value = {} # No sensors found
        mock_percent.side_effect = [10.0, [10.0]]

        # Act
        status = provider.capture_once()

        # Assert
        assert status.current_temperature is None

    @patch('psutil.cpu_percent')
    @patch('time.sleep', return_value=None) # Mock sleep to run tests instantly
    def test_capture_continuous_logic(self, mock_sleep, mock_percent, provider):
        """
        Tests the continuous monitoring loop (hardcoded to 3 iterations).
        Ensures it returns a list of 3 CPUStatus objects.
        """
        # Arrange: 
        # Each iteration calls capture_once, which calls cpu_percent twice.
        # 3 iterations * 2 calls = 6 return values needed in side_effect.
        mock_percent.side_effect = [
            10.0, [10.0], # Iteration 1
            15.0, [15.0], # Iteration 2
            20.0, [20.0]  # Iteration 3
        ]

        # Act
        results = provider.capture_continuous(interval=0.1)

        # Assert
        assert isinstance(results, list)
        assert len(results) == 3
        assert all(isinstance(s, CPUStatus) for s in results)
        assert results[0].total_usage_percentage == 10.0
        assert results[2].total_usage_percentage == 20.0