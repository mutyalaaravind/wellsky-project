from typing import List

from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route, Mount
from starlette.routing import Match

import newrelic.agent

from paperglass.domain.string_utils import remove_prefix

from paperglass.log import getLogger
LOGGER = getLogger(__name__)

from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

#OpenTelemetry instrumentation
SPAN_BASE: str = "MIDDLEWARE:middleware_headers:"
from ..domain.utils.opentelemetry_utils import OpenTelemetryUtils
opentelemetry = OpenTelemetryUtils(SPAN_BASE)


class NewRelicMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        self.app = app
        super().__init__(app) 
       
        
    def get_route_name_from_routes(self, routes: List[Route], prefix, method, actual_path) -> str:
        """Get the matching route pattern for the current request path"""        
        best_route = None
        
        for route in routes:                        
            #LOGGER.debug("Checking route with prefix (%s): %s (%s)", prefix, route, type(route))
            if isinstance(route, Mount):                
                mount_prefix = prefix + route.path
                best_route = self.get_route_name_from_routes(route.routes, mount_prefix, method, actual_path)
            else:
                match_term = remove_prefix(actual_path, prefix)                
                match_params = route.matches({"type": "http", "method": method, "path": match_term})
                
                if match_params[0] == Match.FULL:                    
                    if hasattr(route, 'path_format'):
                        best_route = prefix + route.path_format
                    elif hasattr(route, 'path'):
                        best_route = prefix + route.path
                    break

        if best_route:
            LOGGER.debug("Best route: %s", best_route)
            return best_route
        else:
            LOGGER.debug("Could not find best route.  Using default route based on actual path: %s", actual_path)
            return actual_path

    async def dispatch(self, request: Request, call_next):
        # Custom processing before passing the request down the middleware stack

        with await opentelemetry.getSpan("newrelicmiddleware") as span:
            
            route_path = self.get_route_name_from_routes(request.app.routes, "", request.method, request.url.path)

            name = f"{request.method} {route_path}"
            group = "Function"
            #group = "Python/WebFramework/Controller"
            priority = None

            response = await call_next(request)
            response.headers["x-wsky-newrelic-name"] = f"{group} {name}"
            
            newrelic.agent.set_transaction_name(name, group=group, priority=priority)

            return response