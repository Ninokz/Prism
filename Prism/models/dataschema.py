# -*- coding: utf-8 -*-
# models/dataschema.py

from pydantic import BaseModel
from typing import Any, Dict

from .base import MetaModel, Identifiable

# meta:
#   id: ds_persona_input
#   name: "Persona Configuration Schema"
#   description: "Defines the configurable parameters for the AI persona."
# data:
#   $schema: "https://json-schema.org/draft/2020-12/schema"
#   title: "PersonaInput"
#   type: object
#   required: [language, teaching_tone]
#   additionalProperties: false
#   properties:
#     language:
#       type: string
#       description: "The programming language for the persona."
#       default: "Python"
#     teaching_tone:
#       type: string
#       description: "The teaching style of the persona."
#       enum: ["gentle", "strict", "humorous"]
#       default: "gentle"

class DataschemaModel(BaseModel, Identifiable):
    meta: MetaModel
    data: Dict[str, Any]

    def get_schema_default(self, property_name: str, default_value: Any = None) -> Any:
        """
        安全地从 data (JSON Schema) 的 properties 中获取指定属性的 'default' 值。
        """
        try:
            return self.data.get("properties", {}).get(property_name, {}).get("default", default_value)
        except (TypeError, AttributeError):
            return default_value

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