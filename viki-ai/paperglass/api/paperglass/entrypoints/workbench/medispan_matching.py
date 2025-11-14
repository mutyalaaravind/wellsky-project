import asyncio
import sys, os
import json
from collections import OrderedDict
from kink import inject
from datetime import datetime
from typing import List

from google.cloud import firestore, storage  # type: ignore
from gcloud.aio.storage import Blob, Storage
import google.auth
from google.auth.transport import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from paperglass.settings import (
    GCP_FIRESTORE_DB,
    MEDICATION_MATCHING_BATCH_SIZE
)
from paperglass.domain.util_json import DateTimeEncoder, convertToJson
from paperglass.domain.utils.array_utils import chunk_array
from paperglass.domain.time import now_utc

from paperglass.domain.models import (
    Document,
    MedispanDrug,
    DocumentOperationInstanceLog
)

from paperglass.usecases.commands import (
    GetDocumentLogs
)

from paperglass.interface.ports import (
    ICommandHandlingPort
)

from paperglass.infrastructure.ports import (
    IPromptAdapter,
    IQueryPort,
    IRelevancyFilterPort,
)


from paperglass.domain.utils.opentelemetry_utils import bootstrap_opentelemetry
bootstrap_opentelemetry(__name__)

import logging
from paperglass.log import getLogger
LOGGER = getLogger(__name__)

LOGGER.setLevel(logging.DEBUG)
logging.getLogger('google.auth._default').setLevel(logging.INFO)
logging.getLogger('aiocache.serializers.serializers').setLevel(logging.INFO)
logging.getLogger('aiocache.serializers').setLevel(logging.INFO)
logging.getLogger('aiocache').setLevel(logging.INFO)
logging.getLogger('asyncio').setLevel(logging.INFO)
logging.getLogger('grpc._cython.cygrpc').setLevel(logging.INFO)
logging.getLogger('google.auth.transport.requests').setLevel(logging.INFO)
logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)

logging.getLogger('paperglass.infrastructure.adapters.prompt').setLevel(logging.INFO)
logging.getLogger('paperglass.domain.util_json').setLevel(logging.INFO)

firestore_client = firestore.AsyncClient(database=GCP_FIRESTORE_DB)

