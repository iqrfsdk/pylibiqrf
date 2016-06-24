class Next:

    def __init__(self, handlers, actual=0, warning="Warning: No more handlers in the pipeline!"):
        self.handlers = handlers
        self.actual = actual
        self.warning = warning

    def next(self, channel, object):
        if len(self.handlers) <= self.actual:
            print(self.warning)
        else:
            handler = self.handlers[self.actual]
            self.actual += 1
            handler(channel, object, self.next)
