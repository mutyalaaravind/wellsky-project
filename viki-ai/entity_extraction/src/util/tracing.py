"""
OpenTelemetry tracing utilities for entity extraction service.
"""

import os
import functools
from typing import Any, Callable, Dict, Optional, TypeVar, Union
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from util.custom_logger import getLogger

logger = getLogger(__name__)

# Type variable for decorated functions
F = TypeVar('F', bound=Callable[..., Any])

# Global tracer instance
_tracer: Optional[trace.Tracer] = None

def get_tracer() -> trace.Tracer:
    """Get the global tracer instance."""
    global _tracer
    if _tracer is None:
        _tracer = trace.get_tracer(__name__)
    return _tracer

def initialize_tracing(
    service_name: str = "entity-extraction",
    service_version: str = "1.0.0",
    enable_gcp_exporter: bool = True,
    enable_console_exporter: bool = False,
    enable_jaeger_exporter: bool = False,
    jaeger_endpoint: str = "http://jaeger:4318/v1/traces"
) -> None:
    """
    Initialize OpenTelemetry tracing with appropriate exporters.
    
    Args:
        service_name: Name of the service for tracing
        service_version: Version of the service
        enable_gcp_exporter: Whether to enable Google Cloud Trace exporter
        enable_console_exporter: Whether to enable console exporter (for debugging)
    """
    try:
        # Create resource with service information
        resource = Resource.create({
            ResourceAttributes.SERVICE_NAME: service_name,
            ResourceAttributes.SERVICE_VERSION: service_version,
            ResourceAttributes.SERVICE_INSTANCE_ID: os.environ.get("HOSTNAME", "unknown"),
        })
        
        # Create tracer provider
        tracer_provider = TracerProvider(resource=resource)
        
        # Set up exporters
        processors = []
        
        if enable_gcp_exporter:
            try:
                from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
                gcp_exporter = CloudTraceSpanExporter()
                processors.append(BatchSpanProcessor(gcp_exporter))
                logger.info("Google Cloud Trace exporter initialized")
            except ImportError:
                logger.warning("Google Cloud Trace exporter not available, install opentelemetry-exporter-gcp-trace")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Cloud Trace exporter: {e}")
        
        if enable_console_exporter:
            try:
                from opentelemetry.sdk.trace.export import ConsoleSpanExporter
                console_exporter = ConsoleSpanExporter()
                processors.append(BatchSpanProcessor(console_exporter))
                logger.info("Console span exporter initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize console exporter: {e}")
        
        if enable_jaeger_exporter:
            try:
                from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
                jaeger_exporter = OTLPSpanExporter(endpoint=jaeger_endpoint)
                processors.append(BatchSpanProcessor(jaeger_exporter))
                logger.info(f"Jaeger OTLP exporter initialized with endpoint: {jaeger_endpoint}")
            except ImportError:
                logger.warning("OTLP exporter not available, install opentelemetry-exporter-otlp")
            except Exception as e:
                logger.warning(f"Failed to initialize Jaeger exporter: {e}")
        
        # Add processors to tracer provider
        for processor in processors:
            tracer_provider.add_span_processor(processor)
        
        # Set the global tracer provider
        trace.set_tracer_provider(tracer_provider)
        
        logger.info(f"OpenTelemetry tracing initialized for service: {service_name}")
        
    except Exception as e:
        logger.error(f"Failed to initialize OpenTelemetry tracing: {e}")

def instrument_libraries() -> None:
    """Instrument common libraries for automatic tracing."""
    try:
        # Instrument FastAPI
        FastAPIInstrumentor().instrument()
        logger.info("FastAPI instrumentation enabled")
        
        # Instrument HTTPX
        HTTPXClientInstrumentor().instrument()
        logger.info("HTTPX instrumentation enabled")
        
        # Instrument Requests
        RequestsInstrumentor().instrument()
        logger.info("Requests instrumentation enabled")
        
    except Exception as e:
        logger.error(f"Failed to instrument libraries: {e}")

