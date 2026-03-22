import pytest
from src.engine.trace_generator import build_trace_object, generate_trace

def test_build_trace_object_success():
    # Test valid input for trace generation
    trace = build_trace_object(
        date_str="1990-05-15",
        time_str="14:30",
        city="London",
        state="",
        name="Test Native"
    )
    
    assert trace is not None
    assert trace.subject_name == "Test Native"
    assert "1990-05-15" in trace.birth_data
    
    # Check that some steps got added
    assert len(trace.steps) > 0
    categories = {step.category for step in trace.steps}
    assert "① Astronomical Foundations" in categories
    assert "② Sect Determination" in categories
    assert "③ Essential Dignities" in categories

def test_generate_trace_dict():
    # Same as above but returns dictionary
    trace_dict = generate_trace(
        date_str="1990-05-15",
        time_str="14:30",
        city="London",
        name="Test Native"
    )
    
    assert isinstance(trace_dict, dict)
    assert "steps" in trace_dict
    assert len(trace_dict["steps"]) > 0
    assert trace_dict["subject_name"] == "Test Native"

def test_build_trace_object_invalid():
    # Test error handling when chart generation fails
    trace = build_trace_object(
        date_str="invalid-date",
        time_str="99:99",
        city="Nowhere",
        name="Error Native"
    )
    
    assert trace is not None
    assert len(trace.steps) == 1
    assert trace.steps[0].category == "Error"

def test_generate_trace_invalid():
    # Test error handling Dict result
    trace_dict = generate_trace(
        date_str="invalid-date",
        time_str="99:99",
        city="Nowhere",
        name="Error Native"
    )
    
    assert isinstance(trace_dict, dict)
    assert "error" in trace_dict
    assert "steps" in trace_dict
