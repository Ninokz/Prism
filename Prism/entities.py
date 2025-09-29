# prism/entities.py

from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass(frozen=True)
class CompilationSources:
    """
    一个纯粹的数据容器，用于存放从文件系统加载的所有原生资源。
    与 Prism 核心库之间新的、简单的契约。
    """
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
    """
    一个用于封装编译产物的数据类，作为 Facade 函数的返回类型。
    """
    template_content: str
    model_code: Optional[str] = None