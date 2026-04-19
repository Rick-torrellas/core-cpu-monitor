from unittest.mock import MagicMock


def test_run_continuous_monitoring_calls_provider_and_notifies_observers(statusq_instance, mock_provider, mock_observer, mock_cpu_status):  # noqa: E501
    """
    Verifica que el monitoreo continuo capture datos la cantidad de veces solicitada
    y notifique a los observadores en cada paso del ciclo.
    """
    # 1. Preparación
    statusq_instance.attach(mock_observer)
    iterations = 3
    interval = 0.01  # Intervalo corto para que el test sea rápido

    # 2. Ejecución
    statusq_instance.run_continuous_monitoring(interval=interval, iterations=iterations)

    # 3. Aserciones sobre el Provider
    # Verificamos que capture_once se llamó exactamente el número de veces indicado en iterations
    assert mock_provider.capture_once.call_count == iterations

    # 4. Aserciones sobre el Observer (Ciclo de vida)
    # Debe iniciar una vez
    mock_observer.on_capture_start.assert_called_once_with(mode="continuous")
    
    # Debe recibir datos la misma cantidad de veces que las iteraciones
    assert mock_observer.on_data_received.call_count == iterations
    mock_observer.on_data_received.assert_called_with(status=mock_cpu_status)
    
    # Debe finalizar una vez
    mock_observer.on_finished.assert_called_once()


def test_run_continuous_monitoring_stops_on_exception(statusq_instance, mock_provider, mock_observer):
    """
    Verifica que si ocurre un error durante el monitoreo, se notifique al observer
    y se llame a on_finished.
    """
    # Configurar el mock para que falle en la segunda iteración
    mock_provider.capture_once.side_effect = [MagicMock(), Exception("Hardware Fail")]
    statusq_instance.attach(mock_observer)

    statusq_instance.run_continuous_monitoring(interval=0, iterations=5)

    # Verificamos que se llamó a on_error
    mock_observer.on_error.assert_called_once()
    args, kwargs = mock_observer.on_error.call_args
    assert "Continuous monitoring failure" in kwargs.get('message', args[0])
    
    # Verificamos que on_finished se llamó a pesar del error
    mock_observer.on_finished.assert_called_once()


def test_run_continuous_monitoring_keyboard_interrupt(statusq_instance, mock_provider, mock_observer):
    """
    Verifica el manejo de la interrupción de teclado (Ctrl+C).
    """
    mock_provider.capture_once.side_effect = KeyboardInterrupt()
    statusq_instance.attach(mock_observer)

    statusq_instance.run_continuous_monitoring(interval=0, iterations=1)

    # Debe notificar específicamente el error de interrupción por usuario
    mock_observer.on_error.assert_called_once()
    args, _ = mock_observer.on_error.call_args
    assert "interrupted by user" in args[0]
    mock_observer.on_finished.assert_called_once()