# -*- coding: utf-8 -*-
# generators/jinja_aggregator.py

import jinja2
from jinja2 import Environment, StrictUndefined
from typing import Set

from ..models.ir import IRModel, ResolvedBlock, LiteralContent
from ..exceptions import GenerationError

class JinjaAggregator:
    @staticmethod
    def aggregate(ir: IRModel) -> str:
        """ Aggregate and partially render Jinja templates based on the IR's render sequence. """
        final_template_parts = []
        
        # 步骤 1: 收集所有已知的运行时变量名
        runtime_vars = JinjaAggregator._collect_runtime_vars(ir)

        # 步骤 2: 创建一个特殊的 Jinja 环境，用于处理部分渲染
        env = JinjaAggregator._create_partial_render_env(runtime_vars)

        # 步骤 3: 遍历渲染序列并处理每一项
        for item in ir.render_sequence:
            if isinstance(item, LiteralContent):
                final_template_parts.append(item.content)
            
            elif isinstance(item, ResolvedBlock):
                try:
                    template = env.from_string(item.template_content)
                    partially_rendered_content = template.render(item.merged_defaults)
                    final_template_parts.append(partially_rendered_content)
                except jinja2.exceptions.UndefinedError as e:
                    error_message = (
                        f"Undefined variable found while processing Block '{item.source_ref}': {e.message}. "
                        f"Please ensure all non-runtime variables are defined in the block/variant 'defaults'."
                    )
                    raise GenerationError(error_message) from e
                except jinja2.exceptions.TemplateSyntaxError as e:
                    error_message = (
                        f"Syntax error in Jinja template of Block '{item.source_ref}' at line {e.lineno}: {e.message}"
                    )
                    raise GenerationError(error_message) from e
        
        return "".join(final_template_parts)

    @staticmethod
    def _collect_runtime_vars(ir: IRModel) -> Set[str]:
        """Collect all runtime variable names from the aggregated contracts in the IR."""
        runtime_vars: Set[str] = set()
        for contract in ir.aggregated_contracts.values():
            properties = contract.data.get("properties")
            if isinstance(properties, dict):
                runtime_vars.update(properties.keys())
        return runtime_vars

    @staticmethod
    def _create_partial_render_env(runtime_vars: Set[str]) -> Environment:
        """Create a Jinja environment that preserves placeholders for runtime variables."""

        class PreserveRuntimeUndefined(StrictUndefined):
            """ Self-defined Undefined that preserves runtime variables """
            def __str__(self):
                if self._undefined_name in runtime_vars:
                    return f"{{{{ {self._undefined_name} }}}}"
                # 如果不是运行时变量，StrictUndefined 的基类实现会负责抛出异常
                return super().__str__()

        return Environment(undefined=PreserveRuntimeUndefined)
