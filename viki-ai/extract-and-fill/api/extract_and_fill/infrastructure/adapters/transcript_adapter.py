import uuid, datetime
from google.cloud.firestore import AsyncClient as AsyncFirestoreClient

from extract_and_fill.infrastructure.ports import ITranscriptPort


class TranscriptFireStoreAdapter(ITranscriptPort):
    TRANSCRIPT_COLLECTION = u"extract_transcripts"
    AUTOSCRIBE_TRANSCRIPT_COLLECTION = u"extract_autoscribe_transcripts"

    def __init__(self, project_id, location, db_name) -> None:
        if db_name != "(default)":
            self.db = AsyncFirestoreClient(project=project_id, database=db_name)
        else:
            self.db = AsyncFirestoreClient()

    async def save(self, transcript_id, transcript: str) -> str:
        if not transcript_id:
            transcript_id = str(uuid.uuid4())

        doc = self.db.collection(self.TRANSCRIPT_COLLECTION).document(transcript_id)
        await doc.set({u'transcript': transcript, u"updatedAt": datetime.datetime.utcnow().isoformat()})

        return transcript_id

    async def save_autoscribe_transcript_id(self, autoscribe_transcript_id, autoScribe_transcription_version, transcript_id) -> str:
        doc = self.db.collection(self.AUTOSCRIBE_TRANSCRIPT_COLLECTION).document(autoscribe_transcript_id)
        await doc.set({
                u'autoScribeTranscriptId': autoscribe_transcript_id, 
                u'transcriptId': transcript_id,
                u'autoScribeTranscriptionVersion': autoScribe_transcription_version
            })

        return transcript_id

    async def get_transcript_id_by_autoscribe_id(self, autoscribe_transcript_id) -> str:
        doc_ref = self.db.collection(self.AUTOSCRIBE_TRANSCRIPT_COLLECTION).document(autoscribe_transcript_id)
        doc = await doc_ref.get()
        if doc.exists:
            return doc.to_dict().get("transcriptId"), doc.to_dict().get("autoScribeTranscriptionVersion",0)
        return None,None
