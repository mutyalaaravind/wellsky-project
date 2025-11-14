import time

from ..settings import DEBUG, STAGE, VERSION, GCP_PROJECT_ID, OTEL_SDK_DISABLED

from ..log import getLogger
LOGGER = getLogger(__name__)

from paperglass.domain.context import Context

import newrelic.agent

from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

#OpenTelemetry instrumentation
SPAN_BASE: str = "MIDDLEWARE:middleware_headers:"
from ..domain.utils.opentelemetry_utils import OpenTelemetryUtils
opentelemetry = OpenTelemetryUtils(SPAN_BASE)

class HeadersMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Custom processing before passing the request down the middleware stack
        #LOGGER.debug("HeaderMiddleware: Before request")

        with await opentelemetry.getSpan("headermiddleware") as span:   

            stime = time.time()    

            async def custom_send_response(message):                    
                if message['type'] == 'http.response.start':
                    #LOGGER.debug("Adding custom headers")
                    # Example: Add a custom header
                    headers = [
                        (b'x-wsky-build', str(VERSION)),
                        (b'x-wsky-env', str(STAGE)),
                        (b'x-wsky-debug', str(DEBUG)),
                        (b'x-wsky-project-id', str(GCP_PROJECT_ID)),
                        (b'x-wsky-trace-id', str(Context().traceId.get()))
                    ]

                    etime = time.time()
                    elapsed_time=(etime - stime) * 1000
                    headers.append((b'x-wsky-performance-elapsed-ms', str(round(elapsed_time,1))))

                    span.set_attribute("wsky-build", str(VERSION))
                    span.set_attribute("wsky-env", str(STAGE))
                    span.set_attribute("wsky-debug", str(DEBUG))
                    span.set_attribute("wsky-project-id", str(GCP_PROJECT_ID))

                    if not OTEL_SDK_DISABLED:
                        # Inject traceparent into header
                        carrier = {}
                        
                        # Write the current context into the carrier.
                        TraceContextTextMapPropagator().inject(carrier)    
                        headers.append((b'x-wsky-traceparent', carrier["traceparent"]))                    
                    
                    # Ensure existing headers are preserved and add the new ones                
                    message['headers'].extend(headers)
                await send(message)

            # Pass the request to the next middleware or endpoint
            await self.app(scope, receive, custom_send_response)

            # Custom processing after the request has been handled
            #LOGGER.debug("HeaderMiddleware: After request")