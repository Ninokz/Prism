# -*- coding: utf-8 -*-
# resolvers/register.py

from typing import Dict

from ..models.block import BlockModel
from ..models.dataschema import DataschemaModel
from ..exceptions import ModelError

class ResolverRegister:
    def __init__(self):
        self._blocks: Dict[str, BlockModel] = {}
        self._dataschemas: Dict[str, DataschemaModel] = {}
        self._templates: Dict[str, str] = {}
    
    def register_block(self, block: BlockModel):
        self._blocks[block.id] = block

    def register_dataschema(self, schema: DataschemaModel):
        self._dataschemas[schema.id] = schema

    # 模板为了方便期间，未设置专门的 template 模板类型
    def register_template(self, template_id: str, content: str):
        self._templates[template_id] = content

    def resolve_block(self, block_id: str) -> BlockModel:
        if block_id not in self._blocks:
            raise ModelError(f"Block with id '{block_id}' not found.")
        return self._blocks[block_id]

    def resolve_dataschema(self, schema_id: str) -> DataschemaModel:
        if schema_id not in self._dataschemas:
            raise ModelError(f"Dataschema with id '{schema_id}' not found.")
        return self._dataschemas[schema_id]

    def resolve_template(self, template_id: str) -> str:
        if template_id not in self._templates:
            raise ModelError(f"Template with id '{template_id}' not found.")
        return self._templates[template_id]