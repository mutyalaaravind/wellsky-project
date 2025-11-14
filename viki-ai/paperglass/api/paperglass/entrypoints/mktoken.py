from base64 import b64encode
from json import dumps
from argparse import ArgumentParser


def mktoken(app_id, tenant_id, patient_id):
    return b64encode(dumps({'app_id': app_id, 'tenant_id': tenant_id, 'patient_id': patient_id}).encode()).decode()

def mktoken2(app_id, tenant_id, patient_id):
    return b64encode(dumps({'appId': app_id, 'tenantId': tenant_id, 'patientId': patient_id}).encode()).decode()


if __name__ == '__main__':
    parser = ArgumentParser(description='Create a token for the API')
    parser.add_argument('-a', '--app-id', help='App ID', required=True)
    parser.add_argument('-t', '--tenant-id', help='Tenant ID', required=True)
    parser.add_argument('-p', '--patient-id', help='Patient ID', required=True)

    args = parser.parse_args()
    result = mktoken(args.app_id, args.tenant_id, args.patient_id)
    print(result)