meds = [
    {
        "medispan_options": json.loads("[\n  {\n    \"id\": \"1874\",\n    \"NameDescription\": \"Ascorbic Acid Oral Tablet 1000 MG\",\n    \"GenericName\": \"Ascorbic Acid\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"1000\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet\"\n  },\n  {\n    \"id\": \"1877\",\n    \"NameDescription\": \"Ascorbic Acid Oral Tablet 500 MG\",\n    \"GenericName\": \"Ascorbic Acid\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"500\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet\"\n  },\n  {\n    \"id\": \"23638\",\n    \"NameDescription\": \"Vitamin C Oral Tablet 250 MG\",\n    \"GenericName\": \"Ascorbic Acid\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"250\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet\"\n  },\n  {\n    \"id\": \"23625\",\n    \"NameDescription\": \"Vitamin C Oral Tablet Chewable 250 MG\",\n    \"GenericName\": \"Ascorbic Acid\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"250\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet Chewable\"\n  },\n  {\n    \"id\": \"3723\",\n    \"NameDescription\": \"Calcium Ascorbate Oral Tablet 500 MG\",\n    \"GenericName\": \"Calcium Ascorbate\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"500\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet\"\n  },\n  {\n    \"id\": \"35192\",\n    \"NameDescription\": \"Vitamin C/Bioflavonoids Oral Tablet 1000-25 MG\",\n    \"GenericName\": \"Bioflavonoid Products\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"1000-25\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet\"\n  },\n  {\n    \"id\": \"23639\",\n    \"NameDescription\": \"Vitamin C Oral Tablet 500 MG\",\n    \"GenericName\": \"Ascorbic Acid\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"500\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet\"\n  },\n  {\n    \"id\": \"39074\",\n    \"NameDescription\": \"SM Vitamin C Oral Tablet 250 MG\",\n    \"GenericName\": \"Ascorbic Acid\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"250\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet\"\n  },\n  {\n    \"id\": \"64160\",\n    \"NameDescription\": \"Ascorbic Acid Oral Powder\",\n    \"GenericName\": \"Ascorbic Acid\",\n    \"Route\": \"Oral\",\n    \"Strength\": null,\n    \"StrengthUnitOfMeasure\": null,\n    \"Dosage_Form\": \"Powder\"\n  },\n  {\n    \"id\": \"80073\",\n    \"NameDescription\": \"CVS Vitamin C Oral Tablet 250 MG\",\n    \"GenericName\": \"Ascorbic Acid\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"250\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet\"\n  }\n]"),
        "medication": "Ascorbic Acid 250 MG 1 tablet Tablet by mouth"
    },
    {
        "medispan_options": json.loads("[\n  {\n    \"id\": \"5553\",\n    \"NameDescription\": \"Cyanocobalamin Injection Solution 1000 MCG/ML\",\n    \"GenericName\": \"Cyanocobalamin\",\n    \"Route\": \"Injection\",\n    \"Strength\": \"1000\",\n    \"StrengthUnitOfMeasure\": \"MCG/ML\",\n    \"Dosage_Form\": \"Solution\"\n  },\n  {\n    \"id\": \"44358\",\n    \"NameDescription\": \"Cyanocobalamin  Powder\",\n    \"GenericName\": \"Cyanocobalamin (Bulk)\",\n    \"Route\": \"Does not apply\",\n    \"Strength\": null,\n    \"StrengthUnitOfMeasure\": null,\n    \"Dosage_Form\": \"Powder\"\n  },\n  {\n    \"id\": \"39259\",\n    \"NameDescription\": \"Cyanocobalamin  Crystals\",\n    \"GenericName\": \"Cyanocobalamin (Bulk)\",\n    \"Route\": \"Does not apply\",\n    \"Strength\": null,\n    \"StrengthUnitOfMeasure\": null,\n    \"Dosage_Form\": \"Crystals\"\n  },\n  {\n    \"id\": \"205437\",\n    \"NameDescription\": \"Cyanocobalamin Injection Solution 2000 MCG/ML\",\n    \"GenericName\": \"Cyanocobalamin\",\n    \"Route\": \"Injection\",\n    \"Strength\": \"2000\",\n    \"StrengthUnitOfMeasure\": \"MCG/ML\",\n    \"Dosage_Form\": \"Solution\"\n  },\n  {\n    \"id\": \"92441\",\n    \"NameDescription\": \"Cyanocobalamin Nasal Solution 500 MCG/0.1ML\",\n    \"GenericName\": \"Cyanocobalamin\",\n    \"Route\": \"Nasal\",\n    \"Strength\": \"500\",\n    \"StrengthUnitOfMeasure\": \"MCG/0.1ML\",\n    \"Dosage_Form\": \"Solution\"\n  },\n  {\n    \"id\": \"173015\",\n    \"NameDescription\": \"Methylcobalamin Oral Tablet Disintegrating 5000 MCG\",\n    \"GenericName\": \"Methylcobalamin\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"5000\",\n    \"StrengthUnitOfMeasure\": \"MCG\",\n    \"Dosage_Form\": \"Tablet Disintegrating\"\n  },\n  {\n    \"id\": \"204230\",\n    \"NameDescription\": \"B-12 Methylcobalamin Oral Tablet Disintegrating 1000 MCG\",\n    \"GenericName\": \"Methylcobalamin\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"1000\",\n    \"StrengthUnitOfMeasure\": \"MCG\",\n    \"Dosage_Form\": \"Tablet Disintegrating\"\n  },\n  {\n    \"id\": \"78046\",\n    \"NameDescription\": \"Vitamin B12 Oral Tablet 100 MCG\",\n    \"GenericName\": \"Cyanocobalamin\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"100\",\n    \"StrengthUnitOfMeasure\": \"MCG\",\n    \"Dosage_Form\": \"Tablet\"\n  },\n  {\n    \"id\": \"23579\",\n    \"NameDescription\": \"Vitamin B-12 Oral Tablet 1000 MCG\",\n    \"GenericName\": \"Cyanocobalamin\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"1000\",\n    \"StrengthUnitOfMeasure\": \"MCG\",\n    \"Dosage_Form\": \"Tablet\"\n  },\n  {\n    \"id\": \"102492\",\n    \"NameDescription\": \"Vitamin B12 Oral Tablet 500 MCG\",\n    \"GenericName\": \"Cyanocobalamin\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"500\",\n    \"StrengthUnitOfMeasure\": \"MCG\",\n    \"Dosage_Form\": \"Tablet\"\n  }\n]"),
        "medication": "Cyanocobalamin 1000 MCG 1 tablet Tablet by mouth"
    },
    {
        "medispan_options": json.loads("[\n  {\n    \"id\": \"8349\",\n    \"NameDescription\": \"Ferrous Sulfate Oral Tablet 325 (65 Fe) MG\",\n    \"GenericName\": \"Ferrous Sulfate\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"325 (65 Fe)\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet\"\n  },\n  {\n    \"id\": \"8353\",\n    \"NameDescription\": \"Ferrous Sulfate Oral Tablet Delayed Release 325 (65 Fe) MG\",\n    \"GenericName\": \"Ferrous Sulfate\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"325 (65 Fe)\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet Delayed Release\"\n  },\n  {\n    \"id\": \"211549\",\n    \"NameDescription\": \"Iron (Ferrous Sulfate) Oral Tablet 325 (65 Fe) MG\",\n    \"GenericName\": \"Ferrous Sulfate\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"325 (65 Fe)\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet\"\n  },\n  {\n    \"id\": \"203865\",\n    \"NameDescription\": \"FeroSul Oral Tablet 325 (65 Fe) MG\",\n    \"GenericName\": \"Ferrous Sulfate\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"325 (65 Fe)\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet\"\n  },\n  {\n    \"id\": \"166221\",\n    \"NameDescription\": \"Ferrous Sulfate Oral Tablet Delayed Release 324 (65 Fe) MG\",\n    \"GenericName\": \"Ferrous Sulfate\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"324 (65 Fe)\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet Delayed Release\"\n  },\n  {\n    \"id\": \"10902\",\n    \"NameDescription\": \"Iron Oral Tablet 325 (65 Fe) MG\",\n    \"GenericName\": \"Ferrous Sulfate\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"325 (65 Fe)\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet\"\n  },\n  {\n    \"id\": \"168121\",\n    \"NameDescription\": \"KP Ferrous Sulfate Oral Tablet 325 (65 Fe) MG\",\n    \"GenericName\": \"Ferrous Sulfate\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"325 (65 Fe)\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet\"\n  },\n  {\n    \"id\": \"57287\",\n    \"NameDescription\": \"Meijer Ferrous Sulfate Oral Tablet 325 (65 Fe) MG\",\n    \"GenericName\": \"Ferrous Sulfate\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"325 (65 Fe)\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet\"\n  },\n  {\n    \"id\": \"68838\",\n    \"NameDescription\": \"Ferrous Sulfate Oral Tablet Delayed Release 324 MG\",\n    \"GenericName\": \"Ferrous Sulfate\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"324\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet Delayed Release\"\n  },\n  {\n    \"id\": \"136084\",\n    \"NameDescription\": \"QC Ferrous Sulfate Oral Tablet 325 (65 Fe) MG\",\n    \"GenericName\": \"Ferrous Sulfate\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"325 (65 Fe)\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet\"\n  }\n]"),
        "medication": "Ferrous Sulfate 325 (65 Fe) MG 1 tablet Tablet by mouth"
    },
    {
        "medispan_options": json.loads("[\n  {\n    \"id\": \"8865\",\n    \"NameDescription\": \"Furosemide Oral Tablet 40 MG\",\n    \"GenericName\": \"Furosemide\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"40\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet\"\n  },\n  {\n    \"id\": \"8866\",\n    \"NameDescription\": \"Furosemide Oral Tablet 80 MG\",\n    \"GenericName\": \"Furosemide\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"80\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet\"\n  },\n  {\n    \"id\": \"8864\",\n    \"NameDescription\": \"Furosemide Oral Tablet 20 MG\",\n    \"GenericName\": \"Furosemide\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"20\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet\"\n  },\n  {\n    \"id\": \"44186\",\n    \"NameDescription\": \"Furosemide  Powder\",\n    \"GenericName\": \"Furosemide\",\n    \"Route\": \"Does not apply\",\n    \"Strength\": null,\n    \"StrengthUnitOfMeasure\": null,\n    \"Dosage_Form\": \"Powder\"\n  },\n  {\n    \"id\": \"11844\",\n    \"NameDescription\": \"Lasix Oral Tablet 40 MG\",\n    \"GenericName\": \"Furosemide\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"40\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet\"\n  },\n  {\n    \"id\": \"8862\",\n    \"NameDescription\": \"Furosemide Oral Solution 10 MG/ML\",\n    \"GenericName\": \"Furosemide\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"10\",\n    \"StrengthUnitOfMeasure\": \"MG/ML\",\n    \"Dosage_Form\": \"Solution\"\n  },\n  {\n    \"id\": \"8863\",\n    \"NameDescription\": \"Furosemide Oral Solution 8 MG/ML\",\n    \"GenericName\": \"Furosemide\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"8\",\n    \"StrengthUnitOfMeasure\": \"MG/ML\",\n    \"Dosage_Form\": \"Solution\"\n  },\n  {\n    \"id\": \"11845\",\n    \"NameDescription\": \"Lasix Oral Tablet 80 MG\",\n    \"GenericName\": \"Furosemide\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"80\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet\"\n  },\n  {\n    \"id\": \"23856\",\n    \"NameDescription\": \"Water Pill Oral Tablet\",\n    \"GenericName\": \"Misc Natural Products\",\n    \"Route\": \"Oral\",\n    \"Strength\": null,\n    \"StrengthUnitOfMeasure\": null,\n    \"Dosage_Form\": \"Tablet\"\n  },\n  {\n    \"id\": \"58910\",\n    \"NameDescription\": \"Urosex Oral Tablet\",\n    \"GenericName\": \"Specialty Vitamins Products\",\n    \"Route\": \"Oral\",\n    \"Strength\": null,\n    \"StrengthUnitOfMeasure\": null,\n    \"Dosage_Form\": \"Tablet\"\n  }\n]"),
        "medication": "Furosemide 40 MG 1 tablet Tablet by mouth"
    },
    {
        "medispan_options": json.loads("[\n  {\n    \"id\": \"10338\",\n    \"NameDescription\": \"hydrOXYzine HCl Oral Tablet 25 MG\",\n    \"GenericName\": \"Hydroxyzine HCl\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"25\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet\"\n  },\n  {\n    \"id\": \"10342\",\n    \"NameDescription\": \"hydrOXYzine Pamoate Oral Capsule 25 MG\",\n    \"GenericName\": \"Hydroxyzine Pamoate\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"25\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Capsule\"\n  },\n  {\n    \"id\": \"10339\",\n    \"NameDescription\": \"hydrOXYzine HCl Oral Tablet 50 MG\",\n    \"GenericName\": \"Hydroxyzine HCl\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"50\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet\"\n  },\n  {\n    \"id\": \"10336\",\n    \"NameDescription\": \"hydrOXYzine HCl Oral Tablet 10 MG\",\n    \"GenericName\": \"Hydroxyzine HCl\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"10\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Tablet\"\n  },\n  {\n    \"id\": \"10343\",\n    \"NameDescription\": \"hydrOXYzine Pamoate Oral Capsule 50 MG\",\n    \"GenericName\": \"Hydroxyzine Pamoate\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"50\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Capsule\"\n  },\n  {\n    \"id\": \"10341\",\n    \"NameDescription\": \"hydrOXYzine Pamoate Oral Capsule 100 MG\",\n    \"GenericName\": \"Hydroxyzine Pamoate\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"100\",\n    \"StrengthUnitOfMeasure\": \"MG\",\n    \"Dosage_Form\": \"Capsule\"\n  },\n  {\n    \"id\": \"10335\",\n    \"NameDescription\": \"hydrOXYzine HCl Oral Syrup 10 MG/5ML\",\n    \"GenericName\": \"Hydroxyzine HCl\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"10\",\n    \"StrengthUnitOfMeasure\": \"MG/5ML\",\n    \"Dosage_Form\": \"Syrup\"\n  },\n  {\n    \"id\": \"55396\",\n    \"NameDescription\": \"hydrOXYzine HCl  Powder\",\n    \"GenericName\": \"Hydroxyzine HCl (Bulk)\",\n    \"Route\": \"Does not apply\",\n    \"Strength\": null,\n    \"StrengthUnitOfMeasure\": null,\n    \"Dosage_Form\": \"Powder\"\n  },\n  {\n    \"id\": \"10333\",\n    \"NameDescription\": \"hydrOXYzine HCl Intramuscular Solution 25 MG/ML\",\n    \"GenericName\": \"Hydroxyzine HCl\",\n    \"Route\": \"Intramuscular\",\n    \"Strength\": \"25\",\n    \"StrengthUnitOfMeasure\": \"MG/ML\",\n    \"Dosage_Form\": \"Solution\"\n  },\n  {\n    \"id\": \"44196\",\n    \"NameDescription\": \"hydrOXYzine Pamoate  Powder\",\n    \"GenericName\": \"Hydroxyzine Pamoate\",\n    \"Route\": \"Does not apply\",\n    \"Strength\": null,\n    \"StrengthUnitOfMeasure\": null,\n    \"Dosage_Form\": \"Powder\"\n  }\n]"),
        "medication": "hydrOXYzine HCI 25 MG 25 mg Tablet by mouth"
    },
    {
        "medispan_options": json.loads("[\n  {\n    \"id\": \"153566\",\n    \"NameDescription\": \"Lactulose Oral Solution 20 GM/30ML\",\n    \"GenericName\": \"Lactulose\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"20\",\n    \"StrengthUnitOfMeasure\": \"GM/30ML\",\n    \"Dosage_Form\": \"Solution\"\n  },\n  {\n    \"id\": \"86719\",\n    \"NameDescription\": \"Lactulose Oral Solution 10 GM/15ML\",\n    \"GenericName\": \"Lactulose\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"10\",\n    \"StrengthUnitOfMeasure\": \"GM/15ML\",\n    \"Dosage_Form\": \"Solution\"\n  },\n  {\n    \"id\": \"227703\",\n    \"NameDescription\": \"Lactulose Encephalopathy Oral Solution 20 GM/30ML\",\n    \"GenericName\": \"Lactulose (Encephalopathy)\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"20\",\n    \"StrengthUnitOfMeasure\": \"GM/30ML\",\n    \"Dosage_Form\": \"Solution\"\n  },\n  {\n    \"id\": \"46487\",\n    \"NameDescription\": \"Lactulose Oral Packet 10 GM\",\n    \"GenericName\": \"Lactulose\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"10\",\n    \"StrengthUnitOfMeasure\": \"GM\",\n    \"Dosage_Form\": \"Packet\"\n  },\n  {\n    \"id\": \"87165\",\n    \"NameDescription\": \"Lactulose Encephalopathy Oral Solution 10 GM/15ML\",\n    \"GenericName\": \"Lactulose (Encephalopathy)\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"10\",\n    \"StrengthUnitOfMeasure\": \"GM/15ML\",\n    \"Dosage_Form\": \"Solution\"\n  },\n  {\n    \"id\": \"89964\",\n    \"NameDescription\": \"Constulose Oral Solution 10 GM/15ML\",\n    \"GenericName\": \"Lactulose\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"10\",\n    \"StrengthUnitOfMeasure\": \"GM/15ML\",\n    \"Dosage_Form\": \"Solution\"\n  },\n  {\n    \"id\": \"89962\",\n    \"NameDescription\": \"Enulose Oral Solution 10 GM/15ML\",\n    \"GenericName\": \"Lactulose (Encephalopathy)\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"10\",\n    \"StrengthUnitOfMeasure\": \"GM/15ML\",\n    \"Dosage_Form\": \"Solution\"\n  },\n  {\n    \"id\": \"170911\",\n    \"NameDescription\": \"Diarrhea Oral Suspension 262 MG/15ML\",\n    \"GenericName\": \"Bismuth Subsalicylate\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"262\",\n    \"StrengthUnitOfMeasure\": \"MG/15ML\",\n    \"Dosage_Form\": \"Suspension\"\n  },\n  {\n    \"id\": \"88214\",\n    \"NameDescription\": \"GlycoLax Oral Powder 17 GM/SCOOP\",\n    \"GenericName\": \"Polyethylene Glycol 3350\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"17\",\n    \"StrengthUnitOfMeasure\": \"GM/SCOOP\",\n    \"Dosage_Form\": \"Powder\"\n  },\n  {\n    \"id\": \"224508\",\n    \"NameDescription\": \"Anti-Diarrheal Oral Solution 1 MG/7.5ML\",\n    \"GenericName\": \"Loperamide HCl\",\n    \"Route\": \"Oral\",\n    \"Strength\": \"1\",\n    \"StrengthUnitOfMeasure\": \"MG/7.5ML\",\n    \"Dosage_Form\": \"Solution\"\n  }\n]"),
        "medication": "Lactulose 20 GM/30ML 15 ml Solution by mouth"
    }
]

