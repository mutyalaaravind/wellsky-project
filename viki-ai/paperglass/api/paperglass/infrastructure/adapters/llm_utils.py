from enum import Enum
from typing import Any

class PromptType(str, Enum):
    STRING  = 'string'
    TEXT    = 'text'
    FILE    = 'file'
    INLINE  = 'inline'


def get_prompt_type(prompt: Any) -> PromptType:
    if isinstance(prompt, str):
        return PromptType.STRING
    else:
        dict_prompt = prompt.to_dict()

        if "text" in dict_prompt:
            return PromptType.TEXT
        if "file_data" in dict_prompt:
            return PromptType.FILE
        if "inline_data" in dict_prompt:
            return PromptType.INLINE
        else:
            keys = []
            for key in dict_prompt.keys():
                keys.append(key)                
            raise ValueError("Prompt type '%s' not recognized", ",".join(keys))
    