# prism/core.py

from dataclasses import dataclass

from .models.dataschema import DataschemaModel
from .models.block import BlockModel
from .models.ir import IRModel
from .models.recipe import RecipeModel

from .resolvers.register import ResolverRegister
from .compiler.recipe_compiler import RecipeCompiler
from .generators.jinja_aggregator import JinjaAggregator
from .generators.pydantic_generator import PydanticGenerator
from .entities import CompilationSources, CompilationArtifacts

from .exceptions import ModelNotFoundError

from .schemas.schema_validator import (
    validate_block_file,
    validate_dataschema_file,
    validate_recipe_file
)

def _validate_all(sources: CompilationSources):
    # 1. 迭代验证每个 block 文件
    for block_id, block_data in sources.blocks.items():
        validate_block_file(block_data)
    # 2. 迭代验证每个 dataschema 文件
    for schema_id, schema_data in sources.dataschemas.items():
        validate_dataschema_file(schema_data)
    # 3. 验证单个 recipe 文件
    validate_recipe_file(sources.recipe)

def _build_resolver_from_sources(sources: CompilationSources) -> ResolverRegister:
    # 1. 验证输入数据
    _validate_all(sources)

    resolver = ResolverRegister()
    # 2. 注册模板
    for template_id, content in sources.templates.items():
        resolver.register_template(template_id, content)

    # 3. 验证并注册所有 Dataschemas
    for schema_id, data in sources.dataschemas.items():
        schema_model = DataschemaModel(**data)
        if not schema_model or not schema_model.id == schema_id:
            raise ModelNotFoundError(model_type="Dataschema", identifier=schema_id)
        resolver.register_dataschema(schema_model)

    # 4. 验证并注册所有 Blocks
    for block_id, data in sources.blocks.items():
        block_model = BlockModel(**data)
        if not block_model or not block_model.meta.id == block_id:
            raise ModelNotFoundError(model_type="Block", identifier=block_id)
        resolver.register_block(block_model)
    return resolver

def _compile_recipe_to_ir(sources: CompilationSources) -> IRModel:
    resolver = _build_resolver_from_sources(sources)
    recipe_model = RecipeModel(**sources.recipe)
    compiler = RecipeCompiler(resolver)
    ir : IRModel = compiler.compile(recipe_model)
    return ir

def compile_recipe_to_artifacts(sources: CompilationSources) -> CompilationArtifacts:
    ir = _compile_recipe_to_ir(sources)
    jinja = JinjaAggregator.aggregate(ir)
    pydantic = PydanticGenerator.generate(ir)

    return CompilationArtifacts(
        template_content=jinja,
        model_code=pydantic
    )
