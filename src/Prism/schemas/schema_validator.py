# -*- coding: utf-8 -*-
# schema_validator.py

from typing import Any, Dict

from .generic_validator import validate_by_schema
from .schema_loader import SchemaLoader,_BLOCK_FILE_SCHEMA_YAML, _DATA_SCHEMA_FILE_SCHEMA_YAML, _RECIPE_FILE_SCHEMA_YAML
from ..exceptions import InternalSchemaError, AssetValidationError

def validate_block_file(block_file_name: str, block_data: Dict[str, Any]) -> None:
    validate_by_schema(_BLOCK_FILE_SCHEMA_YAML, SchemaLoader.get_block_schema(), block_file_name, block_data)

def validate_dataschema_file(dataschema_file_name: str, dataschema_data: Dict[str, Any]) -> None:
    validate_by_schema(_DATA_SCHEMA_FILE_SCHEMA_YAML, SchemaLoader.get_dataschema_schema(), dataschema_file_name, dataschema_data)

def validate_recipe_file(recipe_file_name: str, recipe_data: Dict[str, Any]) -> None:
    validate_by_schema(_RECIPE_FILE_SCHEMA_YAML, SchemaLoader.get_recipe_schema(), recipe_file_name, recipe_data)

def is_valid_block_file(block_file_name: str, block_data: Dict[str, Any]) -> bool:
    """verify block file raw data"""
    try:
        validate_block_file(block_file_name, block_data)
        return True
    except (InternalSchemaError, AssetValidationError):
        return False
    except Exception:
        raise

def is_valid_dataschema_file(dataschema_file_name: str, dataschema_data: Dict[str, Any]) -> bool:
    """verify dataschema file raw data"""
    try:
        validate_dataschema_file(dataschema_file_name, dataschema_data)
        return True
    except (InternalSchemaError, AssetValidationError):
        return False
    except Exception:
        raise

def is_valid_recipe_file(recipe_file_name: str, recipe_data: Dict[str, Any]) -> bool:
    """verify recipe file raw data"""
    try:
        validate_recipe_file(recipe_file_name, recipe_data)
        return True
    except (InternalSchemaError, AssetValidationError):
        return False
    except Exception:
        raise