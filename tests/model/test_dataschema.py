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

class TestDataschemaModelFromBadFixtures:
    """
    Tests the DataschemaModel's ability to reject invalid data structures
    loaded directly from the 'badpath' fixture files.
    """
    @pytest.mark.parametrize(
        "bad_schema_id",
        [
            "ds_extra_property",
            "ds_meta_missing_id",
            "ds_missing_data",
            "ds_data_not_object", # <--- 新增的测试用例
        ]
    )
    def test_instantiation_from_bad_fixtures_raises_validation_error(
        self, 
        bad_schema_id: str, 
        all_bad_dataschemas: Dict[str, Dict[str, Any]]
    ):
        """
        Verify that attempting to instantiate DataschemaModel with any of the
        'bad' dataschema fixtures raises a Pydantic ValidationError.
        This test is parameterized to run for each specified bad schema ID.
        """
        # Arrange: Get the specific bad data dictionary from the collection fixture
        bad_data = all_bad_dataschemas.get(bad_schema_id)
        assert bad_data is not None, f"Bad fixture '{bad_schema_id}' not found in all_bad_dataschemas fixture."

        # Act & Assert: Expect a ValidationError when instantiating the model
        with pytest.raises(ValidationError):
            try:
                DataschemaModel(**bad_data)
            except ValidationError as e:
                # 打印错误信息，便于调试
                print(f"\nValidation failed as expected for '{bad_schema_id}':\n{e}")
                raise # 重新抛出异常，让 pytest.raises 捕获