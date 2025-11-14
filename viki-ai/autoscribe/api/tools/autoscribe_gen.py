#!/usr/bin/env python3

import csv
import re
from collections import defaultdict
import json
from google.cloud.firestore import Client
from datetime import datetime

# Step 0: convert mp3 to ogg. comand: ffmpeg -i audio.mp3 audio.ogg
# Step 1: copy .ogg recording to GCS
# (replace "/c70ee241-126a-719b-4b53-c48e5ae3716e" with actual ID)
# gsutil cp audio.ogg gs://viki-ai-provisional-dev/autoscribe/audio/c70ee241-126a-719b-4b53-c48e5ae3716e/default/audio.ogg

# Step 2: edit vars below and run this script
# FIRESTORE_EMULATOR_HOST=127.0.0.1:8080 pipenv run python autoscribe_gen.py

FNAME = "./visitone.csv"
ID = "c70ee241-126a-719b-4b53-c48e5ae3716f"

# speaker_tags = defaultdict(lambda: len(speaker_tags))
speaker_tags = {
    "patient": 2,
    "provider": 1,
    "caregiver": 1,
}

sentences = []
text_sentences = []

with open(FNAME, "r") as f:
    reader = csv.reader(f)
    next(reader)
    for start, end, lang, confidence, channel, speaker_tag, transcript in reader:
        start = float(start)
        end = float(end)
        transcript = transcript.strip()
        transcript = transcript.replace("\n", " ")
        transcript = re.sub(r"\s([\.,\?\!])", r"\1", transcript)
        if not speaker_tag:
            continue
        speaker_tag = speaker_tags[speaker_tag]
        sentences.append(
            {
                "speaker_tag": speaker_tag,
                "words": [{"start": start, "end": end, "text": transcript}],
            }
        )
        text_sentences.append(
            {
                "is_final": True,
                "speaker_tag": speaker_tag,
                "start": start,
                "text": transcript,
            }
        )

# print(json.dumps(sentences, indent=4))
# print(json.dumps(text_sentences, indent=4))

client = Client(project="viki-dev-app-wsky")
doc_ref = client.collection("autoscribe_transactions").document(ID)
# print(doc_ref.get().exists)
doc_ref.set(
    {
        "created": datetime.now(),
        "id": ID,
        "last_updated_section": "default",
        "sections": {
            "default": {
                "backend": "google_v1",
                "is_finalized": True,
                "sentences": sentences,
                "text_sentences": text_sentences,
                "version": 1,
            },
        },
    },
)