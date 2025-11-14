from typing import List, Optional
from pydantic import BaseModel
from extract_and_fill.domain.models import Section, Sentence


class Command(BaseModel):
    pass


class CreateEmbeddingCommand(Command):
    sentence_group_id: str


class CreateTranscriptionCommand(Command):
    type: str = "CreateTranscriptionCommand"
    transcriptText: str
    autoScribeSectionId: str
    autoScribeTranscriptionId: str
    autoScribeTranscriptionVersion: int


class ExtractSectionCommand(Command):
    type: str = "ExtractSectionCommand"
    index: int
    sectionId: str
    transcriptId: str
    transcriptText: str
    transcriptVersion: str
    promptTemplate: dict
    model: str


class FireStoreTriggerToCommandConvertor:
    def convert(self, collection: str, doc: str, before: Optional[dict], after: Optional[dict]):
        if collection == 'extract_embeddings_metadata' and after:
            return [CreateEmbeddingCommand(sentence_group_id=after.get("sentence_group_id"))]
        if collection == 'autoscribe_transactions' and after:
            commands = []
            last_updated_section = after.get("last_updated_section")
            if after.get("sections"):
                version_new = after.get("sections").get(last_updated_section).get("version")
                version_before = before.get("sections", {}).get(last_updated_section, {}).get("version", 0)
                if version_new > version_before:
                    for section_name, values in after.get("sections").items():
                        if last_updated_section == section_name:
                            autoScribeTranscriptionId = f"{after.get('id')}-{section_name}"
                            commands.append(
                                CreateTranscriptionCommand(
                                    autoScribeSectionId=section_name,
                                    autoScribeTranscriptionId=autoScribeTranscriptionId,
                                    autoScribeTranscriptionVersion=version_new,
                                    transcriptText="\n".join(
                                        [sentence.get("text") for sentence in values.get("text_sentences")]
                                    ),
                                )
                            )
            return commands
        if collection == "extract_commands":
            if after.get("type") == "ExtractSectionCommand":
                return [
                    ExtractSectionCommand(
                        index=after.get("index"),
                        sectionId=after.get("sectionId"),
                        transcriptId=after.get("transcriptId"),
                        transcriptText=after.get("transcriptText"),
                        transcriptVersion=after.get("transcriptVersion"),
                        promptTemplate=after.get("promptTemplate"),
                        model=after.get("model"),
                    )
                ]
