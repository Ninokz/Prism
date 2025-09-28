# tests/model/test_dataschema.py

import pytest
from pydantic import ValidationError
from typing import Dict, Any

from Prism.models.dataschema import DataschemaModel
from Prism.models.base import MetaModel

class TestDataschemaModel:
    """Tests for the DataschemaModel class."""

    def test_instantiation_from_valid_data(self, dataschema_code_input: Dict[str, Any]):
        """
        Test that a DataschemaModel can be successfully instantiated from a valid fixture.
        """
        # Act
        schema = DataschemaModel(**dataschema_code_input)

        # Assert
        assert isinstance(schema, DataschemaModel)
        assert isinstance(schema.meta, MetaModel)
        assert schema.meta.id == "ds_code_input"
        assert schema.meta.name == "Code Input Schema"
        
        # Test Identifiable property
        assert schema.id == "ds_code_input"
        
        # Assert the data payload is correctly loaded
        assert isinstance(schema.data, dict)
        assert schema.data['title'] == "CodeInput"
        assert "user_code" in schema.data['required']

    def test_identifiable_property(self, dataschema_code_input: Dict[str, Any]):
        """
        Explicitly test the 'id' property inherited from Identifiable.
        """
        schema = DataschemaModel(**dataschema_code_input)
        assert schema.id == schema.meta.id

class TestDataschemaModelValidation:
    """Tests for Pydantic validation rules on DataschemaModel."""

    def test_raises_error_on_missing_meta(self, dataschema_code_input: Dict[str, Any]):
        """A DataschemaModel must have a 'meta' field."""
        invalid_data = dataschema_code_input.copy()
        del invalid_data["meta"]
        
        with pytest.raises(ValidationError, match="meta\n  Field required"):
            DataschemaModel(**invalid_data)

    def test_raises_error_on_missing_data(self, dataschema_code_input: Dict[str, Any]):
        """A DataschemaModel must have a 'data' field."""
        invalid_data = dataschema_code_input.copy()
        del invalid_data["data"]
        
        with pytest.raises(ValidationError, match="data\n  Field required"):
            DataschemaModel(**invalid_data)

    def test_raises_error_on_invalid_data_type(self, dataschema_code_input: Dict[str, Any]):
        """The 'data' field must be a dictionary."""
        invalid_data = dataschema_code_input.copy()
        invalid_data["data"] = "not a dict"
        
        with pytest.raises(ValidationError, match="data\n  Input should be a valid dictionary"):
            DataschemaModel(**invalid_data)

