# Bad Path Fixtures

This directory contains fixture files that are intentionally invalid. Each file is designed to violate a specific rule defined in the project's schemas. They are used to test the robustness and error-handling capabilities of the schema validation and model parsing logic.

## Blocks (`/blocks`)

- `blk_empty_variants.block.yaml`: Violates `minItems: 1` rule for the `variants` array.
- `blk_extra_property.block.yaml`: Violates `additionalProperties: false` at the root level.
- `blk_invalid_block_type.block.yaml`: Violates `enum` constraint for `block_type`.
- `blk_missing_block_type.block.yaml`: Violates `required` rule, missing `block_type`.
- `blk_missing_meta.block.yaml`: Violates `required` rule, missing `meta`.
- `blk_variant_extra_property.block.yaml`: Violates `additionalProperties: false` within a variant.
- `blk_variant_missing_template_id.block.yaml`: Violates `required` rule within a variant, missing `template_id`.

## DataSchemas (`/dataschemas`)

- `ds_extra_property.dataschema.yaml`: Violates `additionalProperties: false` at the root level.
- `ds_meta_missing_id.dataschema.yaml`: Violates `required` rule within `meta`, missing `id`.
- `ds_missing_data.dataschema.yaml`: Violates `required` rule, missing the `data` object.

## Recipes (`/recipes`)

- `rec_extra_import_property.recipe.yaml`: Violates `additionalProperties: false` in the `imports` object.
- `rec_import_missing_variant_id.recipe.yaml`: Violates `required` rule within an import reference.
- `rec_missing_imports.recipe.yaml`: Violates `required` rule, missing the entire `imports` object.
- `rec_sequence_ambiguous_item.recipe.yaml`: Violates `oneOf` rule in a sequence item by providing both `block_ref` and `literal`.
- `rec_sequence_empty_item.recipe.yaml`: Violates `oneOf` rule in a sequence item by providing neither `block_ref` nor `literal`.
