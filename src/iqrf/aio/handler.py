__all__ = [
    "ChannelHandler",
    "InboundHandler",
    "OutboundHandler"
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
