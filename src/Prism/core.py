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
from .entities import CompilationSources, CompilationArtifacts, CompilationTask

from .exceptions import ModelIDMismatchError

from .schemas.schema_validator import (
    validate_block_file,
    validate_dataschema_file,
    validate_recipe_file
)

def _build_resolver_from_sources(sources: CompilationSources) -> ResolverRegister:
    print("Validating blocks and dataschemas...")
    # 1. 验证输入数据
    for block_id, block_data in sources.blocks.items():
        validate_block_file(block_id,block_data)
    for schema_id, schema_data in sources.dataschemas.items():
        validate_dataschema_file(schema_id, schema_data)
    resolver = ResolverRegister()

    print("Registering templates, dataschemas, and blocks...")
    # 2. 注册模板
    for template_id, content in sources.templates.items():
        resolver.register_template(template_id, content)

    # 3. 注册 Dataschemas
    for schema_id, data in sources.dataschemas.items():
        schema_model = DataschemaModel(**data)
        
        if schema_model.id != schema_id:
            raise ModelIDMismatchError(
                model_type="Dataschema",
                file_id=schema_id,
                content_id=schema_model.id
            )
        resolver.register_dataschema(schema_model)

    # 4. 验证并注册所有 Blocks
    for block_id, data in sources.blocks.items():
        block_model = BlockModel(**data)
        
        if block_model.id != block_id:
            raise ModelIDMismatchError(
                model_type="Block",
                file_id=block_id,
                content_id=block_model.id
            )
        resolver.register_block(block_model)
    print("Done.")
    return resolver

def compile_recipe_to_artifacts(recipe: CompilationTask, sources: CompilationSources) -> CompilationArtifacts:
    validate_recipe_file(recipe.recipe_name, recipe.sources)
    resolver = _build_resolver_from_sources(sources)
    recipe_model = RecipeModel(**recipe.sources)
    compiler = RecipeCompiler(resolver)

    ir : IRModel = compiler.compile(recipe_model)
    
    jinja = JinjaAggregator.aggregate(ir)
    pydantic = PydanticGenerator.generate(ir)
    return CompilationArtifacts(
        template_content=jinja,
        model_code=pydantic
    )