MODEL = "gemini-1.5-flash-002"
PROMPT_OLD = """
For the GIVEN MEDICATION, can you find the best med match from the MATCH LIST given below. Please follow these instructions:
1) The name of medication should be present in the \"content\" field of the MATCH LIST entries. Otherwise say no name match
2) If the GIVEN MEDICATION has medication strength specified, select from the list only if there is exact match of the Strength
3) If the GIVEN MEDICATION has medication form specified, select from the list only if there is exact match of the Dosage_Form
4) If the GIVEN MEDICATION has medication route specified, select from the list only if there is exact match of the Route
5) Otherwise, return "{}" and specific what attributes were not found 

Only return the best match from the list. If no match is found, return "{}"
Only return the best match from the list. If no match is found, return "{}"

GIVEN MEDICATION:
{SEARCH_TERM}

MATCH LIST:
{DATA}
"""

PROMPT = """
For each GIVEN MEDICATIONS, can you find the best medication match from the MATCH LIST given below? Please follow these instructions:
1) The name of the GIVEN MEDICATION should be match the \"NameDescription\" field of the MATCH LIST entries. Otherwise no name match
2) Prefer the match if the MATCH LIST entry's \"NameDescription\" begins with the first word of the GIVEN MEDICATION name
3) Prefer the match if the name of the GIVEN MEDICATION exactly matches (case insensitive) the name of the MATCH LIST \"NameDescription\" entry.  
4) Lower the consideration for the match if the name of the GIVEN MEDICATION only matches the \"GenericName\" field and does not match the \"NameDescription\" field of the MATCH LIST entry.
5) If the GIVEN MEDICATION has medication strength specified, select from the list only if there is exact match of the Strength
6) If the GIVEN MEDICATION has medication form specified, select from the list only if there is exact match of the Dosage_Form
7) If the GIVEN MEDICATION has medication route specified, select from the list only if there is exact match of the Route

The list of GIVEN MEDICATIONS is a dictionary with the key being the index and the value being the name of the medication.

For each medication, only return the best match from the list. 

Return the response in the following json format:

[
    {"**MEDICATION_ID": "**MATCHLIST id"}
]

GIVEN MEDICATIONS:
{SEARCH_TERM}

MATCH LIST:
{DATA}
"""

