# -*- coding: utf-8 -*-
# prism/exceptions.py

from typing import Optional, Any, Dict, List

class PrismError(Exception):
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.context = context or {}

    def __str__(self) -> str:
        class_name = self.__class__.__name__
        output = f"{class_name}: {self.message}"
        if self.context:
            context_str = "\n".join(
                f"  - {key}: {repr(value)}" for key, value in self.context.items()
            )
            output += f"\n[Context]:\n{context_str}"
        return output
    
class TemplatedPrismError(PrismError):
    message_template: str = "An unspecified error occurred."
    def __init__(self, **kwargs: Any):
        formatted_message = self.message_template.format(**kwargs)
        super().__init__(formatted_message, context=kwargs)


class MetaSchemaFileError(TemplatedPrismError):
    """元 schema 文件处理异常。"""
    message_template = "Error in file '{filename}'"

    def __init__(self, filename: str, error: str):
        super().__init__(filename=filename, error=error)

class SchemaValidationError(TemplatedPrismError):
    """JSON Schema验证失败。"""
    message_template = "{schema_type} schema validation failed with {error_count} error(s)"

    def __init__(self, schema_type: str, errors: List[str]):
        error_summary = '; '.join(errors)
        super().__init__(
            schema_type=schema_type, 
            errors=errors, 
            error_count=len(errors),
            error_summary=error_summary
        )

class DataValidationError(TemplatedPrismError):
    """数据验证失败。"""
    message_template = "{data_type} data{identifier_part} validation failed"

    def __init__(self, data_type: str, errors: List[str], identifier: Optional[str] = None):
        identifier_part = f" '{identifier}'" if identifier else ""
        super().__init__(
            data_type=data_type,
            identifier=identifier,
            errors=errors,
            error_count=len(errors),
            identifier_part=identifier_part
        )

class ModelError(PrismError):
    pass

class ModelNotFoundError(TemplatedPrismError):
    message_template = "{model_type} with identifier '{identifier}' not found"

    def __init__(self, model_type: str, identifier: str):
        super().__init__(model_type=model_type, identifier=identifier)

class VariantNotFoundError(TemplatedPrismError):
    message_template = "Variant '{variant_id}' not found in Block '{block_id}'"

    def __init__(self, block_id: str, variant_id: str):
        super().__init__(block_id=block_id, variant_id=variant_id)

class GenerationError(PrismError):
    """生成相关的异常"""
    pass