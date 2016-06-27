from ..channel import Channel

__all__ = ["create_endpoint"]

class UdpHandlerAdapter:

    def __init__(self, loop, channel_handler, inbound_handlers, outbound_handlers):
        self.loop = loop
        self.channel_handler = channel_handler
        self.inbound_handlers = inbound_handlers
        self.outbound_handlers = outbound_handlers

    def connection_made(self, transport):
        self.channel = Channel(
            self.loop,
            transport,
            self.channel_handler,
            self.inbound_handlers,
            self.outbound_handlers
        )

        self.channel.pipeline.handle_connect_event()

    def datagram_received(self, data, address):
        self.channel.pipeline.handle_receive_event(data)

    def error_received(self, exception):
        self.channel.pipeline.handle_raise_event(exception)

    def connection_lost(self, exception):
        self.channel.pipeline.handle_disconnect_event()

async def create_endpoint(loop, address, channel_handler, inbound_handlers, outbound_handlers):
    await loop.create_datagram_endpoint(
        lambda: UdpHandlerAdapter(loop, channel_handler, inbound_handlers, outbound_handlers),
        remote_addr=address
    )
