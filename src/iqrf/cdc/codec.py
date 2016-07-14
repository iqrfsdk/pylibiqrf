import enum

__all__ = [
    "CdcMessageCodecError", "CdcMessageEncodeError", "CdcMessageDecodeError",
    "CdcEncoder", "CdcDecoder",
    "CdcStatus",
    "CdcMessage", "CdcRequest", "CdcResponse"
]

class CdcMessageCodecError(Exception):
    pass

class CdcMessageEncodeError(CdcMessageCodecError):
    pass

class CdcMessageDecodeError(CdcMessageCodecError):
    pass

class CdcEncoder:

    def tokenize(self):
        raise NotImplementedError

    def encode(self):
        raise NotImplementedError

class CdcDecoder:

    @classmethod
    def decode(cls, parameter, value):
        raise NotImplementedError

class CdcStatus(enum.Enum):
    OK = 0,
    BUSY = 1,
    ERROR = 2

class CdcMessage:

    @classmethod
    def decode(cls, parameter, value):
        raise NotImplementedError

    def encode(self):
        raise NotImplementedError

class CdcRequest(CdcMessage):
    pass

class CdcResponse(CdcMessage):

    @classmethod
    def is_async(cls):
        raise NotImplementedError

    @property
    def status(self):
        raise NotImplementedError