def split_tuple_object(t):
    t0 = list(t.keys())[0]
    t1 = list(t.values())[0]
    return t0, t1

@inject
async def list_extracted_meds(document_id, commands: ICommandHandlingPort, query: IQueryPort):
    
    doc: Document = await query.get_document(document_id)
    document = Document(**doc)

    command = GetDocumentLogs(app_id=document.app_id, tenant_id=document.tenant_id, patient_id=document.patient_id, document_id=document_id)
    log_map = await commands.handle_command(command)

    logs = log_map["MEDICATION_EXTRACTION"]

    medmatch_log = None

    for log in logs:
        #LOGGER.debug("Log: %s", log)
        if log.step_id == "MEDISPAN_MATCHING" and "medispan_log_details" in log.context:
            medmatch_log = log
            break
    
    #LOGGER.debug("Medmatch Log: %s", medmatch_log)
    ms_details = medmatch_log.context["medispan_log_details"]

    output = []
    idx = 0
    for detail in ms_details:
        medication_name = detail["medispan_search_term"]
        medispan_options = json.loads(detail["medispan_results"])
        
        output.append({
                "index": idx,
                "medication": medication_name,
                "medispan_options": medispan_options
            }
        )
        idx += 1
    
    if medmatch_log is None:
        LOGGER.error("No Medispan Matching log found for document_id: %s", document_id)
    else:
        LOGGER.debug("Medispan Matching Log found")

    expected_results = await getStepResults(medmatch_log)


    return output, expected_results

