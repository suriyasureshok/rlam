"""
Unit tests for the Action class.
Verifies immutability, validation, equality, and serialization.
"""
import pytest
from datetime import datetime, timezone
from pydantic import ValidationError
from rlam.action import Action


def test_action_creation_with_all_fields():
    """Action can be created with all required fields."""
    timestamp = datetime.now(timezone.utc)
    action = Action(
        action_id="A1",
        action_type="load_data",
        inputs={"path": "data.csv"},
        parameters={"encoding": "utf-8"},
        environment_hash="abc123",
        timestamp=timestamp
    )
    
    assert action.action_id == "A1"
    assert action.action_type == "load_data"
    assert action.inputs == {"path": "data.csv"}
    assert action.parameters == {"encoding": "utf-8"}
    assert action.environment_hash == "abc123"
    assert action.timestamp == timestamp


def test_action_immutability_action_id():
    """Action fields are immutable - action_id cannot be modified."""
    action = Action(
        action_id="A1",
        action_type="test",
        inputs={},
        parameters={},
        environment_hash="hash",
        timestamp=datetime.now(timezone.utc)
    )
    
    with pytest.raises(ValidationError, match="frozen"):
        action.action_id = "A2"


def test_action_immutability_inputs():
    """Action fields are immutable - inputs cannot be modified."""
    action = Action(
        action_id="A1",
        action_type="test",
        inputs={"x": 1},
        parameters={},
        environment_hash="hash",
        timestamp=datetime.now(timezone.utc)
    )
    
    with pytest.raises(ValidationError, match="frozen"):
        action.inputs = {"x": 2}


def test_action_immutability_parameters():
    """Action fields are immutable - parameters cannot be modified."""
    action = Action(
        action_id="A1",
        action_type="test",
        inputs={},
        parameters={"threshold": 0.5},
        environment_hash="hash",
        timestamp=datetime.now(timezone.utc)
    )
    
    with pytest.raises(ValidationError, match="frozen"):
        action.parameters = {"threshold": 0.9}


def test_action_equality_with_identical_fields():
    """Two Actions with identical fields are equal."""
    timestamp = datetime.now(timezone.utc)
    
    action1 = Action(
        action_id="A1",
        action_type="compute",
        inputs={"x": 10, "y": 20},
        parameters={"method": "sum"},
        environment_hash="hash123",
        timestamp=timestamp
    )
    
    action2 = Action(
        action_id="A1",
        action_type="compute",
        inputs={"x": 10, "y": 20},
        parameters={"method": "sum"},
        environment_hash="hash123",
        timestamp=timestamp
    )
    
    assert action1 == action2


def test_action_inequality_with_different_action_id():
    """Actions with different action_ids are not equal."""
    timestamp = datetime.now(timezone.utc)
    
    action1 = Action(
        action_id="A1",
        action_type="compute",
        inputs={},
        parameters={},
        environment_hash="hash",
        timestamp=timestamp
    )
    
    action2 = Action(
        action_id="A2",
        action_type="compute",
        inputs={},
        parameters={},
        environment_hash="hash",
        timestamp=timestamp
    )
    
    assert action1 != action2


def test_action_missing_required_field_action_id():
    """Missing action_id raises validation error."""
    with pytest.raises(ValidationError, match="action_id"):
        Action(
            action_type="test",
            inputs={},
            parameters={},
            environment_hash="hash",
            timestamp=datetime.now(timezone.utc)
        )


def test_action_missing_required_field_action_type():
    """Missing action_type raises validation error."""
    with pytest.raises(ValidationError, match="action_type"):
        Action(
            action_id="A1",
            inputs={},
            parameters={},
            environment_hash="hash",
            timestamp=datetime.now(timezone.utc)
        )


def test_action_missing_required_field_inputs():
    """Missing inputs raises validation error."""
    with pytest.raises(ValidationError, match="inputs"):
        Action(
            action_id="A1",
            action_type="test",
            parameters={},
            environment_hash="hash",
            timestamp=datetime.now(timezone.utc)
        )


def test_action_missing_required_field_environment_hash():
    """Missing environment_hash raises validation error."""
    with pytest.raises(ValidationError, match="environment_hash"):
        Action(
            action_id="A1",
            action_type="test",
            inputs={},
            parameters={},
            timestamp=datetime.now(timezone.utc)
        )


def test_action_serialization_to_dict():
    """Action serialization to dict preserves all fields."""
    timestamp = datetime.now(timezone.utc)
    action = Action(
        action_id="A1",
        action_type="transform",
        inputs={"data": [1, 2, 3]},
        parameters={"scale": 2},
        environment_hash="env_abc",
        timestamp=timestamp
    )
    
    action_dict = action.model_dump()
    
    assert action_dict["action_id"] == "A1"
    assert action_dict["action_type"] == "transform"
    assert action_dict["inputs"] == {"data": [1, 2, 3]}
    assert action_dict["parameters"] == {"scale": 2}
    assert action_dict["environment_hash"] == "env_abc"
    assert action_dict["timestamp"] == timestamp


def test_action_serialization_to_json():
    """Action serialization to JSON preserves all fields."""
    timestamp = datetime.now(timezone.utc)
    action = Action(
        action_id="A1",
        action_type="process",
        inputs={"value": 42},
        parameters={"mode": "fast"},
        environment_hash="hash_xyz",
        timestamp=timestamp
    )
    
    json_str = action.model_dump_json()
    
    # Verify JSON is valid and contains expected fields
    assert '"action_id":"A1"' in json_str
    assert '"action_type":"process"' in json_str
    assert '"value":42' in json_str
    assert '"mode":"fast"' in json_str
    assert '"environment_hash":"hash_xyz"' in json_str


def test_action_deserialization_from_dict():
    """Action can be reconstructed from serialized dict without data loss."""
    original = Action(
        action_id="A1",
        action_type="analyze",
        inputs={"dataset": "test.csv"},
        parameters={"algorithm": "linear"},
        environment_hash="hash_001",
        timestamp=datetime.now(timezone.utc)
    )
    
    # Serialize and deserialize
    serialized = original.model_dump()
    reconstructed = Action(**serialized)
    
    assert reconstructed == original


def test_action_timestamp_defaults_to_utcnow():
    """Action timestamp defaults to current UTC time if not provided."""
    before = datetime.now(timezone.utc)
    
    action = Action(
        action_id="A1",
        action_type="test",
        inputs={},
        parameters={},
        environment_hash="hash"
    )
    
    after = datetime.now(timezone.utc)
    
    # Timestamp should be between before and after
    assert before <= action.timestamp <= after
