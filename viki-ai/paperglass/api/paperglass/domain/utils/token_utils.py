from base64 import b64encode
from json import dumps
from argparse import ArgumentParser

def mktoken(app_id, tenant_id, patient_id):
    return b64encode(dumps({'app_id': app_id, 'tenant_id': tenant_id, 'patient_id': patient_id}).encode()).decode()

def mktoken2(app_id, tenant_id, patient_id):
    return b64encode(dumps({'appId': app_id, 'tenantId': tenant_id, 'patientId': patient_id}).encode()).decode()