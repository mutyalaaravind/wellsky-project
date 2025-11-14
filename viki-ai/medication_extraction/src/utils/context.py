import contextvars
import asyncio
import uuid

from ..settings import (
    STAGE
)

class Context:

    user = contextvars.ContextVar('user', default=None)
    baseAggregate = contextvars.ContextVar('baseAggregate', default=None)   
    trace = contextvars.ContextVar('trace', default=None)
    opentelemetry = contextvars.ContextVar('opentelementry', default=None)
    traceId = contextvars.ContextVar('traceId', default=None)
    tracer = contextvars.ContextVar('tracer', default=None)    

    def __init__(self):
        tid = str(uuid.uuid4())
        self.traceId.set(tid)
        pass

    async def getUser(self):
        return self.user.get()

    async def getUsername(self):
        return self.sync_getUsername()
        
    def sync_getUsername(self):
        if self.user is None:        
            return "unknown"
        elif self.user.get() is None:
            return "unknown"
        else:
            return self.user.get()["username"]

   
    async def setUser(self, user):
        self.user.set(user)

    def getBaseAggregate(self):
        return self.baseAggregate.get()
    
    async def setBaseAggregate(self, baseAggregate):
        self.baseAggregate.set(baseAggregate)

    def setBaseAggregate_sync(self, baseAggregate):
        self.baseAggregate.set(baseAggregate)

    def getLoggingContext(self):
        traceId = self.traceId.get()
        username = self.sync_getUsername()
        baseAggregate = self.getBaseAggregate() if self.baseAggregate is not None else {}

        loggingContext = {}
        if baseAggregate:
            loggingContext = baseAggregate.copy()
            loggingContext["traceId"] = traceId
            loggingContext["username"] = username

        loggingContext["env"] = STAGE
        
        return loggingContext


    async def getTrace(self):
        return self.trace.get()


    async def setTrace(self, trace):
        self.trace.set(trace)


    async def getTraceId(self):
        return self.async_getTraceId()


    def sync_getTraceId(self):
        if self.traceId is not None and self.traceId.get() is not None:            
            return self.traceId.get()
        else:
            return None


    async def setOpenTelemetry(self, opentelemetry_traceparent: str, openetelemetry_tracestate: str, opentelemetry_baggage: str):
        o = {
            "parenttrace": opentelemetry_traceparent,
            "tracestate": openetelemetry_tracestate,
            "baggage": opentelemetry_baggage
        }
        self.opentelemetry.set(o)
    

    async def getOpenTelemetry(self):
        return self.opentelemetry.get()
    

    def getTracer(self):
        return self.tracer.get()
    
    def setTracer(self, tracer):
        self.tracer.set(tracer)

    def extractCommand(self, command):        
        context_keys = [
            "app_id",
            "tenant_id",
            "patient_id",
            "user_id",
            "document_id",
            "document_operation_definition_id",
            "document_operation_instance_id",
            "page_number",
        ]
        
        if not command:
            return {}            
        
        o = command.dict()
        
        context_obj = {}
        for key in context_keys:
            if key in o:
                context_obj[key] = o[key]   

        self.setBaseAggregate_sync(context_obj)
        return o
