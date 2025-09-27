# -*- coding: utf-8 -*-
# models/dataschema.py

from pydantic import BaseModel
from typing import Any, Dict

from .base import MetaModel, Identifiable

class DataschemaModel(BaseModel, Identifiable):
    meta: MetaModel
    data: Dict[str, Any]

    def get_schema_default(self, property_name: str, default_value: Any = None) -> Any:
        """
        安全地从 data (JSON Schema) 的 properties 中获取指定属性的 'default' 值。
        这个版本使用更明确的检查，而不是 try-except。
        """
        properties = self.data.get("properties")
        # 1. 检查 'properties' 字段是否存在且为字典
        if not isinstance(properties, dict):
            return default_value
        prop_details = properties.get(property_name)
        # 2. 检查具体属性 (如 'language') 是否存在且为字典
        if not isinstance(prop_details, dict):
            return default_value
        # 3. 安全地获取 'default' 值，如果不存在则返回 default_value
        return prop_details.get("default", default_value)

    def get_all_schema_defaults(self) -> Dict[str, Any]:
        """
        提取并返回 schema 中定义的所有 'default' 值。
        这个方法对于编译器合并 defaults 尤其有用。
        """
        defaults = {}
        properties = self.data.get("properties", {})
        if not isinstance(properties, dict):
            return {}

        for prop_name, prop_details in properties.items():
            if isinstance(prop_details, dict) and "default" in prop_details:
                defaults[prop_name] = prop_details["default"]
        return defaults