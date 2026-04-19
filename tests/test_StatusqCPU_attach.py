def test_attach_observer_registers_correctly(statusq_instance, mock_observer):
    """
    Test Case: Verify that an observer is correctly added to the StatusqCPU instance.
    
    This test ensures that when the attach method is called, the observer 
    is stored in the internal _observers list, allowing it to receive future notifications.
    """
    
    # 1. Pre-condition: Check that the observers list starts empty
    # Note: Using access to protected member _observers for verification purposes in testing
    assert len(statusq_instance._observers) == 0
    
    # 2. Action: Attach the mocked observer
    statusq_instance.attach(mock_observer)
    
    # 3. Assertion: Verify the list contains exactly one observer
    assert len(statusq_instance._observers) == 1
    
    # 4. Assertion: Verify the stored observer is exactly the one we attached
    assert statusq_instance._observers[0] is mock_observer

def test_attach_multiple_observers(statusq_instance, mock_observer):
    """
    Test Case: Verify that multiple observers can be registered simultaneously.
    """
    from unittest.mock import MagicMock

    from cc_statusq_cpu.core.CPUObserver import CPUObserver

    # Create a second distinct mock observer
    second_observer = MagicMock(spec=CPUObserver)
    
    # Attach both observers
    statusq_instance.attach(mock_observer)
    statusq_instance.attach(second_observer)
    
    # Verify both are present in the list
    assert len(statusq_instance._observers) == 2
    assert mock_observer in statusq_instance._observers
    assert second_observer in statusq_instance._observers