# -*- coding: utf-8 -*-
# compiler/defaults_merger.py

from typing import Any, Dict, Optional

class DefaultsMerger:
    @staticmethod
    def merge(
        block_defaults: Optional[Dict[str, Any]] = None,
        variant_defaults: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        merged = {}
        if block_defaults:
            merged.update(block_defaults)
        if variant_defaults:
            merged.update(variant_defaults)
        return merged
