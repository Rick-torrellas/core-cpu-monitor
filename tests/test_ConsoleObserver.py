import pytest

from cc_statusq_cpu.capsule.ConsoleObserver import ConsoleObserver


class TestConsoleObserver:
    """
    Test suite for the ConsoleObserver class to ensure it formats 
    and prints monitoring data correctly to the console.
    """

    @pytest.fixture
    def observer(self):
        """Returns a fresh instance of ConsoleObserver for each test."""
        return ConsoleObserver()

    def test_on_capture_start_prints_correct_mode(self, observer, capsys):
        """
        GIVEN a monitoring mode (e.g., 'continuous')
        WHEN on_capture_start is triggered
        THEN it should print a rocket emoji and the mode name to stdout.
        """
        mode = "continuous"
        observer.on_capture_start(mode)
        
        # Capture the printed output
        captured = capsys.readouterr()
        
        assert "🚀 Starting monitoring in mode: continuous" in captured.out

    def test_on_data_received_formats_metrics_correctly(self, observer, mock_cpu_status, capsys):
        """
        GIVEN a CPUStatus object with specific metrics
        WHEN on_data_received is called
        THEN it should print the formatted timestamp, usage, and temperature.
        """
        # Trigger the observer method with the mock data from conftest.py
        observer.on_data_received(mock_cpu_status)
        
        captured = capsys.readouterr()
        
        # Expected format: [12:00:00] Total Usage: 25.5% | Temp: 55.0°C
        # Note: The timestamp in mock_cpu_status is 12:00:00
        assert "[12:00:00]" in captured.out
        assert "Total Usage: 25.5%" in captured.out
        assert "Temp: 55.0°C" in captured.out

    def test_on_error_prints_error_message(self, observer, capsys):
        """
        GIVEN an error message and an Exception
        WHEN on_error is called
        THEN it should print an error icon and the details.
        """
        message = "Connection lost"
        error = ValueError("Sample error")
        
        observer.on_error(message, error)
        
        captured = capsys.readouterr()
        
        # Verify the structure of the error output
        assert "❌ ERROR: Connection lost -> Sample error" in captured.out

    def test_on_data_received_with_missing_temp(self, observer, mock_cpu_status, capsys):
        """
        GIVEN a CPUStatus where temperature is None
        WHEN on_data_received is called
        THEN it should still print but display 'None' or handle the value.
        """
        # Modify the mock status to simulate missing temperature data
        mock_cpu_status.current_temperature = None
        
        observer.on_data_received(mock_cpu_status)
        
        captured = capsys.readouterr()
        
        # Ensure it doesn't crash and prints None for temperature
        assert "Temp: None°C" in captured.out