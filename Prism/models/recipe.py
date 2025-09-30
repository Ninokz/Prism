# -*- coding: utf-8 -*-
# models/recipe.py

from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import List, Optional

from .base import MetaModel, Identifiable
from ..exceptions import ModelError

class ImportRef(BaseModel):
    """Reference to an imported Block variant"""
    model_config = ConfigDict(extra='forbid')
    block_id: str
    variant_id: str

class ImportsModel(BaseModel):
    """ Represents the imports section of a Recipe, containing references to various Block types"""
    model_config = ConfigDict(extra='forbid')
    # 单实例
    persona: Optional[ImportRef] = None
    output_spec: Optional[ImportRef] = None
    # 多实例
    tasks: List[ImportRef] = []
    rules: List[ImportRef] = []
    examples: List[ImportRef] = []
    contexts: List[ImportRef] = []

class SequenceItem(BaseModel):
    """ An item in the composition sequence, either a block reference or a literal string """
    model_config = ConfigDict(extra='forbid')
    block_ref: Optional[str] = None
    literal: Optional[str] = None

    @model_validator(mode='after')
    def check_exclusive_fields(self) -> 'SequenceItem':
        if not (self.block_ref is None) ^ (self.literal is None):
            raise ModelError("Must provide exactly one of 'block_ref' or 'literal'")
        return self

class CompositionModel(BaseModel):
    """ The composition section of a Recipe, defining the sequence of blocks and literals """
    model_config = ConfigDict(extra='forbid')
    sequence: List[SequenceItem]

class RecipeModel(BaseModel, Identifiable):
    """ The top-level Recipe model, encapsulating metadata, imports, and composition """
    model_config = ConfigDict(extra='forbid')
    meta: MetaModel
    imports: ImportsModel
    composition: CompositionModel