async def getStepResults(log):
    expectations = log.context["step_results"]
    return expectations

@inject
async def test_new_matching(document_id, prompt: IPromptAdapter):
    prompt_input, expected_results = await list_extracted_meds(document_id)

    results = await medispan_matching(prompt_input)

    #LOGGER.debug("Options: %s", json.dumps(prompt_input[0]["medispan_options"], indent=2))

    if results:
        LOGGER.warning("== Testing Results for %s ====================================================================================", document_id)
        for result in results:
            await assertResults(result, expected_results)

        LOGGER.debug("Results: %s", json.dumps(results, indent=2))
    else:
        LOGGER.debug("No results found")

async def assertResults(result, expected_results):
    medispan_matches = []
    for item in expected_results:        
        medispan_matches.append(item["medispan_id"])

    if result["medispan_id"] in medispan_matches:
        LOGGER.debug("Medication '%s' matched to MedispanId: %s - %s", result["medication_name"], result["medispan_id"], result["medispan_name"])
    else:
        LOGGER.error("Result is different: %s", json.dumps(result))

async def medispan_matching(prompt_input, batch_size=MEDICATION_MATCHING_BATCH_SIZE):    
    batches = chunk_array(prompt_input, batch_size)

    output = []
    for batch in batches:
        results = await medispanmatching_batch(batch)        
        output.extend(results)
    return output

