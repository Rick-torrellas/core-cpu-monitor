from cc_statusq_cpu.core import (
    DataReceivedEvent,
    MonitoringErrorEvent,
    MonitoringFinishedEvent,
    MonitoringStartedEvent,
    StatusqCPU,
)


def test_run_single_check_success(mock_provider, event_bus, mock_cpu_status):
    """
    Test a successful execution of run_single_check.
    Verifies that the provider is called and all lifecycle events are published.
    """
    # 1. Setup: Track events published to the bus
    received_events = []
    
    # We subscribe to the base CPUEvent to catch everything published
    from cc_statusq_cpu.core import CPUEvent
    event_bus.subscribe(CPUEvent, lambda e: received_events.append(e))
    
    # 2. Execute
    app = StatusqCPU(provider=mock_provider, event_bus=event_bus)
    result = app.run_single_check()
    
    # 3. Assertions
    # Ensure the returned data is what the provider "captured"
    assert result == mock_cpu_status
    mock_provider.capture_once.assert_called_once()
    
    # Verify the sequence of events: Started -> DataReceived -> Finished
    assert len(received_events) == 3
    assert isinstance(received_events[0], MonitoringStartedEvent)
    assert received_events[0].mode == "single"
    
    assert isinstance(received_events[1], DataReceivedEvent)
    assert received_events[1].status == mock_cpu_status
    
    assert isinstance(received_events[2], MonitoringFinishedEvent)

def test_run_single_check_failure(mock_provider, event_bus):
    """
    Test how run_single_check handles an exception from the provider.
    Ensures that MonitoringErrorEvent is fired and FinishedEvent still occurs.
    """
    # 1. Setup: Force the mock provider to raise an exception
    mock_provider.capture_once.side_effect = Exception("Hardware failure")
    
    received_events = []
    from cc_statusq_cpu.core import CPUEvent
    event_bus.subscribe(CPUEvent, lambda e: received_events.append(e))
    
    # 2. Execute
    app = StatusqCPU(provider=mock_provider, event_bus=event_bus)
    result = app.run_single_check()
    
    # 3. Assertions
    # Result should be None on failure
    assert result is None
    
    # Verify Error sequence: Started -> Error -> Finished
    assert any(isinstance(e, MonitoringErrorEvent) for e in received_events)
    assert isinstance(received_events[-1], MonitoringFinishedEvent)
    
    error_event = next(e for e in received_events if isinstance(e, MonitoringErrorEvent))
    assert "Error during single capture" in error_event.message
    assert str(error_event.exception) == "Hardware failure"

def test_run_single_check_event_payload_integrity(mock_provider, event_bus, mock_cpu_status):
    """
    Ensures that the data inside DataReceivedEvent is exactly what was provided.
    This validates the 'Capsule' pattern where data is wrapped without modification.
    """
    captured_status = None
    
    def handle_data(event):
        nonlocal captured_status
        captured_status = event.status

    event_bus.subscribe(DataReceivedEvent, handle_data)
    
    app = StatusqCPU(provider=mock_provider, event_bus=event_bus)
    app.run_single_check()
    
    assert captured_status.total_usage_percentage == 15.5
    assert captured_status.name == "TestProcessor"