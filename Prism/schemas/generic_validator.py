# -*- coding: utf-8 -*-
# generic_validator.py

import jsonschema
from typing import Dict, Any

from ..exceptions import (
    SchemaValidationError,
    DataValidationError
)

def _validate_metaschema(meta_schema: Dict[str, Any], schema_type: str) -> None:
    """验证给定的meta_schema是否符合JSON Schema规范
    
    Args:
        meta_schema: 要验证的meta_schema字典
        schema_type: schema类型标识符，用于错误报告
        
    Raises:
        SchemaValidationError: 如果meta_schema无效
    """
    try:
        jsonschema.Draft202012Validator.check_schema(meta_schema)
    except jsonschema.SchemaError as e:
        raise SchemaValidationError(
            schema_type=schema_type,
            errors=[str(e)]
        ) from e

def _safe_get_identifier(data: Dict[str, Any]) -> str | None:
    """尝试从data数据中安全地获取block_id"""
    try:
        return data['meta']['id']
    except (KeyError, TypeError):
        return None

def _validate_by_schema(data_type: str, raw_data: Dict[str, Any], file_schema: Dict[str, Any]) -> None:
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