def trace_function(
    name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
    record_exception: bool = True
) -> Callable[[F], F]:
    """
    Decorator to trace function execution.
    
    Args:
        name: Custom span name (defaults to function name)
        attributes: Additional attributes to add to the span
        record_exception: Whether to record exceptions in the span
    
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            span_name = name or f"{func.__module__}.{func.__qualname__}"
            tracer = get_tracer()
            
            with tracer.start_as_current_span(span_name) as span:
                # Add custom attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                
                # Add function metadata
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                try:
                    result = await func(*args, **kwargs)
                    span.set_attribute("function.result.success", True)
                    return result
                except Exception as e:
                    span.set_attribute("function.result.success", False)
                    span.set_attribute("function.error.type", type(e).__name__)
                    span.set_attribute("function.error.message", str(e))
                    
                    if record_exception:
                        span.record_exception(e)
                    
                    raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            span_name = name or f"{func.__module__}.{func.__qualname__}"
            tracer = get_tracer()
            
            with tracer.start_as_current_span(span_name) as span:
                # Add custom attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                
                # Add function metadata
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("function.result.success", True)
                    return result
                except Exception as e:
                    span.set_attribute("function.result.success", False)
                    span.set_attribute("function.error.type", type(e).__name__)
                    span.set_attribute("function.error.message", str(e))
                    
                    if record_exception:
                        span.record_exception(e)
                    
                    raise
        
        # Return appropriate wrapper based on function type
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:  # CO_COROUTINE
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def trace_pipeline_step(
    step_name: str,
    pipeline_key: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None
) -> Callable[[F], F]:
    """
    Decorator specifically for tracing pipeline steps.
    
    Args:
        step_name: Name of the pipeline step
        pipeline_key: Pipeline identifier
        attributes: Additional attributes
    
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        step_attributes = {
            "pipeline.step.name": step_name,
            "pipeline.step.type": "processing"
        }
        
        if pipeline_key:
            step_attributes["pipeline.key"] = pipeline_key
        
        if attributes:
            step_attributes.update(attributes)
        
        return trace_function(
            name=f"pipeline.step.{step_name}",
            attributes=step_attributes
        )(func)
    
    return decorator

def add_span_attributes(attributes: Dict[str, Any]) -> None:
    """
    Add attributes to the current active span.
    
    Args:
        attributes: Dictionary of attributes to add
    """
    current_span = trace.get_current_span()
    if current_span and current_span.is_recording():
        for key, value in attributes.items():
            current_span.set_attribute(key, value)

def add_span_event(name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
    """
    Add an event to the current active span.
    
    Args:
        name: Event name
        attributes: Event attributes
    """
    current_span = trace.get_current_span()
    if current_span and current_span.is_recording():
        current_span.add_event(name, attributes or {})

def get_trace_id() -> Optional[str]:
    """
    Get the current trace ID as a string.
    
    Returns:
        Trace ID string or None if no active span
    """
    current_span = trace.get_current_span()
    if current_span and current_span.is_recording():
        trace_id = current_span.get_span_context().trace_id
        return f"{trace_id:032x}"
    return None

def get_span_id() -> Optional[str]:
    """
    Get the current span ID as a string.
    
    Returns:
        Span ID string or None if no active span
    """
    current_span = trace.get_current_span()
    if current_span and current_span.is_recording():
        span_id = current_span.get_span_context().span_id
        return f"{span_id:016x}"
    return None

def create_child_span(
    name: str,
    attributes: Optional[Dict[str, Any]] = None
) -> trace.Span:
    """
    Create a child span of the current active span.
    
    Args:
        name: Span name
        attributes: Span attributes
    
    Returns:
        New child span
    """
    tracer = get_tracer()
    span = tracer.start_span(name)
    
    if attributes:
        for key, value in attributes.items():
            span.set_attribute(key, value)
    
    return span

# Context manager for manual span creation
class traced_operation:
    """Context manager for creating traced operations."""
    
    def __init__(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        record_exception: bool = True
    ):
        self.name = name
        self.attributes = attributes or {}
        self.record_exception = record_exception
        self.span = None
    
    def __enter__(self):
        tracer = get_tracer()
        self.span = tracer.start_span(self.name)
        
        # Add attributes
        for key, value in self.attributes.items():
            self.span.set_attribute(key, value)
        
        return self.span
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.span:
            if exc_type is not None:
                self.span.set_attribute("operation.success", False)
                self.span.set_attribute("operation.error.type", exc_type.__name__)
                self.span.set_attribute("operation.error.message", str(exc_val))
                
                if self.record_exception:
                    self.span.record_exception(exc_val)
            else:
                self.span.set_attribute("operation.success", True)
            
            self.span.end()
