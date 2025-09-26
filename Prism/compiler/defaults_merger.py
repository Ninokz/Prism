# -*- coding: utf-8 -*-
# compiler/defaults_merger.py

from typing import Any, Dict, Optional

class DefaultsMerger:
    @staticmethod
    def merge(
        schema_defaults: Optional[Dict[str, Any]] = None,
        block_defaults: Optional[Dict[str, Any]] = None,
        variant_defaults: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        merged = {}
        if schema_defaults:
            merged.update(schema_defaults)
        if block_defaults:
            merged.update(block_defaults)
        if variant_defaults:
            merged.update(variant_defaults)
        return merged
