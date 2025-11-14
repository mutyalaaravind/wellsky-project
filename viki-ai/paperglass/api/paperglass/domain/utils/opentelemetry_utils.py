import functools

from opentelemetry import trace, baggage
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.starlette import StarletteInstrumentor
from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor

from ...settings import CLOUD_PROVIDER
from ..context import Context

def bootstrap_opentelemetry(name: str):
    # Initialize OpenTelemetry
    trace.set_tracer_provider(TracerProvider())

    if CLOUD_PROVIDER == "google":
        from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
        cloud_trace_exporter = CloudTraceSpanExporter()
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(cloud_trace_exporter)
        )
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
    tracer = trace.get_tracer(name)
    Context().setTracer(tracer)
    

class OpenTelemetryUtils:

    baseClass:str = "default:"

    def __init__(self, baseClass:str):
        self.baseClass = baseClass
        
    async def getSpan(self, spanName: str):
        tracer = Context().getTracer()

        spanContextManager = tracer.start_as_current_span(self.baseClass + spanName)        
            
        return spanContextManager

    async def autoSetAttributes(self, span):

        traceid = await Context().getTraceId()

        span.set_attribute("trace-id", traceid)        

        for k, v in (await Context().getOpenTelemetry()).items():
            if v is not None:
                span.set_attribute(k, v)


def span(span_name=None):
    def decorator_span(func):
        @functools.wraps(func)
        async def wrapper_span(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            name = span_name if span_name else func.__name__
            with tracer.start_as_current_span(name) as span:
                return await func(*args, **kwargs)
        return wrapper_span

    if callable(span_name):
        # The decorator was used without arguments
        func = span_name
        span_name = None
        return decorator_span(func)

    return decorator_span