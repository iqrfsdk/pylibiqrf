import asyncio

from .utility import Next

__all__ = [
    "ChannelHandler", "InboundHandler", "OutboundHandler",
    "Pipeline", "Channel"
]

class ChannelHandler:

    def connected(self, channel):
        raise NotImplementedError()

    def raised(self, channel, exception):
        raise NotImplementedError()

    def disconnected(self, channel):
        raise NotImplementedError()

class InboundHandler:

    def received(self, channel, data, next):
        raise NotImplementedError()

class OutboundHandler:

    def sent(self, channel, message, next):
        raise NotImplementedError()

class Pipeline:

    def __init__(self, channel, channel_handler, inbound_handlers, outbound_handlers):
        self.channel = channel
        self.channel_handler = channel_handler
        self.inbound_handlers = inbound_handlers
        self.outbound_handlers = outbound_handlers

    def handle_connect_event(self, channel):
        self.channel_handler.connected(self.channel)

    def handle_raise_event(self, exception):
        self.channel_handler.raised(self.channel, exception)

    def handle_disconnect_event(self, channel):
        self.channel_handler.disconnected(self.channel)

    def handle_receive_event(self, data):
        Next(self.inbound_handlers).next(self.channel, data)

    def handle_send_event(self, message):
        Next(self.outbound_handlers).next(self.channel, message)

class Channel:

    def __init__(self, channel_handler, inbound_handlers, outbound_handlers):
        self.pipeline = Pipeline(self, channel_handler, inbound_handlers, outbound_handlers)

    def send(self, message):
        pass

    def disconnect(self):
        pass

async def connect(loop, url, channel_handler, inbound_handlers, outbound_handlers, options={}):
    pass
