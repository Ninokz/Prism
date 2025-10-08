# -*- coding: utf-8 -*-
# models/ir.py

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union

from .base import MetaModel
from .dataschema import DataschemaModel

class ResolvedBlock(BaseModel):
    """ Represents a resolved block in the IR, containing all necessary information for rendering """
    source_ref: str = Field(
        ..., 
        description="Reference marks from the Recipe. eg 'persona' or 'tasks[1]'"
    )
    
    # 解析后的核心内容
    template_content: str = Field(
        ..., 
        description="Full template content after resolving imports and variants"
    )

    runtime_contract: Optional[DataschemaModel] = Field(
        None, 
        description="Runtime contract associated with this block, if any"
    )
    
    # 用于调试和追溯的元数据
    source_block_meta: MetaModel
    source_variant_id: str
    merged_defaults: Dict[str, Any] = Field(
        ..., 
        description="Merged defaults from Variant > Block level"
    )

class LiteralContent(BaseModel):
    """ Literal string content in the IR render sequence """
    content: str

# 定义一个类型别名，用于表示最终渲染序列中的项
RenderSequenceItem = Union[ResolvedBlock, LiteralContent]

class IRModel(BaseModel):
    """ Intermediate Representation(IR) """
    source_recipe_meta: MetaModel = Field(
        ..., 
        description="Source metadata from the original Recipe"
    )
    
    # 这个列表给 JinjaAggregator 使用，用于拼接最终模板
    render_sequence: List[RenderSequenceItem]
    
    # 这个字典给 PydanticGenerator 使用，用于生成数据类
    # Key 是 contract 的 ID，用于自动去重
    aggregated_contracts: Dict[str, DataschemaModel] = Field(
        default_factory=dict,
        description="Collection of all unique data contracts referenced in the IR"
    )
