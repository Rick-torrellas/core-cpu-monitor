def test_run_single_check_success(statusq_instance, mock_provider, mock_observer, mock_cpu_status):
    """
    Test that run_single_check correctly triggers all observer lifecycle events
    and returns the expected CPU data under normal conditions.
    """
    
    # 1. Arrange: Attach the mock observer to the StatusqCPU instance
    statusq_instance.attach(mock_observer)

    # 2. Act: Execute the single check
    result = statusq_instance.run_single_check()

    # 3. Assert: Verify the provider was called
    mock_provider.capture_once.assert_called_once()

    # 4. Assert: Verify the returned data matches the mock status
    assert result == mock_cpu_status
    assert result.name == "Test-Processor-v1"

    # 5. Assert: Verify the observer notifications (Lifecycle)
    # Ensure 'on_capture_start' was called with the correct mode
    mock_observer.on_capture_start.assert_called_once_with(mode="single")
    
    # Ensure 'on_data_received' was called with the mock status object
    mock_observer.on_data_received.assert_called_once_with(status=mock_cpu_status)
    
    # Ensure 'on_finished' was called regardless of success
    mock_observer.on_finished.assert_called_once()
    
    # Ensure 'on_error' was NEVER called
    mock_observer.on_error.assert_not_called()


def test_run_single_check_error(statusq_instance, mock_provider, mock_observer):
    """
    Test that run_single_check handles exceptions from the provider 
    and notifies observers about the error.
    """
    
    # 1. Arrange: Force the provider to raise an exception
    error_message = "Hardware failure"
    mock_provider.capture_once.side_effect = Exception(error_message)
    statusq_instance.attach(mock_observer)

    # 2. Act: Execute the check
    result = statusq_instance.run_single_check()

    # 3. Assert: The result should be None if an exception occurs
    assert result is None

    # 4. Assert: Verify error notification
    # The code notifies 'on_error' when an exception is caught
    mock_observer.on_error.assert_called_once()
    
    # Check if the error message passed to the observer is the expected one
    args, kwargs = mock_observer.on_error.call_args
    assert "Error during single capture" in kwargs['message']
    assert str(kwargs['error']) == error_message

    # 5. Assert: 'on_finished' must be called even if it fails (inside 'finally' block)
    mock_observer.on_finished.assert_called_once()