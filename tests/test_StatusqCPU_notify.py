from unittest.mock import MagicMock

import pytest

from cc_statusq_cpu.core.CPUObserver import CPUObserver


def test_notify_calls_registered_observers(statusq_instance, mock_observer):
    """
    Test that _notify correctly propagates an event to a registered observer.
    """
    # 1. Setup: Attach the mock observer to the StatusqCPU instance
    statusq_instance.attach(mock_observer)
    
    # 2. Action: Manually trigger the internal _notify method
    event_name = "on_capture_start"
    test_mode = "test_mode"
    statusq_instance._notify(event_name, mode=test_mode)
    
    # 3. Assertion: Check if the observer's method was called with the correct arguments
    mock_observer.on_capture_start.assert_called_once_with(mode=test_mode)

def test_notify_multiple_observers(statusq_instance):
    """
    Test that _notify sends updates to all attached observers.
    """
    # 1. Setup: Create and attach multiple observers
    obs1 = MagicMock(spec=CPUObserver)
    obs2 = MagicMock(spec=CPUObserver)
    statusq_instance.attach(obs1)
    statusq_instance.attach(obs2)
    
    # 2. Action: Notify a generic event
    statusq_instance._notify("on_finished")
    
    # 3. Assertion: Verify both observers received the signal
    obs1.on_finished.assert_called_once()
    obs2.on_finished.assert_called_once()

def test_notify_with_missing_method(statusq_instance):
    """
    Test the robustness of _notify when an observer does not implement a specific method.
    The reflection (getattr) should handle this gracefully without raising an AttributeError.
    """
    # 1. Setup: Create an object that doesn't have the expected observer methods
    # Using a plain object instead of a spec-mock to test the 'getattr' check
    class IncompleteObserver:
        pass 
    
    incomplete_obs = IncompleteObserver()
    statusq_instance.attach(incomplete_obs)
    
    # 2. Action & Assertion: 
    # Calling _notify should not raise any exception even if 'on_data_received' is missing
    try:
        statusq_instance._notify("on_data_received", status=None)
    except AttributeError:
        pytest.fail("_notify raised AttributeError for a missing observer method!")

def test_notify_with_complex_args(statusq_instance, mock_observer, mock_cpu_status):
    """
    Test that _notify correctly passes complex objects (like CPUStatus) to observers.
    """
    statusq_instance.attach(mock_observer)
    
    # Action: Notify data received with a mock status object
    statusq_instance._notify("on_data_received", status=mock_cpu_status)
    
    # Assertion: Ensure the data integrity is maintained during notification
    mock_observer.on_data_received.assert_called_once_with(status=mock_cpu_status)