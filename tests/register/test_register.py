# tests/resolvers/test_register.py

import pytest
from typing import Dict, Any

from Prism.resolvers.register import ResolverRegister
from Prism.models.block import BlockModel
from Prism.models.dataschema import DataschemaModel
from Prism.exceptions import ModelError,ModelNotFoundError

@pytest.fixture
def resolver_register() -> ResolverRegister:
    """提供一个空的、干净的 ResolverRegister 实例供每个测试使用。"""
    return ResolverRegister()

class TestResolverRegisterUnit:
    """对 ResolverRegister 的核心单元功能进行测试。"""

    def test_initialization(self, resolver_register: ResolverRegister):
        """测试 ResolverRegister 初始化后是否为空。"""
        assert not resolver_register._blocks
        assert not resolver_register._dataschemas
        assert not resolver_register._templates

    def test_register_and_resolve_block(self, resolver_register: ResolverRegister, block_persona: Dict[str, Any]):
        """测试成功注册和解析单个 BlockModel。"""
        # 准备：将字典数据转换为模型实例
        block_model = BlockModel(**block_persona)
        
        # 操作：注册
        resolver_register.register_block(block_model)
        
        # 验证：解析
        resolved_block = resolver_register.resolve_block("blk_persona")
        
        assert resolved_block is not None
        assert resolved_block == block_model
        assert resolved_block.id == "blk_persona"

    def test_register_and_resolve_dataschema(self, resolver_register: ResolverRegister, dataschema_code_input: Dict[str, Any]):
        """测试成功注册和解析单个 DataschemaModel。"""
        # 准备
        dataschema_model = DataschemaModel(**dataschema_code_input)
        
        # 操作
        resolver_register.register_dataschema(dataschema_model)
        
        # 验证
        resolved_schema = resolver_register.resolve_dataschema("ds_code_input")
        
        assert resolved_schema is not None
        assert resolved_schema == dataschema_model
        assert resolved_schema.id == "ds_code_input"

    def test_register_and_resolve_template(self, resolver_register: ResolverRegister, template_persona_expert: str):
        """测试成功注册和解析单个模板。"""
        template_id = "tpl_persona_expert"
        
        # 操作
        resolver_register.register_template(template_id, template_persona_expert)
        
        # 验证
        resolved_template = resolver_register.resolve_template(template_id)
        
        assert resolved_template is not None
        assert resolved_template == template_persona_expert
        assert "{{ language }}" in resolved_template

class TestResolverRegisterErrorHandling:
    """测试 ResolverRegister 的错误处理和边界情况。"""

    @pytest.mark.parametrize("resolve_method, item_id", [
        ("resolve_block", "non_existent_block"),
        ("resolve_dataschema", "non_existent_schema"),
        ("resolve_template", "non_existent_template"),
    ])
    def test_resolve_not_found_raises_model_error(self, resolver_register: ResolverRegister, resolve_method: str, item_id: str):
        """测试解析不存在的资源时是否会引发 ModelError。"""
        with pytest.raises(ModelNotFoundError) as exc_info:
            # 使用 getattr 动态调用解析方法
            getattr(resolver_register, resolve_method)(item_id)
        
        # 验证错误信息是否清晰
        assert f"'{item_id}' not found" in str(exc_info.value)

    def test_registering_duplicate_id_overwrites(self, resolver_register: ResolverRegister, block_persona: Dict[str, Any]):
        """测试使用相同的 ID 注册会覆盖先前的值。"""
        # 第一次注册
        original_block = BlockModel(**block_persona)
        original_name = original_block.meta.name
        resolver_register.register_block(original_block)
        
        # 创建一个同ID但不同内容的新 Block
        modified_data = block_persona.copy()
        modified_data["meta"]["name"] = "Overwritten Persona"
        overwriting_block = BlockModel(**modified_data)
        
        # 第二次注册
        resolver_register.register_block(overwriting_block)
        
        # 验证
        resolved_block = resolver_register.resolve_block("blk_persona")
        
        # 验证1: 确认内容已被更新 (这是最重要的验证)
        assert resolved_block.meta.name == "Overwritten Persona"
        assert resolved_block.meta.name != original_name

        # 验证2: 确认对象实例已被替换 (更严格的检查)
        assert resolved_block is not original_block, "The object in the register should be a different instance."
        
        # 验证3: 确认注册表中只有一个条目
        assert len(resolver_register._blocks) == 1

class TestResolverRegisterIntegration:
    """
    使用 'happypath' 中的所有数据进行集成测试，
    模拟真实应用场景中加载所有资源的流程。
    """
    
    @pytest.fixture(scope="class")
    def populated_register(self, complete_fixture_set: Dict[str, Any]) -> ResolverRegister:
        """创建一个预填充了所有 'happypath' 数据的 ResolverRegister 实例。"""
        register = ResolverRegister()
        
        # 注册所有 blocks
        for block_id, block_data in complete_fixture_set["blocks"].items():
            register.register_block(BlockModel(**block_data))
            
        # 注册所有 dataschemas
        for schema_id, schema_data in complete_fixture_set["dataschemas"].items():
            register.register_dataschema(DataschemaModel(**schema_data))
            
        # 注册所有 templates
        for template_id, template_content in complete_fixture_set["templates"].items():
            register.register_template(template_id, template_content)
            
        return register

    def test_all_items_are_registered(self, populated_register: ResolverRegister, complete_fixture_set: Dict[str, Any]):
        """验证所有资源都已成功注册。"""
        assert len(populated_register._blocks) == len(complete_fixture_set["blocks"])
        assert len(populated_register._dataschemas) == len(complete_fixture_set["dataschemas"])
        assert len(populated_register._templates) == len(complete_fixture_set["templates"])

    @pytest.mark.parametrize("block_id_to_check", ["blk_persona", "blk_task", "blk_output"])
    def test_can_resolve_any_registered_block(self, populated_register: ResolverRegister, block_id_to_check: str):
        """抽样测试是否可以解析任何已注册的 block。"""
        resolved_block = populated_register.resolve_block(block_id_to_check)
        assert isinstance(resolved_block, BlockModel)
        assert resolved_block.id == block_id_to_check

    def test_can_resolve_any_registered_dataschema(self, populated_register: ResolverRegister):
        """抽样测试是否可以解析任何已注册的 dataschema。"""
        resolved_schema = populated_register.resolve_dataschema("ds_code_input")
        assert isinstance(resolved_schema, DataschemaModel)
        assert resolved_schema.id == "ds_code_input"

    @pytest.mark.parametrize("template_id_to_check", ["tpl_persona_expert", "tpl_task_explain_code", "tpl_output_json"])
    def test_can_resolve_any_registered_template(self, populated_register: ResolverRegister, template_id_to_check: str):
        """抽样测试是否可以解析任何已注册的 template。"""
        resolved_template = populated_register.resolve_template(template_id_to_check)
        assert isinstance(resolved_template, str)
        assert len(resolved_template) > 0

