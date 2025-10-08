# -*- coding: utf-8 -*-
# generic_validator.py

import jsonschema
from typing import Dict, Any

from ..exceptions import (
    InternalSchemaError,
    AssetValidationError
)

def _validate_metaschema(meta_schema_name: str, meta_schema_content: Dict[str, Any]) -> None:
    """Verify that the provided meta-schema is itself valid."""
    try:
        jsonschema.Draft202012Validator.check_schema(meta_schema_content)
    except jsonschema.SchemaError as e:
        raise InternalSchemaError(
            internal_schema_file_name=meta_schema_name,
            errors=[str(e)]
        ) from e

def _safe_get_identifier(data: Dict[str, Any]) -> str | None:
    try:
        return data['meta']['id']
    except (KeyError, TypeError):
        return None

def validate_by_schema(meta_schema_name: str, meta_schema_content: Dict[str, Any], validate_file: str, raw_data: Dict[str, Any]) -> None:
    """Validate raw_data against the provided file_schema using JSON Schema."""
    try:
        _validate_metaschema(meta_schema_name, meta_schema_content)

        validator = jsonschema.Draft202012Validator(meta_schema_content)
        validated_errors = sorted(validator.iter_errors(raw_data), key=lambda e: e.path)

        if validated_errors:
            error_messages = [
                f"Path '{'.'.join(map(str, error.path))}': {error.message}" 
                for error in validated_errors
            ]
            identifier = _safe_get_identifier(raw_data)
            raise AssetValidationError(asset_file_name=validate_file, errors=error_messages, identifier=identifier)
    except InternalSchemaError:
        raise
    except (jsonschema.ValidationError, jsonschema.SchemaError) as e:
        identifier = _safe_get_identifier(raw_data)
        raise AssetValidationError(
            asset_file_name=validate_file,
            errors=[f"JSON Schema validation failed: {str(e)}"],
            identifier=identifier
        ) from e
