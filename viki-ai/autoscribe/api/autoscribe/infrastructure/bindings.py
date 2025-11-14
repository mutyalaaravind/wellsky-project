from kink import di

from autoscribe.infrastructure.adapters.factories import SpeechRecognitionFactory
from autoscribe.infrastructure.adapters.firestore import FirestoreAdapter
from autoscribe.infrastructure.adapters.google_speech import GoogleSpeechAdapter
from autoscribe.infrastructure.adapters.google_speech_v2 import GoogleSpeechV2Adapter
from autoscribe.infrastructure.ports import IPersistencePort, ISpeechRecognitionFactory, ISpeechRecognitionPort
from autoscribe.settings import GCS_BUCKET_NAME, GCP_PROJECT_ID, GOOGLE_SPEECH_API_VERSION


di[IPersistencePort] = lambda _: FirestoreAdapter()
di[ISpeechRecognitionFactory] = lambda _: SpeechRecognitionFactory()
