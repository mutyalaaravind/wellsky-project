import logging

import coloredlogs

from main.settings import DEBUG

logging.basicConfig(level=logging.INFO)
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s %(name)s[%(process)d] [%(levelname)s] %(message)s',
    # https://stackoverflow.com/questions/37703609/using-python-logging-with-aws-lambda
    # Let's kindly ask AWS (and other systems that want to poke their nose everywhere) to go fuck themselves:
    force=True,
)

coloredlogs.install(level='DEBUG' if DEBUG else 'INFO')

# Make some modules less verbose
for name in ('urllib3', 'google', 'chromadb', 'grpc', 'clickhouse_connect', 'shapely', 'gcloud'):
    logging.getLogger(name).setLevel(logging.ERROR)

getLogger = logging.getLogger
