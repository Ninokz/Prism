# -*- coding: utf-8 -*-
# tests/compiler/test_defaults_merger.py

import pytest
from typing import Dict, Any

from Prism.compiler.defaults_merger import DefaultsMerger
from Prism.models.block import BlockModel

class TestDefaultsMerger:
    """
    Tests for the DefaultsMerger static class.
    
    These tests use the various `blk_merging_*` fixtures loaded by the
    `all_blocks` fixture in conftest.py.
    """

    def test_merge_override(self, all_blocks: Dict[str, Any]):
        """
        SCENARIO: Variant defaults should override block defaults for overlapping keys.
        FIXTURE: blk_merging_override.block.yaml
        """
        # 1. Setup: Load and parse the specific block data
        block_data = all_blocks["blk_merging_override"]
        block = BlockModel(**block_data)
        variant = block.get_variant_by_id("variant_override")

        # 2. Execute: Call the merge method
        merged = DefaultsMerger.merge(block.defaults, variant.defaults)

        # 3. Assert: Verify the merged result
        expected = {
            "language": "Go",         # Overridden by variant
            "log_level": "INFO",      # Kept from block
            "timeout": 60,            # Kept from block
            "strict_mode": True       # Added by variant
        }
        assert merged == expected
        assert merged["language"] == "Go", "Variant value should win."

    def test_merge_disjoint(self, all_blocks: Dict[str, Any]):
        """
        SCENARIO: Merging defaults where block and variant have no overlapping keys.
        FIXTURE: blk_merging_disjoint.block.yaml
        """
        # 1. Setup
        block_data = all_blocks["blk_merging_disjoint"]
        block = BlockModel(**block_data)
        variant = block.get_variant_by_id("variant_disjoint")

        # 2. Execute
        merged = DefaultsMerger.merge(block.defaults, variant.defaults)

        # 3. Assert
        expected = {
            "api_version": "v1",  # From block
            "retries": 3          # From variant
        }
        assert merged == expected

    def test_merge_block_only(self, all_blocks: Dict[str, Any]):
        """
        SCENARIO: Merging when only block-level defaults are present.
        FIXTURE: blk_merging_block_only.block.yaml
        """
        # 1. Setup
        block_data = all_blocks["blk_merging_block_only"]
        block = BlockModel(**block_data)
        variant = block.get_variant_by_id("variant_no_defaults")
        
        # Sanity check: variant.defaults should be None in the model
        assert variant.defaults is None

        # 2. Execute
        merged = DefaultsMerger.merge(block.defaults, variant.defaults)

        # 3. Assert: The result should be identical to the block's defaults
        expected = {
            "format": "json",
            "indent": 2
        }
        assert merged == expected
        assert merged == block.defaults

    def test_merge_variant_only(self, all_blocks: Dict[str, Any]):
        """
        SCENARIO: Merging when only variant-level defaults are present.
        FIXTURE: blk_merging_variant_only.block.yaml
        """
        # 1. Setup
        block_data = all_blocks["blk_merging_variant_only"]
        block = BlockModel(**block_data)
        variant = block.get_variant_by_id("variant_with_defaults")

        # Sanity check: block.defaults should be None in the model
        assert block.defaults is None

        # 2. Execute
        merged = DefaultsMerger.merge(block.defaults, variant.defaults)

        # 3. Assert: The result should be identical to the variant's defaults
        expected = {
            "tone": "friendly",
            "verbosity": "high"
        }
        assert merged == expected
        assert merged == variant.defaults

    def test_merge_no_defaults(self, all_blocks: Dict[str, Any]):
        """
        SCENARIO: Merging when neither the block nor the variant has defaults.
        FIXTURE: blk_merging_no_defaults.block.yaml
        """
        # 1. Setup
        block_data = all_blocks["blk_merging_no_defaults"]
        block = BlockModel(**block_data)
        variant = block.get_variant_by_id("variant_no_defaults")

        # Sanity check: both should be None
        assert block.defaults is None
        assert variant.defaults is None

        # 2. Execute
        merged = DefaultsMerger.merge(block.defaults, variant.defaults)

        # 3. Assert: The result should be an empty dictionary
        assert merged == {}

    def test_merge_with_direct_none_and_empty_dict_inputs(self):
        """
        SCENARIO: Test edge cases by directly passing None or {} to the method,
                  bypassing file loading. This tests the method in isolation.
        """
        block_d = {"a": 1}
        variant_d = {"b": 2}

        # Both None
        assert DefaultsMerger.merge(None, None) == {}
        
        # One None
        assert DefaultsMerger.merge(block_d, None) == block_d
        assert DefaultsMerger.merge(None, variant_d) == variant_d
        
        # One empty dict
        assert DefaultsMerger.merge(block_d, {}) == block_d
        assert DefaultsMerger.merge({}, variant_d) == variant_d
        
        # Both empty dicts
        assert DefaultsMerger.merge({}, {}) == {}
