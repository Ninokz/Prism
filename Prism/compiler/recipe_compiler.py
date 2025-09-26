# -*- coding: utf-8 -*-
# compiler/recipe_compiler.py

import re
from typing import Any, Dict, List, Optional, Tuple, Iterable
from dataclasses import dataclass

from ..models.recipe import RecipeModel, ImportRef, SequenceItem
from ..models.block import BlockModel, Variant
from ..models.dataschema import DataschemaModel
from ..models.ir import IRModel, ResolvedBlock, LiteralContent, RenderSequenceItem
from ..resolvers.register import ResolverRegister
from ..compiler.defaults_merger import DefaultsMerger
from ..exceptions import CompilationError

# 中间表示中的 CompiledImport，包含了从 ImportRef 到实际内容的所有解析结果
@dataclass(frozen=True)
class CompiledImport:
    source_ref: str
    block: BlockModel
    variant: Variant
    template_content: str
    contract: Optional[DataschemaModel]
    merged_defaults: Dict[str, Any]

class RecipeCompiler:
    def __init__(self, resolver_register: ResolverRegister):
        self._resolver = resolver_register
        self._defaults_merger = DefaultsMerger()

    def compile(self, recipe: RecipeModel) -> IRModel:
        ...

    def _resolve_all_imports(self, recipe: RecipeModel) -> Dict[str, CompiledImport]:
        """
        预处理 recipe.imports 中的所有项。
        返回一个映射: { "persona": CompiledImport, "tasks[0]": CompiledImport, ... }
        """
        resolved_map: Dict[str, CompiledImport] = {}
        
        # 使用 model_dump 来安全地遍历 ImportsModel 的所有字段
        for import_key, import_value in recipe.imports.model_dump(exclude_none=True).items():
            if isinstance(import_value, list): # 例如 tasks, rules
                for i, item in enumerate(import_value):
                    ref_str = f"{import_key}[{i}]"
                    import_ref = ImportRef(**item)
                    # 编译 ImportRef 为 CompiledImport
                    resolved_map[ref_str] = self._compile_single_import(ref_str, import_ref)
            else: # 例如 persona, output_spec
                ref_str = import_key
                import_ref = ImportRef(**import_value)
                resolved_map[ref_str] = self._compile_single_import(ref_str, import_ref)
        return resolved_map

    def _compile_single_import(self, source_ref: str, import_ref: ImportRef) -> CompiledImport:
        """将单个 import 引用编译成一个信息丰富的 CompiledImport 对象。"""
        # --- 解析阶段 ---
        # 1. 解析 Block 和 Variant
        block = self._resolver.resolve_block(import_ref.block_id)
        variant = block.get_variant_by_id(import_ref.variant_id)
        # 2. 解析模板内容
        template_content = self._resolver.resolve_template(variant.template_id)
        # 3. 解析数据契约（如果有）
        contract: Optional[DataschemaModel] = None
        if variant.contract_id:
            contract = self._resolver.resolve_dataschema(variant.contract_id)
        # 4. 获取 Schema 级别的兜底值
        schema_defaults = contract.get_all_schema_defaults() if contract else {}
        # 5. 合并值 - 这里的合并顺序是：Schema < Block < Variant，后者优先级更高
        merged_defaults = self._defaults_merger.merge(
            schema_defaults = schema_defaults,
            block_defaults = block.defaults,
            variant_defaults = variant.defaults
        )

        return CompiledImport(
            source_ref=source_ref,
            block=block,
            variant=variant,
            template_content=template_content,
            contract=contract,
            merged_defaults=merged_defaults
        )

    # TODO: _build_ir_components 方法需要实现