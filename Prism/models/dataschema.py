# -*- coding: utf-8 -*-
# models/dataschema.py

from pydantic import BaseModel, ConfigDict
from typing import Any, Dict

from .base import MetaModel, Identifiable

class DataschemaModel(BaseModel, Identifiable):
    model_config = ConfigDict(extra='forbid')
    meta: MetaModel
    data: Dict[str, Any]