# -*- coding: utf-8 -*-
# prism/exceptions.py

from typing import Optional, Any, Dict, List

class PrismError(Exception):
    """Prism工具的基础异常类"""
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.context = context or {}
    
    def __str__(self) -> str:
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} (context: {context_str})"
        return self.message

class SchemaFileError(PrismError):
    """基础 schema 文件异常"""
    pass

class ValidationError(PrismError):
    """验证相关的基础异常"""
    pass

class SchemaValidationError(ValidationError):
    """JSON Schema验证失败"""
    def __init__(self, schema_type: str, errors: List[str]):
        self.schema_type = schema_type
        self.errors = errors
        context = {"schema_type": schema_type, "error_count": len(errors), "errors": errors}
        super().__init__(
            f"{schema_type} schema validation failed: {'; '.join(errors)}",
            context
        )

class DataValidationError(ValidationError):
    """数据验证失败的基础异常"""
    def __init__(self, data_type: str, errors: List[str], identifier: Optional[str] = None):
        self.data_type = data_type
        self.errors = errors
        self.identifier = identifier
        
        if identifier:
            message = f"{data_type} data '{identifier}' validation failed: {'; '.join(errors)}"
            context = {"schema_type": data_type, "identifier": identifier, "error_count": len(errors)}
        else:
            message = f"{data_type} data validation failed: {'; '.join(errors)}"
            context = {"schema_type": data_type, "error_count": len(errors)}
            
        super().__init__(message, context)

class ModelError(PrismError):
    """模型属性异常"""
    pass

class GenerationError(PrismError):
    """生成相关的异常"""
    pass