"""
Main HTTP multiplexer.
"""
from ..settings import (
    CLOUD_PROVIDER, 
    NEW_RELIC_TRACE_ENABLED,
    NEW_RELIC_TRACE_OTLP_ENDPOINT,
    NEW_RELIC_LICENSE_KEY,
    GCP_TRACE_ENABLED,
)

from textwrap import dedent

# from autoscribe.interface.adapters.ws import WebSocketAdapter
from ..interface.adapters.rest import RestAdapter
from ..settings import DEBUG, STAGE, VERSION
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse
from starlette.routing import Mount, Route
from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.starlette import StarletteInstrumentor

import newrelic.agent

# Initialize OpenTelemetry
trace.set_tracer_provider(TracerProvider())


if CLOUD_PROVIDER == "google":

    if GCP_TRACE_ENABLED:
        print("Enabling Google Cloud Trace")
        from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
        cloud_trace_exporter = CloudTraceSpanExporter()
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(cloud_trace_exporter)
        )

    if NEW_RELIC_TRACE_ENABLED and NEW_RELIC_LICENSE_KEY:
        print("Enabling New Relic Trace")
        otlp_exporter = OTLPSpanExporter(
            endpoint=NEW_RELIC_TRACE_OTLP_ENDPOINT,
            headers=(("api-key", NEW_RELIC_LICENSE_KEY),),
        )
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)

elif CLOUD_PROVIDER=="local":
    from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
    cloud_trace_exporter = CloudTraceSpanExporter()
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(cloud_trace_exporter)
    )
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter())
    )
else:
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter())
    )

# Get a tracer
tracer = trace.get_tracer(__name__)

from ..domain.context import Context
Context().setTracer(tracer)

from paperglass.log import getLogger, labels
LOGGER = getLogger(__name__)

from .middleware_headers import HeadersMiddleware
from .middleware_newrelic import NewRelicMiddleware


async def index(request):
    return PlainTextResponse(
        dedent(
            fr'''
            PaperGlass

            Does the PDF magic.

            Version: {VERSION}
            Stage: {STAGE}
            '''
        ).strip('\n')
    )


app = Starlette(
    debug=DEBUG,
    on_startup=[],
    on_shutdown=[],
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_methods=("GET", "POST", "PATCH", "OPTIONS", "DELETE"),
            allow_headers=[
                'access-control-allow-origin',
                'authorization',
                'content-type',
                'x-api-key',
                'graphql-submit-form',
                'httponly',
                'secure',
                'strict-transport-security',
                'x-content-type-options',
                'x-frame-options',
                'sentry-trace',
                'okta-token',
                'ehr-token'
            ],
        ),
        Middleware(HeadersMiddleware),
        Middleware(NewRelicMiddleware),
    ],
    routes=[
        Route('/', index),
        Mount('/api', RestAdapter()),
        # Mount('/ws', WebSocketAdapter(OKTA_DISABLE, OKTA_ISSUER, OKTA_AUDIENCE, OKTA_SCOPE)),
    ],
)

StarletteInstrumentor.instrument_app(app)

# `request` is an instance of urllib3.connectionpool.HTTPConnectionPool
def request_hook(span, instance, headers, body):
    pass
    
# `response` is an instance of urllib3.response.HTTPResponse
def response_hook(span, request, response):
    pass    

URLLib3Instrumentor().instrument(
    request_hook=request_hook, response_hook=response_hook
)

if CLOUD_PROVIDER != "local":
    LOGGER.info("Initializing New Relic with environment: %s", STAGE)
    newrelic.agent.initialize(config_file="./newrelic.ini", environment=STAGE)

@app.on_event("startup")
async def startup_event():
    LOGGER.info("Starting up PaperGlass API?  Yes!")