from kink import inject
from autoscribe.infrastructure.adapters.google_speech import GoogleSpeechAdapter
from autoscribe.infrastructure.adapters.google_speech_v2 import GoogleSpeechV2Adapter
from autoscribe.infrastructure.adapters.transcribe import AWSTranscribeAdapter
from autoscribe.infrastructure.ports import ISpeechRecognitionFactory
from autoscribe.settings import AWS_DEFAULT_REGION, AWS_ROLE_ARN, CLOUD_PROVIDER, GCP_PROJECT_ID, GCS_BUCKET_NAME


class SpeechRecognitionFactory(ISpeechRecognitionFactory):
    @inject
    def get_implementation(
        self,
        backend: ISpeechRecognitionFactory.Backend,
    ):
        if backend == ISpeechRecognitionFactory.Backend.GOOGLE_V1:
            return GoogleSpeechAdapter(GCP_PROJECT_ID, GCS_BUCKET_NAME, CLOUD_PROVIDER)
        elif backend == ISpeechRecognitionFactory.Backend.GOOGLE_V2:
            return GoogleSpeechV2Adapter(GCP_PROJECT_ID)
        elif backend == ISpeechRecognitionFactory.Backend.AWS_TRANSCRIBE:
            return AWSTranscribeAdapter(AWS_ROLE_ARN, AWS_DEFAULT_REGION)

        raise NameError(f'No implementation for {backend}')
