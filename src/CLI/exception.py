# -*- coding: utf-8 -*-
# CLI/exceptions.py

from typing import Optional, Any, Dict, List

class CLIError(Exception):
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

class ProjectilitializationError(CLIError):
    def __init__(self, project_path: str, reason: str):
        message = f"Failed to initialize project at '{project_path}'. Reason: {reason}"
        super().__init__(message, context={"project_path": project_path, "reason": reason})

class ScaffoldError(CLIError):
    def __init__(self, file_type: str, file_name: str, reason: str):
        message = f"Failed to create {file_type} '{file_name}'. Reason: {reason}"
        super().__init__(message, context={"file_type": file_type, "file_name": file_name, "reason": reason})

class LoaderError(CLIError):
    def __init__(self, file_type: str, file_name: str, reason: str):
        message = f"Failed to load {file_type} '{file_name}'. Reason: {reason}"
        super().__init__(message, context={"file_type": file_type, "file_name": file_name, "reason": reason})