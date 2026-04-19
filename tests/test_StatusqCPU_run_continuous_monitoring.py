from unittest.mock import patch

from cc_statusq_cpu.core import (
    DataReceivedEvent,
    MonitoringErrorEvent,
    MonitoringFinishedEvent,
    MonitoringStartedEvent,
    StatusqCPU,
)


def test_run_continuous_monitoring_flow(mock_provider, event_bus, tracker_logs):
    """
    Verifies that a continuous monitoring session triggers the correct sequence of events:
    Started -> DataReceived (per iteration) -> Finished.
    """
    # Initialize the system under test
    tracker = StatusqCPU(provider=mock_provider, event_bus=event_bus)
    
    # Subscribe the tracker_logs list to all CPUEvent types
    from cc_statusq_cpu.core import CPUEvent
    event_bus.subscribe(CPUEvent, lambda e: tracker_logs.append(e))

    # Run for exactly 2 iterations with 0 delay for speed
    iterations = 2
    tracker.run_continuous_monitoring(interval=0, iterations=iterations)

    # Assertions
    assert len(tracker_logs) == 4  # Start + 2 Data + Finish
    assert isinstance(tracker_logs[0], MonitoringStartedEvent)
    assert tracker_logs[0].mode == "continuous"
    assert isinstance(tracker_logs[1], DataReceivedEvent)
    assert isinstance(tracker_logs[2], DataReceivedEvent)
    assert isinstance(tracker_logs[3], MonitoringFinishedEvent)
    
    # Verify the provider was actually called the correct number of times
    assert mock_provider.capture_once.call_count == iterations

def test_run_continuous_monitoring_exception_handling(mock_provider, event_bus, tracker_logs):
    """
    Verifies that if the provider raises an exception, the MonitoringErrorEvent is published
    and the process still fires a MonitoringFinishedEvent.
    """
    # Setup the mock to crash on the first call
    mock_provider.capture_once.side_effect = Exception("Hardware Failure")
    
    tracker = StatusqCPU(provider=mock_provider, event_bus=event_bus)
    event_bus.subscribe(MonitoringErrorEvent, lambda e: tracker_logs.append(e))
    event_bus.subscribe(MonitoringFinishedEvent, lambda e: tracker_logs.append(e))

    # Run monitoring
    tracker.run_continuous_monitoring(interval=0, iterations=5)

    # Even though we asked for 5 iterations, it should stop after the first error
    assert any(isinstance(e, MonitoringErrorEvent) for e in tracker_logs)
    assert any(isinstance(e, MonitoringFinishedEvent) for e in tracker_logs)
    assert "Hardware Failure" in tracker_logs[0].message or str(tracker_logs[0].exception) == "Hardware Failure"

def test_run_continuous_monitoring_keyboard_interrupt(mock_provider, event_bus, tracker_logs):
    """
    Simulates a user pressing Ctrl+C (KeyboardInterrupt) during monitoring.
    """
    # Setup mock to simulate a user interruption
    mock_provider.capture_once.side_effect = KeyboardInterrupt()
    
    tracker = StatusqCPU(provider=mock_provider, event_bus=event_bus)
    event_bus.subscribe(MonitoringErrorEvent, lambda e: tracker_logs.append(e))
    
    tracker.run_continuous_monitoring(interval=0)

    # Check if the specific interrupt message was captured
    assert len(tracker_logs) > 0
    assert "interrupted by user" in tracker_logs[0].message

@patch("time.sleep", return_value=None)
def test_run_continuous_monitoring_interval_timing(mock_sleep, mock_provider, event_bus):
    """
    Ensures that the monitoring loop respects the interval provided by calling time.sleep.
    """
    tracker = StatusqCPU(provider=mock_provider, event_bus=event_bus)
    
    # Run for 3 iterations
    iterations = 3
    interval = 0.5
    tracker.run_continuous_monitoring(interval=interval, iterations=iterations)

    # Assert that sleep was called with the correct interval for every iteration
    assert mock_sleep.call_count == iterations
    mock_sleep.assert_called_with(interval)