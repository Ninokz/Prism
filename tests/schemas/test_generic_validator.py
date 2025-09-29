# tests/schemas/test_generic_validator.py

import pytest
from typing import Dict, Any

from Prism.schemas.generic_validator import _validate_by_schema, _validate_metaschema, _safe_get_identifier
from Prism.exceptions import DataValidationError, SchemaValidationError

# A minimal valid schema for testing purposes
VALID_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {"name": {"type": "string"}},
    "required": ["name"]
}

# A minimal invalid schema (violates metaschema)
INVALID_SCHEMA = {
    "type": "object",
    "properties": {"name": {"type": "invalid_type"}}
}

class TestGenericValidatorInternals:
    """Tests for the internal functions of generic_validator."""

    def test_validate_metaschema_success(self):
        """Test that a valid schema passes metaschema validation."""
        try:
            _validate_metaschema(VALID_SCHEMA, "test_schema")
        except SchemaValidationError:
            pytest.fail("Valid metaschema should not raise SchemaValidationError")

    def test_validate_metaschema_failure(self):
        """Test that an invalid schema fails metaschema validation."""
        with pytest.raises(SchemaValidationError) as exc_info:
            _validate_metaschema(INVALID_SCHEMA, "test_schema")
        
        error_string = str(exc_info.value)
        assert "'invalid_type'" in error_string
        assert "is not valid under any of the given schemas" in error_string


    @pytest.mark.parametrize("data, expected_id", [
        ({"meta": {"id": "test-123"}}, "test-123"),
        ({"meta": {"name": "No ID"}}, None),
        ({"data": {}}, None),
        ({"meta": "not a dict"}, None),
    ])
    def test_safe_get_identifier(self, data: Dict[str, Any], expected_id: str):
        """Test the safe retrieval of an identifier from data."""
        assert _safe_get_identifier(data) == expected_id

class TestValidateBySchema:
    """Tests for the core _validate_by_schema function."""

    def test_validation_success(self):
        """Test successful validation of valid data against a valid schema."""
        valid_data = {"name": "John Doe"}
        try:
            _validate_by_schema("test_data", valid_data, VALID_SCHEMA)
        except DataValidationError:
            pytest.fail("Valid data should not raise DataValidationError")

    def test_validation_failure_with_invalid_data(self):
        """Test that invalid data raises DataValidationError."""
        invalid_data = {"age": 30} # Missing 'name'
        with pytest.raises(DataValidationError) as exc_info:
            _validate_by_schema("test_data", invalid_data, VALID_SCHEMA)
        
        error = exc_info.value
        assert error.data_type == "test_data"
        assert error.identifier is None # No 'meta.id' in test data
        assert len(error.errors) == 1
        assert "'name' is a required property" in error.errors[0]

    def test_validation_failure_with_identifier(self):
        """Test that the identifier is correctly captured in the exception."""
        invalid_data = {"meta": {"id": "user-profile"}, "age": 30}
        with pytest.raises(DataValidationError) as exc_info:
            _validate_by_schema("test_data", invalid_data, VALID_SCHEMA)
        
        assert exc_info.value.identifier == "user-profile"

    def test_validation_raises_schema_error_for_invalid_schema(self):
        """Test that an invalid schema raises SchemaValidationError."""
        valid_data = {"name": "John Doe"}
        with pytest.raises(SchemaValidationError):
            _validate_by_schema("test_data", valid_data, INVALID_SCHEMA)

