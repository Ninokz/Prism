# tests/schemas/test_schema_loader.py

import pytest
import yaml
from unittest.mock import patch, MagicMock

from Prism.schemas.schema_loader import SchemaLoader
from Prism.exceptions import MetaSchemaFileError

@pytest.fixture(autouse=True)
def clear_schema_cache():
    """Fixture to automatically clear the schema cache before each test."""
    SchemaLoader._schemas.clear()
    yield
    SchemaLoader._schemas.clear()

class TestSchemaLoader:
    """Tests for the SchemaLoader class."""

    def test_get_block_schema_success(self):
        """Test successfully loading the block schema."""
        schema = SchemaLoader.get_block_schema()
        assert isinstance(schema, dict)
        assert schema['title'] == "Block File (MVP)"
        assert 'properties' in schema

    def test_get_dataschema_schema_success(self):
        """Test successfully loading the dataschema schema."""
        schema = SchemaLoader.get_dataschema_schema()
        assert isinstance(schema, dict)
        assert schema['title'] == "Dataschema File (MVP)"
        assert 'properties' in schema

    def test_get_recipe_schema_success(self):
        """Test successfully loading the recipe schema."""
        schema = SchemaLoader.get_recipe_schema()
        assert isinstance(schema, dict)
        assert schema['title'] == "Recipe File (V1 Final)"
        assert 'properties' in schema

    @patch('importlib.resources.read_text')
    def test_schema_caching_mechanism(self, mock_read_text: MagicMock):
        """Test that schemas are loaded only once and then cached."""
        # Mock the return value to be a valid YAML string
        mock_read_text.return_value = "title: 'Mocked Schema'"

        # First call should trigger the read
        schema1 = SchemaLoader.get_block_schema()
        assert schema1['title'] == 'Mocked Schema'
        mock_read_text.assert_called_once()

        # Second call should hit the cache and not trigger another read
        schema2 = SchemaLoader.get_block_schema()
        assert schema2['title'] == 'Mocked Schema'
        mock_read_text.assert_called_once() # Still called only once

    @patch('importlib.resources.read_text', side_effect=FileNotFoundError("File not found"))
    def test_load_schema_raises_filenotfound_and_has_correct_context(self, mock_read_text: MagicMock):
        """
        Test that MetaSchemaFileError is raised and contains the correct attributes.
        """
        # 1. 只断言异常类型，不检查消息
        with pytest.raises(MetaSchemaFileError) as exc_info:
            SchemaLoader.get_block_schema()

        # 2. 捕获异常对象 (exc_info.value) 并检查其属性
        assert exc_info.value.message == "Error in file 'block.file.schema.yaml'"
        assert exc_info.value.context['filename'] == 'block.file.schema.yaml'
        assert exc_info.value.context['error'] == 'File not found'

    @patch('importlib.resources.read_text', return_value="key: {invalid yaml")
    def test_load_schema_raises_yaml_error(self, mock_read_text: MagicMock):
        """Test that SchemaFileError is raised for invalid YAML syntax."""
        with pytest.raises(MetaSchemaFileError, match="Error parsing schema file"):
            SchemaLoader.get_block_schema()

