# -*- coding: utf-8 -*-
# models/dataschema.py

from pydantic import BaseModel
from typing import Any, Dict

from .base import MetaModel, Identifiable

class DataschemaModel(BaseModel, Identifiable):
    meta: MetaModel
    data: Dict[str, Any]