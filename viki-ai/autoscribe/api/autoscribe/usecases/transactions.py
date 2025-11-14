from typing import List
from autoscribe.domain.models import Transaction
from autoscribe.domain.values import Section
from autoscribe.infrastructure.ports import IPersistencePort, ISpeechRecognitionFactory
from kink import inject


@inject
async def ensure_transaction(transaction_id: str, persistence: IPersistencePort):
    transaction = await persistence.get_transaction(transaction_id)
    if transaction is None:
        transaction = Transaction.create(transaction_id)
        await persistence.put_transaction(transaction)
    return transaction


class TransactionUsecaseError(Exception):
    pass


@inject
async def get_audio_signed_url(
    transaction_id: str,
    section_id: str,
    persistence: IPersistencePort,
    speech_recognition_factory: ISpeechRecognitionFactory,
) -> str:
    transaction = await persistence.get_transaction(transaction_id)
    if not transaction:
        raise TransactionUsecaseError(f'Transaction {transaction_id} not found')
    section = transaction.sections.get(section_id)
    if not section:
        raise TransactionUsecaseError(f'Section {section_id} not found')
    if section.backend is None:
        raise TransactionUsecaseError('This section does not have backend specified (this is historical data)')
    speech_recognition = speech_recognition_factory.get_implementation(
        ISpeechRecognitionFactory.Backend(section.backend)
    )
    return await speech_recognition.get_audio_signed_url(transaction_id, section_id)


@inject
async def finalize(
    transaction_id: str, section_id: str, text_sentences: List[str], persistence: IPersistencePort
) -> Section:
    transaction = await persistence.get_transaction(transaction_id)
    transaction.finalize_section(section_id, text_sentences)
    await persistence.put_transaction(transaction)
    return transaction.sections[section_id]
