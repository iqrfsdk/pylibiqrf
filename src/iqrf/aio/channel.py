class Next:

    def __init__(self, handlers, action, actual=0, warning="Warning: No more handlers in the pipeline!"):
        self.handlers = handlers
        self.action = action
        self.actual = actual
        self.warning = warning

    def next(self, channel, object):
        if len(self.handlers) <= self.actual:
            print(self.warning)
        else:
            handler = self.handlers[self.actual]
            self.actual += 1
            getattr(handler, self.action)(channel, object, self.next)

class Pipeline:

    def __init__(self, channel, channel_handler, inbound_handlers, outbound_handlers):
        self.channel = channel
        self.channel_handler = channel_handler
        self.inbound_handlers = inbound_handlers
        self.outbound_handlers = outbound_handlers

    def handle_connect_event(self):
        self.channel_handler.connected(self.channel)

    def handle_raise_event(self, exception):
        self.channel_handler.raised(self.channel, exception)

    def handle_disconnect_event(self):
        self.channel_handler.disconnected(self.channel)

    def handle_receive_event(self, data):
        Next(self.inbound_handlers, "received").next(self.channel, data)

    def handle_send_event(self, message):
        Next(self.outbound_handlers, "sent").next(self.channel, message)

class Channel:

    def __init__(self, loop, transport, channel_handler, inbound_handlers, outbound_handlers):
        self.loop = loop
        self.transport = transport
        self.pipeline = Pipeline(self, channel_handler, inbound_handlers, outbound_handlers)

    def send(self, message):
        self.pipeline.handle_send_event(message)

    def disconnect(self):
        self.transport.close()
