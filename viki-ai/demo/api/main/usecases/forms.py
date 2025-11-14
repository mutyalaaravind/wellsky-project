from kink import inject

from main.infrastructure.ports import IFormRepositoryPort


@inject
async def get_form_instance(id: str, form_repository: IFormRepositoryPort) -> dict:
    return await form_repository.get_form_instance(id)


@inject
async def save_form_instance(id: str, data: dict, form_repository: IFormRepositoryPort):
    return await form_repository.save_form_instance(id, data)
