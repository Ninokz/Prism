# tests/schemas/test_schema_loader.py

import pytest
import yaml
from unittest.mock import patch, MagicMock

from Prism.schemas.schema_loader import SchemaLoader
from Prism.exceptions import SchemaFileError

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
    def test_load_schema_raises_filenotfound(self, mock_read_text: MagicMock):
        """Test that SchemaFileError is raised for a missing file."""
        with pytest.raises(SchemaFileError, match="Schema file .* not found"):
            SchemaLoader.get_block_schema()

    @patch('importlib.resources.read_text', return_value="key: {invalid yaml")
    def test_load_schema_raises_yaml_error(self, mock_read_text: MagicMock):
        """Test that SchemaFileError is raised for invalid YAML syntax."""
        with pytest.raises(SchemaFileError, match="Error parsing schema file"):
            SchemaLoader.get_block_schema()

