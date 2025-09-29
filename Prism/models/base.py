# -*- coding: utf-8 -*-
# models/meta.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from abc import ABC, abstractmethod

class MetaModel(BaseModel):
    """基础元模型类"""
    model_config = ConfigDict(extra='forbid')
    id: str
    name: str
    description: Optional[str] = None

    def __str__(self) -> str:
        return f'[{self.id}] {self.name}'

    def __repr__(self) -> str:
        result = {'id': self.id, 'name': self.name}
        if self.description:
            result['description'] = self.description
        return str(result)

    def __hash__(self) -> int:
        return hash(self.id)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MetaModel):
            return NotImplemented
        return self.id == other.id

class Identifiable(ABC):
    meta: MetaModel
    @property
    def id(self) -> str:
        return self.meta.id