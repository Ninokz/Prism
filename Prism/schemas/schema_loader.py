from importlib import resources
import yaml
from typing import Dict, Any

from ..exceptions import SchemaFileError, PrismError

_DATA_SCHEMA_FILE_SCHEMA_YAML = 'dataschema.file.schema.yaml'
_BLOCK_FILE_SCHEMA_YAML = 'block.file.schema.yaml'
_RECIPE_FILE_SCHEMA_YAML = 'recipe.file.schema.yaml'

class SchemaLoader:
    _schemas: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def _load_schema(cls, filename: str) -> Dict[str, Any]:
        if __package__ is None:
            raise PrismError("Package 'schemas' is not defined")
        try:
            if filename not in cls._schemas:
                schema_text = resources.read_text(__package__, filename)
                cls._schemas[filename] = yaml.safe_load(schema_text)
            return cls._schemas[filename]
        except FileNotFoundError as e:
            raise SchemaFileError(f"Schema file '{filename}' not found") from e
        except yaml.YAMLError as e:
            raise SchemaFileError(f"Error parsing schema file '{filename}': {str(e)}") from e
        except (ImportError, AttributeError) as e:
            raise SchemaFileError(f"Error accessing schema file '{filename}': {str(e)}") from e
    
    @classmethod
    def get_dataschema_schema(cls) -> Dict[str, Any]:
        return cls._load_schema(_DATA_SCHEMA_FILE_SCHEMA_YAML)

    @classmethod
    def get_block_schema(cls) -> Dict[str, Any]:
        return cls._load_schema(_BLOCK_FILE_SCHEMA_YAML)

    @classmethod
    def get_recipe_schema(cls) -> Dict[str, Any]:
        return cls._load_schema(_RECIPE_FILE_SCHEMA_YAML)