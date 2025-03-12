import re
from typing import Dict, Any

def camel_to_snake(s: str) -> str:
    """Convert camelCase string to snake_case."""
    return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()

def snake_to_camel(s: str) -> str:
    """Convert snake_case string to camelCase."""
    components = s.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def camel_to_snake_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """Convert dictionary with camelCase keys to snake_case keys."""
    result = {}
    for k, v in d.items():
        snake_key = camel_to_snake(k)
        if isinstance(v, dict):
            result[snake_key] = camel_to_snake_dict(v)
        elif isinstance(v, list) and v and isinstance(v[0], dict):
            result[snake_key] = [camel_to_snake_dict(item) for item in v]
        else:
            result[snake_key] = v
    return result

def snake_to_camel_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """Convert dictionary with snake_case keys to camelCase keys."""
    result = {}
    for k, v in d.items():
        camel_key = snake_to_camel(k)
        if isinstance(v, dict):
            result[camel_key] = snake_to_camel_dict(v)
        elif isinstance(v, list) and v and isinstance(v[0], dict):
            result[camel_key] = [snake_to_camel_dict(item) for item in v]
        else:
            result[camel_key] = v
    return result