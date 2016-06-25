import asyncio

from .utility import Next

__all__ = [
    "ErrorHandler", "InboundHandler", "OutboundHandler",
    "Pipeline", "Channel"
]

class ErrorHandler:

    def raised(self, channel, exception):
        raise NotImplementedError()

class InboundHandler:

    def received(self, channel, data, next):
        raise NotImplementedError()

class OutboundHandler:

    def sent(self, channel, message, next):
        raise NotImplementedError()

class Pipeline:

    def __init__(self, channel, error_handler, inbound_handlers, outbound_handlers):
        self.channel = channel
        self.error_handler = error_handler
        self.inbound_handlers = inbound_handlers
        self.outbound_handlers = outbound_handlers

    def handle_raise_event(self, exception):
        self.error_handler.raised(channel, exception)

    def handle_receive_event(self, data):
        Next(self.inbound_handlers).next(self.channel, data)

    def handle_send_event(self, message):
        Next(self.outbound_handlers).next(self.channel, message)

class Channel:

    def __init__(self, url, error_handler, inbound_handlers, outbound_handlers, options={}):
        self.url = url
        self.pipeline = Pipeline(self, error_handler, inbound_handlers, outbound_handlers)
        self.options = options

    async def connect(self):
        pass

    async def send(self, message):
        pass

    async def disconnect(self):
        pass

async def connect(url, error_handler, inbound_handlers, outbound_handlers, options={}):
    pass
