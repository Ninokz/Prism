# -*- coding: utf-8 -*-
# models/block.py

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, List, Literal, Optional

from .base import MetaModel, Identifiable
from ..exceptions import ModelError

BlockType = Literal["Persona", "Task", "OutputSpecification", "Rules", "Examples", "Context"]

class ProvidesDefaultsMixin:
    """
    一个 Mixin 类，为拥有 'defaults: Optional[Dict[str, Any]]' 属性的模型
    提供安全的访问方法。
    """
    # 这是一个类型注解，告诉类型检查器，使用此 Mixin 的类应该有这个属性
    defaults: Optional[Dict[str, Any]]

    def get_default(self, key: str, default_value: Any = None) -> Any:
        """
        安全地从 'defaults' 字典中获取一个值。
        如果 'defaults' 本身是 None，或者 key 不存在，则返回指定的 default_value。
        """
        if self.defaults is None:
            return default_value
        return self.defaults.get(key, default_value)

class Variant(BaseModel, ProvidesDefaultsMixin):
    model_config = ConfigDict(extra='forbid')
    id: str
    description: Optional[str] = None
    defaults: Optional[Dict[str, Any]] = None
    template_id: str
    contract_id: Optional[str] = None

class BlockModel(BaseModel, Identifiable, ProvidesDefaultsMixin):
    model_config = ConfigDict(extra='forbid')
    meta: MetaModel
    block_type: BlockType
    defaults: Optional[Dict[str, Any]] = None
    variants: List[Variant] = Field(..., min_length=1)

    def get_variant_by_id(self, variant_id: str) -> Variant:
        for v in self.variants:
            if v.id == variant_id:
                return v
        raise ModelError(f"在 Block '{self.id}' 中未找到 ID 为 '{variant_id}' 的变体。")
