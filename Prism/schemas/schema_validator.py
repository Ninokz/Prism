# -*- coding: utf-8 -*-
# schema_validator.py

from typing import Any, Dict

from .generic_validator import validate_by_schema
from .schema_loader import SchemaLoader,_BLOCK_FILE_SCHEMA_YAML, _DATA_SCHEMA_FILE_SCHEMA_YAML, _RECIPE_FILE_SCHEMA_YAML
from ..exceptions import SchemaValidationError, DataValidationError

def validate_block_file(data: Dict[str, Any]) -> None:
    validate_by_schema(_BLOCK_FILE_SCHEMA_YAML, data, SchemaLoader.get_block_schema())

def validate_dataschema_file(data: Dict[str, Any]) -> None:
    validate_by_schema(_DATA_SCHEMA_FILE_SCHEMA_YAML, data, SchemaLoader.get_dataschema_schema())

def validate_recipe_file(data: Dict[str, Any]) -> None:
    validate_by_schema(_RECIPE_FILE_SCHEMA_YAML, data, SchemaLoader.get_recipe_schema())

def is_valid_block_file(data: Dict[str, Any]) -> bool:
    """verify block file raw data"""
    try:
        validate_block_file(data)
        return True
    except (SchemaValidationError, DataValidationError):
        return False
    except Exception:
        raise

def is_valid_dataschema_file(data: Dict[str, Any]) -> bool:
    """verify dataschema file raw data"""
    try:
        validate_dataschema_file(data)
        return True
    except (SchemaValidationError, DataValidationError):
        return False
    except Exception:
        raise

def is_valid_recipe_file(data: Dict[str, Any]) -> bool:
    """verify recipe file raw data"""
    try:
        validate_recipe_file(data)
        return True
    except (SchemaValidationError, DataValidationError):
        return False
    except Exception:
        raise