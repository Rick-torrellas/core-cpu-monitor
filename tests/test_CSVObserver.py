import csv
import os
from unittest.mock import MagicMock

from cc_statusq_cpu.capsule.CSVObserver import CSVObserver


def test_csv_observer_initialization(tmp_path, mock_cpu_status):
    """
    Test that the CSV file is created and headers are written correctly 
    upon receiving the first data packet.
    """
    # Use a temporary directory provided by pytest to avoid polluting the workspace
    file_path = tmp_path / "test_log.csv"
    observer = CSVObserver(file_path=str(file_path))

    # The file should not exist before the first data reception
    assert not os.path.exists(file_path)

    # Simulate receiving data
    observer.on_data_received(mock_cpu_status)

    # Verify file creation
    assert os.path.exists(file_path)

    # Verify headers match CPUStatus keys
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        expected_headers = list(mock_cpu_status.__dict__.keys())
        assert headers == expected_headers

def test_csv_observer_append_data(tmp_path, mock_cpu_status):
    """
    Test that subsequent data captures are appended as new rows in the CSV.
    """
    file_path = tmp_path / "test_append.csv"
    observer = CSVObserver(file_path=str(file_path))

    # Send data twice
    observer.on_data_received(mock_cpu_status)
    observer.on_data_received(mock_cpu_status)

    # Check file content (1 header row + 2 data rows = 3 rows total)
    with open(file_path, mode='r', encoding='utf-8') as f:
        rows = list(csv.reader(f))
        assert len(rows) == 3 
        
        # Verify the data values in the second row match the status object
        # Note: CSV stores everything as strings
        assert rows[1][0] == str(mock_cpu_status.name)
        assert float(rows[1][7]) == mock_cpu_status.total_usage_percentage

def test_csv_observer_error_handling(tmp_path, mock_cpu_status):
    """
    Test that errors during file writing do not crash the application 
    and are redirected to the on_error handler.
    """
    # Create a path that will cause an error (e.g., a directory with the same name as the file)
    invalid_path = tmp_path / "invalid_dir"
    invalid_path.mkdir()
    # We force an error by trying to write to a path where a directory already exists
    
    observer = CSVObserver(file_path=str(invalid_path)) # Pointing to a directory instead of a file
    
    # Mock the on_error method to verify it's called
    observer.on_error = MagicMock()

    # This should trigger the try-except block in on_data_received
    observer.on_data_received(mock_cpu_status)

    # Verify that on_error was called with an error message
    observer.on_error.assert_called_once()
    args, _ = observer.on_error.call_args
    assert "Failed to write to file" in args[0]

def test_csv_observer_reset_on_finished(tmp_path, mock_cpu_status):
    """
    Test that the _initialized flag is reset when the session finishes.
    """
    file_path = tmp_path / "test_reset.csv"
    observer = CSVObserver(file_path=str(file_path))

    observer.on_data_received(mock_cpu_status)
    assert observer._initialized is True

    observer.on_finished()
    assert observer._initialized is False