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
from .defaults_merger import DefaultsMerger
from ..exceptions import RecipeReferenceError

# 中间表示中的 CompiledImport, 包含了从 ImportRef 到实际内容的所有解析结果
@dataclass(frozen=True)
class CompiledImport:
    source_ref: str
    block: BlockModel
    variant: Variant
    template_content: str
    contract: Optional[DataschemaModel]
    merged_defaults: Dict[str, Any]

class RecipeCompiler:
    """ run the compilation from RecipeModel to IRModel. """
    def __init__(self, resolver_register: ResolverRegister):
        self._resolver = resolver_register
        self._defaults_merger = DefaultsMerger()

    def compile(self, recipe: RecipeModel) -> IRModel:
        """ run the compilation from RecipeModel to IRModel. """

        # 1. 解析 Recipe 中定义的所有 imports，并构建一个扁平化、易于访问的字典。
        compiled_imports_map = self._resolve_all_imports(recipe)

        # 2. 根据 recipe.composition.sequence 构建最终的渲染序列和聚合的数据契约。
        render_sequence, aggregated_contracts = self._build_ir_components(
            recipe.composition.sequence,
            compiled_imports_map
        )

        # 3. 组装并返回最终的 IRModel。
        return IRModel(
            source_recipe_meta=recipe.meta,
            render_sequence=render_sequence,
            aggregated_contracts=aggregated_contracts
        )

    def _resolve_all_imports(self, recipe: RecipeModel) -> Dict[str, CompiledImport]:
        """ resolve and compile all imports defined in the Recipe into a flat map. """
        resolved_map: Dict[str, CompiledImport] = {}

        for import_key, import_value in recipe.imports.model_dump(exclude_none=True).items():
            if isinstance(import_value, list): # 多例 例如 tasks, rules
                for i, item in enumerate(import_value):
                    ref_str = f"{import_key}[{i}]"
                    import_ref = ImportRef(**item)
                    # 编译 ImportRef 为 CompiledImport
                    resolved_map[ref_str] = self._compile_single_import(ref_str, import_ref)
            else: # 单例 例如 persona, output_spec
                ref_str = import_key
                import_ref = ImportRef(**import_value)
                resolved_map[ref_str] = self._compile_single_import(ref_str, import_ref)
        return resolved_map

    def _compile_single_import(self, source_ref: str, import_ref: ImportRef) -> CompiledImport:
        """ Compile a single ImportRef into a CompiledImport by resolving all necessary components. """
        # 1. 解析 Block 和 Variant
        block = self._resolver.resolve_block(import_ref.block_id)
        variant = block.get_variant_by_id(import_ref.variant_id)
        # 2. 解析模板内容
        template_content = self._resolver.resolve_template(variant.template_id)
        # 3. 解析数据契约（如果有）
        contract: Optional[DataschemaModel] = None
        if variant.contract_id:
            contract = self._resolver.resolve_dataschema(variant.contract_id)
        # 4. 合并值 - 这里的优先级合并顺序是：Block < Variant
        merged_defaults = self._defaults_merger.merge(
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

    def _build_ir_components(
        self, 
        sequence_items: List[SequenceItem], 
        compiled_imports_map: Dict[str, CompiledImport]
    ) -> Tuple[List[RenderSequenceItem], Dict[str, DataschemaModel]]:
        """ act as a helper to build the render_sequence and aggregated_contracts for IRModel. """
        render_sequence: List[RenderSequenceItem] = []
        aggregated_contracts: Dict[str, DataschemaModel] = {}

        for itm in sequence_items:
            if itm.literal is not None:
                # 1. 处理 literal
                render_sequence.append(LiteralContent(content=itm.literal))
            elif itm.block_ref is not None:
                # 2. 处理 block_ref
                refs_to_process = self._expand_block_ref(itm.block_ref, list(compiled_imports_map.keys()))
                for block_ref in refs_to_process:
                    if block_ref not in compiled_imports_map:
                        raise RecipeReferenceError(
                            reference=block_ref
                        )

                    compiled_import = compiled_imports_map[block_ref]
                    # 3. 为 IR 创建 ResolvedBlock
                    resolved_block = ResolvedBlock(
                        source_ref=compiled_import.source_ref,
                        template_content=compiled_import.template_content,
                        runtime_contract=compiled_import.contract,
                        source_block_meta=compiled_import.block.meta,
                        source_variant_id=compiled_import.variant.id,
                        merged_defaults=compiled_import.merged_defaults
                    )
                    render_sequence.append(resolved_block)
                    # 4. 如果存在数据契约，则聚合它 (按ID去重)
                    if compiled_import.contract:
                        aggregated_contracts[compiled_import.contract.id] = compiled_import.contract

        return render_sequence, aggregated_contracts

    def _expand_block_ref(self, ref: str, available_refs: list[str]) -> list[str]:
        """ expand a block reference to actual import keys in compiled_imports_map. """
        # Case 1: 精确匹配 "persona" 或 "tasks[0]"
        if ref in available_refs:
            return [ref]
        
        # Case 2: 展开引用 "tasks"
        plural_refs = [key for key in available_refs if key.startswith(f"{ref}[")]
        if not plural_refs:
            # 如果未找到，让上层逻辑去抛出一个清晰的错误
            return [ref]

        # 使用 key 函数进行自然排序，确保 tasks[2] 在 tasks[10] 之前
        def natural_sort_key(s: str):
            match = re.search(r'\[(\d+)\]', s)
            return int(match.group(1)) if match else -1
        return sorted(plural_refs, key=natural_sort_key)
    