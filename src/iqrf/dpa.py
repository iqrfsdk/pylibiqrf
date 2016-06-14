class DpaMessage:

    # TODO: Add methods for checking messages, calculating checksums, etc.

    def __init__(self, data):
        self.data = data

    def __str__(self):
        return "DpaMessage({})".format(self.data)

    def encode(self):
        return bytes(self.data)

    @classmethod
    def decode(cls, data):
        return cls(list(data))