@inject
async def medispanmatching_batch(prompt_input, prompt: IPromptAdapter):
    LOGGER.debug("Testing Medispan Matching")

    start_time = datetime.now()    

    med_db = {}
    medispan_db = {}

    idx = 0
    for med in prompt_input:
        #Cyanocobalamin 1000 MCG 1 tablet Tablet by mouth
        index = med["index"]
        med_db[str(index)] = med["medication"]
        idx += 1

        medispan_options = med["medispan_options"]
        for medispan in medispan_options:
            medispan_db[medispan["id"]] = medispan            

    #LOGGER.debug("Med DB: %s", med_db)
    medispan_list = list(medispan_db.values())

    #LOGGER.debug("Medispan DB: %s", json.dumps(medispan_list, indent=2))

    this_prompt = PROMPT.replace("{SEARCH_TERM}", json.dumps(med_db, indent=2))
    this_prompt = this_prompt.replace("{DATA}", json.dumps(medispan_list, indent=2))

    #LOGGER.debug("Prompt: %s", this_prompt)
    LOGGER.debug("Prompt size: %s", len(this_prompt))

    LOGGER.warning("== Executing prompt ====================================================================================")
    results = await prompt.multi_modal_predict_2([this_prompt], model=MODEL)
    LOGGER.warning("== Execution complete ==================================================================================")
    results = convertToJson(results)

    result_db = {}
    for result in results:
        idx, medispanid = split_tuple_object(result)
        result_db[idx] = medispanid

    #LOGGER.debug("ResultDB: %s", json.dumps(result_db, indent=2))

    output = []
    for item in med_db.keys():
        index = int(item)

        medication_name = med_db[item]

        LOGGER.debug("Item: %s medication_name: %s", item, medication_name)

        medispan_id = None
        if item in result_db:
            LOGGER.debug("Found medispanid for index: %s", index)
            medispan_id = result_db[item]
        else:
            LOGGER.debug("No medispanid found for index: %s", index)
        
        output.append({
                "index": index,
                "medication_name": medication_name,
                "medispan_id": medispan_id,
                "medispan_name": medispan_db[medispan_id]["NameDescription"] if medispan_id else None
            }
        )


    end_time = datetime.now()
    elapsed_time = end_time - start_time    
    LOGGER.debug("End time: %s", end_time)
    LOGGER.debug("Elapsed Time: %s", elapsed_time.total_seconds())

    return output

    # for med in meds:
    #     medication = med["medication"]
    #     medispan_options = med["medispan_options"]
    #     this_prompt = PROMPT.replace("{SEARCH_TERM}", medication).replace("{DATA}", json.dumps(medispan_options, indent=2))

    #     LOGGER.debug("Prompt: %s", this_prompt)

    #     results = await prompt.multi_modal_predict_2([this_prompt], model=MODEL)

    #     LOGGER.debug("Results: %s", results)



async def run():
    LOGGER.info("Running test")
    #document_id = "f5af6786a3f011ef82b842004e494300"  # DEV  11 meds
    #document_id = "70ad7538a88611efbd2442004e494300"  # DEV lined up.pdf
    document_id = "2a36fceca79f11efb32c42004e494300" # STAGE Load Test document
    results = await test_new_matching(document_id)
    #results = await test_medispanmatching()
    

def main():    
    asyncio.run(run())

if __name__ == "__main__":   
    main()






