from paperglass.infrastructure.ports import IPromptAdapter
from kink import inject
import json

@inject()
async def extract(prompt_config, prompt_adapter:IPromptAdapter):
    prompt_config = json.loads(prompt_config)
    return await prompt_adapter.extract(prompt_config.get("prompt_text"), prompt_config.get("model"))