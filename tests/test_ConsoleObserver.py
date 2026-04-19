import pytest

from cc_statusq_cpu.capsule import ConsoleObserver


class TestConsoleObserver:
    """
    Unit tests for the ConsoleObserver class.
    Focuses on verifying that the output strings sent to stdout 
    match the expected formatting for each lifecycle event.
    """

    @pytest.fixture
    def observer(self):
        """Returns a clean instance of ConsoleObserver for each test."""
        return ConsoleObserver()

    def test_on_capture_start_output(self, observer, capsys):
        """
        GIVEN a monitoring mode (e.g., 'single')
        WHEN on_capture_start is called
        THEN it should print the correct startup message to stdout.
        """
        mode = "single"
        observer.on_capture_start(mode)
        
        # Capture the output from stdout
        captured = capsys.readouterr()
        
        assert f"Starting monitoring in mode: {mode}" in captured.out
        assert "🚀" in captured.out

    def test_on_data_received_output(self, observer, mock_cpu_status, capsys):
        """
        GIVEN a mock CPUStatus object
        WHEN on_data_received is called
        THEN it should print a formatted string containing usage and temperature.
        """
        # We assume 'mock_cpu_status' is provided by your conftest.py
        # or manually injected here for specific values
        mock_cpu_status.total_usage_percentage = 45.5
        mock_cpu_status.current_temperature = 60.0
        
        observer.on_data_received(mock_cpu_status)
        
        captured = capsys.readouterr()
        
        # Verify that key metrics are present in the console output
        assert "Total Usage: 45.5%" in captured.out
        assert "Temp: 60.0°C" in captured.out
        # Verify timestamp formatting (HH:MM:SS)
        expected_time = mock_cpu_status.timestamp.strftime('%H:%M:%S')
        assert expected_time in captured.out

    def test_on_error_output(self, observer, capsys):
        """
        GIVEN an error message and an exception
        WHEN on_error is called
        THEN it should print an error notification to stdout.
        """
        error_msg = "Connection failed"
        test_exception = ValueError("Invalid data")
        
        observer.on_error(error_msg, test_exception)
        
        captured = capsys.readouterr()
        
        assert "❌ ERROR:" in captured.out
        assert error_msg in captured.out
        assert str(test_exception) in captured.out

    def test_on_data_received_with_none_temp(self, observer, mock_cpu_status, capsys):
        """
        GIVEN a CPUStatus where temperature is None
        WHEN on_data_received is called
        THEN it should still function (verify robustness).
        """
        mock_cpu_status.current_temperature = None
        
        # This checks if the observer handles None values without crashing
        observer.on_data_received(mock_cpu_status)
        
        captured = capsys.readouterr()
        assert "None°C" in captured.out or "Total Usage" in captured.out