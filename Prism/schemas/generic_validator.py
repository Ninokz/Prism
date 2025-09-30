# -*- coding: utf-8 -*-
# generic_validator.py

import jsonschema
from typing import Dict, Any

from ..exceptions import (
    SchemaValidationError,
    DataValidationError
)

def _validate_metaschema(meta_schema: Dict[str, Any], schema_type: str) -> None:
    """Verify that the provided meta-schema is itself valid."""
    try:
        jsonschema.Draft202012Validator.check_schema(meta_schema)
    except jsonschema.SchemaError as e:
        raise SchemaValidationError(
            schema_type=schema_type,
            errors=[str(e)]
        ) from e

def _safe_get_identifier(data: Dict[str, Any]) -> str | None:
    try:
        return data['meta']['id']
    except (KeyError, TypeError):
        return None

def validate_by_schema(data_type: str, raw_data: Dict[str, Any], file_schema: Dict[str, Any]) -> None:
    """Validate raw_data against the provided file_schema using JSON Schema."""
    try:
        _validate_metaschema(file_schema, data_type)

        validator = jsonschema.Draft202012Validator(file_schema)
        errors = sorted(validator.iter_errors(raw_data), key=lambda e: e.path)

        if errors:
            error_messages = [
                f"Path '{'.'.join(map(str, error.path))}': {error.message}" 
                for error in errors
            ]
            identifier = _safe_get_identifier(raw_data)
            raise DataValidationError(data_type=data_type, errors=error_messages, identifier=identifier)
    except SchemaValidationError:
        raise
    except (jsonschema.ValidationError, jsonschema.SchemaError) as e:
        identifier = _safe_get_identifier(raw_data)
        raise DataValidationError(
            data_type=data_type,
            errors=[f"JSON Schema validation failed: {str(e)}"],
            identifier=identifier
        ) from e
