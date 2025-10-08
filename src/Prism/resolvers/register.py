# -*- coding: utf-8 -*-
# resolvers/register.py

from typing import Dict

from ..models.block import BlockModel
from ..models.dataschema import DataschemaModel
from ..exceptions import ResolutionError

class ResolverRegister:
    """register and resolve models by their identifiers."""
    def __init__(self):
        self._blocks: Dict[str, BlockModel] = {}
        self._dataschemas: Dict[str, DataschemaModel] = {}
        self._templates: Dict[str, str] = {}
    
    def register_block(self, block: BlockModel):
        self._blocks[block.id] = block

    def register_dataschema(self, schema: DataschemaModel):
        self._dataschemas[schema.id] = schema

    def register_template(self, template_id: str, content: str):
        self._templates[template_id] = content

    def resolve_block(self, block_id: str) -> BlockModel:
        if block_id not in self._blocks:
            raise ResolutionError(asset_type='Block', identifier=block_id)
        return self._blocks[block_id]

    def resolve_dataschema(self, schema_id: str) -> DataschemaModel:
        if schema_id not in self._dataschemas:
            raise ResolutionError(asset_type='Dataschema', identifier=schema_id)
        return self._dataschemas[schema_id]

    def resolve_template(self, template_id: str) -> str:
        if template_id not in self._templates:
            raise ResolutionError(asset_type='Template', identifier=template_id)
        return self._templates[template_id]
