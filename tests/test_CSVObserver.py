import csv
import os

import pytest

from cc_statusq_cpu.capsule import CSVObserver


class TestCSVObserver:
    """
    Unit tests for the CSVObserver class.
    Focuses on file creation, header integrity, and data row appending.
    """

    @pytest.fixture
    def temp_csv_file(self, tmp_path):
        """Creates a temporary path for the CSV file."""
        return tmp_path / "test_cpu_log.csv"

    @pytest.fixture
    def observer(self, temp_csv_file):
        """Initializes the CSVObserver with a temporary file path."""
        return CSVObserver(file_path=str(temp_csv_file))

    def test_file_creation_on_first_data(self, observer, temp_csv_file, mock_cpu_status):
        """
        Test that the CSV file is created only when the first data point is received,
        not necessarily when the monitoring starts.
        """
        # Ensure file does not exist yet
        assert not os.path.exists(temp_csv_file)

        # Act: Trigger data reception
        observer.on_data_received(mock_cpu_status)

        # Assert: File should now exist
        assert os.path.exists(temp_csv_file)

    def test_csv_header_integrity(self, observer, temp_csv_file, mock_cpu_status):
        """
        Verify that the CSV header matches the keys of the CPUStatus dataclass.
        """
        observer.on_data_received(mock_cpu_status)

        with open(temp_csv_file, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            
            # Expected fields from CPUStatus (name, architecture, etc.)
            expected_fields = list(mock_cpu_status.__dict__.keys())
            assert header == expected_fields

    def test_appending_multiple_records(self, observer, temp_csv_file, mock_cpu_status):
        """
        Ensure that multiple calls to on_data_received append rows 
        instead of overwriting the file.
        """
        # Act: Send two data points
        observer.on_data_received(mock_cpu_status)
        observer.on_data_received(mock_cpu_status)

        with open(temp_csv_file, mode='r', encoding='utf-8') as f:
            lines = list(csv.reader(f))
            # 1 header row + 2 data rows = 3 total lines
            assert len(lines) == 3

    def test_data_value_accuracy(self, observer, temp_csv_file, mock_cpu_status):
        """
        Verify that the values written in the CSV match the CPUStatus object data.
        """
        observer.on_data_received(mock_cpu_status)

        with open(temp_csv_file, mode='r', encoding='utf-8') as f:
            lines = list(csv.reader(f))
            data_row = lines[1] # First row after header

            # Check specific fields (indexing based on CPUStatus structure)
            # Assuming 'name' is the first field
            assert data_row[0] == mock_cpu_status.name
            # Check total usage percentage (convert string back to float for comparison)
            assert float(data_row[7]) == mock_cpu_status.total_usage_percentage

    def test_reset_state_on_finished(self, observer, mock_cpu_status):
        """
        Check if the observer resets its internal '_initialized' state 
        when the session finishes.
        """
        observer.on_data_received(mock_cpu_status)
        assert observer._initialized is True

        observer.on_finished()
        assert observer._initialized is False