from datetime import datetime

import pytest

from cc_statusq_cpu.core.CPUStatus import CPUStatus


class TestCPUStatus:
    """
    Test suite for the CPUStatus DTO (Data Transfer Object).
    Verifies that hardware metrics are correctly stored and retrieved.
    """

    @pytest.fixture
    def sample_date(self):
        """Fixed timestamp for deterministic testing."""
        return datetime(2026, 4, 18, 12, 0, 0)

    @pytest.fixture
    def cpu_status_instance(self, sample_date):
        """Provides a standard instance of CPUStatus with dummy data."""
        return CPUStatus(
            name="Intel Core i7",
            architecture="x86_64",
            physical_cores=8,
            logical_cores=16,
            current_frequency=3500.0,
            min_frequency=800.0,
            max_frequency=4800.0,
            total_usage_percentage=22.5,
            usage_per_core=[20.0, 25.0, 30.0, 15.0],
            average_load=[1.2, 0.8, 0.5],
            user_time=1500.0,
            system_time=600.0,
            idle_time=9000.0,
            current_temperature=52.5,
            timestamp=sample_date
        )

    def test_cpu_status_initialization(self, cpu_status_instance, sample_date):
        """
        Tests that all fields are correctly assigned during initialization.
        """
        assert cpu_status_instance.name == "Intel Core i7"
        assert cpu_status_instance.architecture == "x86_64"
        assert cpu_status_instance.physical_cores == 8
        assert cpu_status_instance.logical_cores == 16
        assert cpu_status_instance.current_frequency == 3500.0
        assert cpu_status_instance.total_usage_percentage == 22.5
        assert cpu_status_instance.usage_per_core == [20.0, 25.0, 30.0, 15.0]
        assert cpu_status_instance.timestamp == sample_date

    def test_cpu_status_optional_temperature(self, sample_date):
        """
        Ensures that current_temperature can be None (for systems without sensors).
        """
        status = CPUStatus(
            name="Generic CPU",
            architecture="ARM",
            physical_cores=2,
            logical_cores=2,
            current_frequency=1000.0,
            min_frequency=1000.0,
            max_frequency=1000.0,
            total_usage_percentage=5.0,
            usage_per_core=[5.0, 5.0],
            average_load=[0.1, 0.1, 0.1],
            user_time=100.0,
            system_time=10.0,
            idle_time=1000.0,
            current_temperature=None,  # Missing sensor case
            timestamp=sample_date
        )
        assert status.current_temperature is None

    def test_cpu_status_types(self, cpu_status_instance):
        """
        Validates that the numeric fields contain the expected data types.
        """
        assert isinstance(cpu_status_instance.total_usage_percentage, float)
        assert isinstance(cpu_status_instance.physical_cores, int)
        assert isinstance(cpu_status_instance.usage_per_core, list)
        assert isinstance(cpu_status_instance.timestamp, datetime)

    def test_immutability_or_modification(self, cpu_status_instance):
        """
        Verifies if we can modify fields or if the DTO behaves as expected 
        when values change.
        """
        cpu_status_instance.name = "Updated Name"
        assert cpu_status_instance.name == "Updated Name"