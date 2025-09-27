# -*- coding: utf-8 -*-
# models/ir.py

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union

from .base import MetaModel
from .dataschema import DataschemaModel

class ResolvedBlock(BaseModel):
    """
    IR中的核心元素：一个被完全解析、准备好渲染的 Block 变体。
    """
    source_ref: str = Field(
        ..., 
        description="来自 Recipe 的引用标识，例如 'persona' 或 'tasks[1]'"
    )
    
    # --- 解析后的核心内容 ---
    template_content: str = Field(
        ..., 
        description="最终的、从 ID 解析出的模板字符串"
    )
    runtime_contract: Optional[DataschemaModel] = Field(
        None, 
        description="关联的运行时数据契约（如果存在）"
    )
    
    # --- 用于调试和追溯的元数据 ---
    source_block_meta: MetaModel
    source_variant_id: str
    merged_defaults: Dict[str, Any] = Field(
        ..., 
        description="按 Variant > Block 优先级合并后的最终兜底值"
    )

class LiteralContent(BaseModel):
    """
    IR中的字面量元素，直接来自 recipe.composition.sequence 中的 'literal'。
    """
    content: str

# 定义一个类型别名，用于表示最终渲染序列中的项
RenderSequenceItem = Union[ResolvedBlock, LiteralContent]

class IRModel(BaseModel):
    """
    中间表示（Intermediate Representation）模型。
    这是编译器最终的、无歧义的产物，也是代码生成器的唯一输入。
    """
    source_recipe_meta: MetaModel = Field(
        ..., 
        description="源 Recipe 的 meta 信息"
    )
    
    # 这个列表给 JinjaAggregator 使用，用于拼接最终模板
    render_sequence: List[RenderSequenceItem]
    
    # 这个字典给 PydanticGenerator 使用，用于生成数据类
    # Key 是 contract 的 ID，用于自动去重
    aggregated_contracts: Dict[str, DataschemaModel] = Field(
        default_factory=dict,
        description="编译过程中收集到的所有运行时数据契约的集合"
    )
