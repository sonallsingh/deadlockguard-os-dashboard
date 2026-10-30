from app import safety_algorithm, request_resources, detect_single_instance, DEFAULT_ALLOC, DEFAULT_MAX, DEFAULT_AVAIL

def test_default_safe_sequence():
    result = safety_algorithm(DEFAULT_ALLOC, DEFAULT_MAX, DEFAULT_AVAIL)
    assert result["safe"] is True
    assert result["sequence"] == [1, 3, 0, 2, 4]

def test_request_exceeds_available_waits():
    result = request_resources(DEFAULT_ALLOC, DEFAULT_MAX, DEFAULT_AVAIL, 0, [0, 0, 3])
    assert result["status"] == "waiting"

def test_request_creates_unsafe_state_denied():
    result = request_resources(DEFAULT_ALLOC, DEFAULT_MAX, DEFAULT_AVAIL, 4, [3, 3, 0])
    assert result["status"] == "denied_unsafe"

def test_single_instance_cycle():
    assert detect_single_instance({"P0": "P1", "P1": "P0"}) is True

def test_no_cycle():
    assert detect_single_instance({"P0": "P1"}) is False
