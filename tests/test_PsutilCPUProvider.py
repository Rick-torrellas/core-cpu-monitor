from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

# Importing the provider and the DTO
from cc_statusq_cpu.capsule import PsutilCPUProvider
from cc_statusq_cpu.core import CPUStatus


class TestPsutilCPUProvider:
    """
    Integration and Unit tests for the PsutilCPUProvider.
    We mock psutil to ensure consistent results regardless of the host machine.
    """

    @pytest.fixture
    def provider(self):
        """Returns an instance of the provider for each test."""
        return PsutilCPUProvider()

    @patch("psutil.cpu_freq")
    @patch("psutil.cpu_times")
    @patch("psutil.cpu_percent")
    @patch("psutil.getloadavg")
    @patch("psutil.sensors_temperatures")
    def test_capture_once_returns_valid_dto(
        self, 
        mock_temps, 
        mock_load, 
        mock_percent, 
        mock_times, 
        mock_freq, 
        provider
    ):
        """
        Tests that capture_once correctly maps psutil data into a CPUStatus DTO.
        """
        # 1. Setup mocks with dummy data
        mock_freq.return_value = MagicMock(current=2400.0, min=800.0, max=4000.0)
        mock_times.return_value = MagicMock(user=100.0, system=50.0, idle=500.0)
        mock_percent.side_effect = [15.0, [10.0, 20.0]] # First for total, second for per-cpu
        mock_load.return_value = (0.5, 0.6, 0.7)
        
        # Mocking complex temperature structure: { 'label': [sensor_data] }
        sensor_mock = MagicMock()
        sensor_mock.current = 55.0
        mock_temps.return_value = {"coretemp": [sensor_mock]}

        # 2. Execute the capture
        result = provider.capture_once()

        # 3. Assertions
        assert isinstance(result, CPUStatus)
        assert result.current_frequency == 2400.0
        assert result.total_usage_percentage == 15.0
        assert result.usage_per_core == [10.0, 20.0]
        assert result.current_temperature == 55.0
        assert isinstance(result.timestamp, datetime)
        
        # Verify psutil was called correctly
        mock_percent.assert_any_call(interval=None)
        mock_percent.assert_any_call(interval=None, percpu=True)

    @patch("psutil.cpu_freq")
    def test_capture_once_handles_missing_frequency(self, mock_freq, provider):
        """
        Some systems (like VMs or certain ARM chips) might not return CPU frequency.
        The provider should handle None and return 0.0 values.
        """
        mock_freq.return_value = None
        
        result = provider.capture_once()
        
        assert result.current_frequency == 0.0
        assert result.min_frequency == 0.0
        assert result.max_frequency == 0.0

    @patch("psutil.sensors_temperatures")
    def test_capture_once_handles_no_temperature_sensors(self, mock_temps, provider):
        """
        Ensures that if no temperature sensors are found, the DTO has None for temperature.
        """
        mock_temps.return_value = {} # Empty dict as returned by some OS
        
        result = provider.capture_once()
        
        assert result.current_temperature is None

    def test_capture_continuous_returns_list(self, provider):
        """
        Tests that capture_continuous returns a list of results.
        We use a small interval to keep the test fast.
        """
        # We patch capture_once to avoid slow real psutil calls during the loop
        with patch.object(PsutilCPUProvider, 'capture_once') as mock_capture:
            mock_capture.return_value = MagicMock(spec=CPUStatus)
            
            results = provider.capture_continuous(interval=0.01)
            
            assert isinstance(results, list)
            assert len(results) == 3 # Based on your implementation loop
            assert mock_capture.call_count == 3