# prism/entities.py

from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass(frozen=True)
class CompilationSources:
    """Data container for holding raw compilation sources."""
    # Key: template_id (通常是文件名), Value: 模板文件内容
    templates: Dict[str, str] = field(default_factory=dict)
    
    # Key: dataschema_id, Value: 从 YAML 加载的原生 dict
    dataschemas: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Key: block_id, Value: 从 YAML 加载的原生 dict
    blocks: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # 单独的 Recipe 原生 dict
    recipe: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CompilationArtifacts:
    """Data container for holding compilation results."""
    template_content: str
    model_code: Optional[str] = None