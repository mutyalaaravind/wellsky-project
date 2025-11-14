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

from paperglass.entrypoints.middleware_newrelic import NewRelicMiddleware

from paperglass.log import getLogger, labels
LOGGER = getLogger(__name__)

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

from ..interface.adapters.rest import RestAdapter
from ..settings import DEBUG, STAGE, VERSION
from ..interface.adapters.eventarc import EventarcAdapter


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
            allow_methods=("GET", "POST", "OPTIONS"),
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
            ],
        ),
        Middleware(NewRelicMiddleware),
    ],
    routes=[
        Route('/', index),
        Mount('/eventarc', EventarcAdapter()),
        
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
    LOGGER.info("Initializing New Relic with environment: %s", {STAGE})
    newrelic.agent.initialize(config_file="./newrelic.ini", environment=STAGE)