from core_cpu_monitor import CPUStateCheck

TARGET_MODULE = "core_cpu_monitor.domain"

# --- Tests Mejorados ---


def test_capture_complete_data(mock_psutil, mock_platform, mock_datetime):
    """Verifica que todos los campos se mapeen correctamente."""
    check = CPUStateCheck()
    status = check.capture()
    expected_now = mock_datetime.now.return_value
    assert status.total_usage_percentage == 20.5
    assert status.usage_per_core == [10.0, 30.0]
    assert status.user_time == 10.0
    assert status.average_load == [1.0, 0.5, 0.2]
    assert status.timestamp == expected_now


def test_capture_temperature_exception_handling(mock_psutil, mock_platform):
    """Verifica la resiliencia: si los sensores fallan, la temperatura es None."""
    mock_psutil.sensors_temperatures.side_effect = Exception("Hardware error")

    check = CPUStateCheck()
    status = check.capture()

    assert status.current_temperature is None
    # Verificamos que el resto del objeto se creó correctamente
    assert status.name == "Intel"


def test_capture_no_load_avg_support(mock_psutil, mock_platform):
    """Simula un sistema (como Windows antiguo) que no tiene getloadavg."""
    # Forzamos que la llamada lance AttributeError, simulando que no existe o falla
    mock_psutil.getloadavg.side_effect = AttributeError

    check = CPUStateCheck()
    status = check.capture()

    assert status.average_load is None


def test_capture_freq_none(mock_psutil, mock_platform):
    """Verifica que si cpu_freq devuelve None, los valores sean 0.0."""
    mock_psutil.cpu_freq.return_value = None

    check = CPUStateCheck()
    status = check.capture()

    assert status.current_frequency == 0.0
    assert status.min_frequency == 0.0
