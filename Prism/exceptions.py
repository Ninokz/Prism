# -*- coding: utf-8 -*-
# prism/exceptions.py

from typing import Optional, Any, Dict, List

class PrismError(Exception):
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.context = context or {}

    def __str__(self) -> str:
        class_name = self.__class__.__name__
        output = f"{class_name}: {self.message}"
        if self.context:
            context_str = "\n".join(
                f"  - {key}: {repr(value)}" for key, value in self.context.items()
            )
            output += f"\n[Context]:\n{context_str}"
        return output
    
class TemplatedPrismError(PrismError):
    message_template: str = "An unspecified error occurred"

    def __init__(self, **kwargs: Any):
        formatted_message = self.message_template.format(**kwargs)
        super().__init__(formatted_message, context=kwargs)

class MetaSchemaFileError(TemplatedPrismError):
    message_template = "Could not load or parse the file '{filename}'. Reason: {error}"

    def __init__(self, filename: str, error: str):
        super().__init__(filename=filename, error=error)

class InternalSchemaError(TemplatedPrismError):
    message_template = (
        "Internal validation failed for schema '{internal_schema_file_name}'. "
        "This is likely a bug in Prism itself. Please report this issue. Details: {error_summary}"
    )

    def __init__(self, internal_schema_file_name: str, errors: List[str]):
        error_summary = '; '.join(errors)
        super().__init__(
            internal_schema_file_name=internal_schema_file_name,
            errors=errors,
            error_summary=error_summary
        )

class AssetValidationError(TemplatedPrismError):
    message_template = (
        "The content of '{asset_file_name}' is invalid and does not conform to the schema. "
        "Found {error_count} error(s):\n- {error_details}"
    )

    def __init__(self, asset_file_name: str, errors: List[str]):
        error_details = "\n- ".join(errors)
        super().__init__(
            asset_file_name=asset_file_name,
            errors=errors,
            error_count=len(errors),
            error_details=error_details
        )

class ModelError(PrismError):
    pass

class ModelIDMismatchError(TemplatedPrismError):
    message_template = (
        "ID mismatch in {model_type} file '{file_id}.{model_type}.yaml'. "
        "The filename ID is '{file_id}', but the ID inside the file (meta.id) is '{content_id}'. "
        "Please make them consistent."
    )
    
    def __init__(self, model_type: str, file_id: str, content_id: str):
        super().__init__(
            model_type=model_type, file_id=file_id, content_id=content_id
        )

class ResolutionError(TemplatedPrismError):
    """
    Raised by the ResolverRegister when an asset (Block, Dataschema, Template)
    cannot be found by its identifier during the resolution phase.
    """
    message_template = (
        "Could not resolve {asset_type} with ID '{identifier}'. "
        "It was referenced by: {source_context}."
    )
    def __init__(self, asset_type: str, identifier: str, source_context: str = "an unknown location"):
        super().__init__(
            asset_type=asset_type, identifier=identifier, source_context=source_context
        )

class VariantNotFoundError(TemplatedPrismError):
    message_template = (
        "Variant '{variant_id}' not found in Block '{block_id}'. "
        "Available variants are: {available_variants}."
    )
    def __init__(self, block_id: str, variant_id: str, available_variants: List[str]):
        available_str = ", ".join(f"'{v}'" for v in available_variants) if available_variants else "None"
        super().__init__(
            block_id=block_id, variant_id=variant_id, available_variants=available_str
        )

class RecipeError(TemplatedPrismError):
    pass

class RecipeReferenceError(TemplatedPrismError):
    message_template = (
        "Reference '{reference}' in the recipe's composition sequence could not be resolved. "
        "It is not defined in the 'imports' section."
    )
    def __init__(self, reference: str):
        super().__init__(reference=reference)

class RecipePropertyError(TemplatedPrismError):
    message_template = "Recipe property error: {message}"
    def __init__(self, message: str):
        super().__init__(message=message)

class GenerationError(PrismError):
    message_template = "Generation error: {message}"
    def __init__(self, message: str):
        super().__init__(message=message)