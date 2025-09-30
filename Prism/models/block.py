# -*- coding: utf-8 -*-
# models/block.py

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, List, Literal, Optional

from .base import MetaModel, Identifiable
from ..exceptions import VariantNotFoundError

BlockType = Literal["Persona", "Task", "OutputSpecification", "Rules", "Examples", "Context"]

class ProvidesDefaultsMixin:
    """ a Mixin to provide default value retrieval functionality """
    # 这是一个类型注解，告诉类型检查器，使用此 Mixin 的类应该有这个属性
    defaults: Optional[Dict[str, Any]]

    def get_default(self, key: str, default_value: Any = None) -> Any:
        if self.defaults is None:
            return default_value
        return self.defaults.get(key, default_value)

class Variant(BaseModel, ProvidesDefaultsMixin):
    """variant of a Block, each with its own template and optional contract"""
    model_config = ConfigDict(extra='forbid')
    id: str
    description: Optional[str] = None
    defaults: Optional[Dict[str, Any]] = None
    template_id: str
    contract_id: Optional[str] = None

class BlockModel(BaseModel, Identifiable, ProvidesDefaultsMixin):
    """block definition with multiple variants"""
    model_config = ConfigDict(extra='forbid')
    meta: MetaModel
    block_type: BlockType
    defaults: Optional[Dict[str, Any]] = None
    variants: List[Variant] = Field(..., min_length=1)

    def get_variant_by_id(self, variant_id: str) -> Variant:
        for v in self.variants:
            if v.id == variant_id:
                return v
        raise VariantNotFoundError(block_id=self.id, variant_id=variant_id)
