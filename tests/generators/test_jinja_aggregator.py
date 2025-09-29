# tests/generators/test_jinja_aggregator.py

import pytest
from typing import Set

from Prism.generators.jinja_aggregator import JinjaAggregator
from Prism.models.ir import IRModel, ResolvedBlock, LiteralContent
from Prism.exceptions import GenerationError

# ===================================================================
#
#                       STATIC METHOD TESTS
#
# ===================================================================

class TestJinjaAggregatorHelpers:
    """
    单元测试 JinjaAggregator 的静态辅助方法。
    """

    def test_collect_runtime_vars(self, compiled_ir: IRModel):
        """
        测试 _collect_runtime_vars 是否能正确地从 IR 中提取所有运行时变量。
        """
        # --- Act ---
        runtime_vars = JinjaAggregator._collect_runtime_vars(compiled_ir)

        # --- Assert ---
        assert isinstance(runtime_vars, set)
        # ds_code_input.dataschema.yaml 中定义了 'user_code'
        assert runtime_vars == {"user_code"}

    def test_collect_runtime_vars_with_no_contracts(self, compiled_ir: IRModel):
        """
        测试当 IR 中没有数据契约时，返回一个空集合。
        """
        # --- Arrange ---
        ir_no_contracts = compiled_ir.model_copy(deep=True)
        ir_no_contracts.aggregated_contracts = {}

        # --- Act ---
        runtime_vars = JinjaAggregator._collect_runtime_vars(ir_no_contracts)

        # --- Assert ---
        assert runtime_vars == set()

# ===================================================================
#
#                       AGGREGATION TESTS
#
# ===================================================================

class TestJinjaAggregation:
    """
    测试核心的 aggregate 方法。
    """

    def test_aggregate_happy_path(self, compiled_ir: IRModel):
        """
        测试完整的 happy path，验证编译期变量被渲染，运行时变量被保留。
        """
        # --- Act ---
        final_template = JinjaAggregator.aggregate(compiled_ir)

        # --- Assert ---
        # 1. 验证编译期变量被正确替换
        # 来自 blk_persona 的 'language' 和 'teaching_tone'
        assert "expert in TypeScript" in final_template
        assert "a strict teaching style" in final_template
        # 来自 blk_output 的 'confidence_score_default'
        assert "Default to 0.95" in final_template
        
        # 2. 验证运行时变量被正确保留 (以 Jinja 语法)
        # 来自 blk_task 的 'user_code'
        assert "{{ user_code }}" in final_template

        # 3. 验证 LiteralContent 被正确插入
        assert "\n\n---\n\n" in final_template
        assert "\n\n### REQUIRED OUTPUT FORMAT\n" in final_template

        # 4. 验证最终输出是一个拼接好的字符串
        assert isinstance(final_template, str)
        # 检查一些拼接的边界
        assert "beginner." in final_template  # persona 结尾
        assert "Your task" in final_template # task 开头
        assert "key components." in final_template # task 结尾

    def test_aggregate_with_only_compile_time_vars(self, compiled_ir: IRModel):
        """
        测试一个只包含编译期变量的模板。
        """
        # --- Arrange ---
        # 创建一个只包含 persona block 的简化版 IR
        ir_simple = compiled_ir.model_copy(deep=True)
        ir_simple.render_sequence = [
            item for item in compiled_ir.render_sequence if isinstance(item, ResolvedBlock) and item.source_ref == "persona"
        ]
        ir_simple.aggregated_contracts = {}

        # --- Act ---
        final_template = JinjaAggregator.aggregate(ir_simple)

        # --- Assert ---
        assert "expert in TypeScript" in final_template
        assert "a strict teaching style" in final_template
        # 确认没有任何未解析的 {{...}}
        assert "{{" not in final_template
        assert "}}" not in final_template

    def test_aggregate_with_only_runtime_vars(self, compiled_ir: IRModel):
        """
        测试一个只包含运行时变量的模板。
        """
        # --- Arrange ---
        # 创建一个只包含 task block 的简化版 IR
        ir_simple = compiled_ir.model_copy(deep=True)
        ir_simple.render_sequence = [
            item for item in compiled_ir.render_sequence if isinstance(item, ResolvedBlock) and item.source_ref == "tasks[0]"
        ]
        # aggregated_contracts 保持不变

        # --- Act ---
        final_template = JinjaAggregator.aggregate(ir_simple)

        # --- Assert ---
        assert "{{ user_code }}" in final_template
        # 确认除了 user_code 外没有其他变量
        assert final_template.count("{{") == 1
        assert final_template.count("}}") == 1

    def test_aggregate_raises_error_for_undefined_variable(self, compiled_ir: IRModel):
        """
        测试当模板中存在一个未定义的变量时，是否会抛出 GenerationError。
        """
        # --- Arrange ---
        # 复制一份 IR 并篡改其中一个模板
        ir_bad_template = compiled_ir.model_copy(deep=True)
        
        # 找到 persona block 并加入一个未定义的变量
        for item in ir_bad_template.render_sequence:
            if isinstance(item, ResolvedBlock) and item.source_ref == "persona":
                item.template_content += " and your favorite food is {{ undefined_food }}."
                break
        
        # --- Act & Assert ---
        with pytest.raises(GenerationError) as exc_info:
            JinjaAggregator.aggregate(ir_bad_template)

        # 验证错误信息是否清晰、有帮助
        error_message = str(exc_info.value)
        assert "在处理 Block 'persona' 时发现未定义的变量" in error_message
        assert "'undefined_food' is undefined" in error_message
        assert "请确保所有非运行时变量都在 block/variant 的 'defaults' 中定义" in error_message
