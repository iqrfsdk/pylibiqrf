import re

from . import codec
from . import base_codec
from ..log import logger

__all__ = [
    "ErrorResponse",
    "TestRequest", "TestResponse",
    "ResetRequest", "ResetResponse",
    "TrResetRequest", "TrResetResponse",
    "InfoRequest", "InfoResponse",
    "TrInfoRequest", "TrInfoResponse",
    "IndicationRequest", "IndicationResponse",
    "SpiStatusRequest", "SpiStatusResponse",
    "DataSendRequest", "DataSendResponse",
    "DataReceivedResponse",
    "SwitchToCustomClassRequest", "SwitchToCustomClassResponse",
    "SwitchToUartRequest", "SwitchToUartResponse",
    "SwitchToSpiRequest", "SwitchToSpiResponse",
    "decode_cdc_message"
]

class CdcToken:

    TERMINATOR = b"\r"
    REQUEST = b">"
    RESPONSE = b"<"
    PATTERN = re.compile(b"(" + REQUEST + b"|" + RESPONSE + b")([A-Z]{0,3})(.*?)" + TERMINATOR + b"$")
    SEPARATOR = b":"
    OK = b"OK"
    BUSY = b"BUSY"
    ERROR = b"ERR"

class BaseCdcEncoder(codec.CdcEncoder):

    def encode(self):
        parameter, value = self.tokenize()
        message_type = type(self)

        if isinstance(self, codec.CdcRequest):
            direction = CdcToken.REQUEST
            identifier = base_codec.get_cdc_request_id(message_type)
        elif isinstance(self, codec.CdcResponse):
            direction = CdcToken.RESPONSE
            identifier = base_codec.get_cdc_response_id(message_type)

        if value is None:
            encoded = b"".join([direction, identifier, CdcToken.TERMINATOR])
        else:
            if parameter is None:
                encoded = b"".join([direction, identifier, CdcToken.SEPARATOR, value, CdcToken.TERMINATOR])
            else:
                encoded = b"".join([direction, identifier, parameter, CdcToken.SEPARATOR, value, CdcToken.TERMINATOR])

        logger.debug("Encoded %s to: '%s'.", self, encoded)

        return encoded

class BaseCdcDecoder(codec.CdcDecoder):
    pass

class NoneEncoder(BaseCdcEncoder):

    def tokenize(self):
        return None, None

class NoneDecoder(BaseCdcDecoder):

    @classmethod
    def decode(cls, parameter, value):
        if parameter is not None or value is not None:
            raise codec.CdcMessageDecodeError

        return cls()

class StatusEncoder(BaseCdcEncoder):

    def tokenize(self):
        if self.status == codec.CdcStatus.OK:
            status = CdcToken.OK
        elif self.status == codec.CdcStatus.BUSY:
            status = CdcToken.BUSY
        elif self.status == codec.CdcStatus.ERROR:
            status = CdcToken.ERROR
        else:
            raise codec.CdcMessageEncodeError

        return None, status

class StatusDecoder(BaseCdcDecoder):

    @classmethod
    def decode(cls, parameter, value):
        if parameter is not None or value is None:
            raise codec.CdcMessageDecodeError

        if value == CdcToken.OK:
            status = codec.CdcStatus.OK
        elif value == CdcToken.BUSY:
            status = codec.CdcStatus.BUSY
        elif value == CdcToken.ERROR:
            status = codec.CdcStatus.ERROR
        else:
            raise codec.CdcMessageDecodeError

        return cls(status)

class InfoEncoder(BaseCdcEncoder):

    def tokenize(self):
        return None, self.type.encode() + b"#" + self.version.encode() + b"#" + self.id.encode()

class InfoDecoder(BaseCdcDecoder):

    @classmethod
    def decode(cls, parameter, value):
        if parameter is not None or value is None:
            raise codec.CdcMessageDecodeError

        return cls(*[info.decode() for info in value.split(b"#")])

class TrInfoEncoder(BaseCdcEncoder):

    def tokenize(self):
        return None, self.info

class TrInfoDecoder(BaseCdcDecoder):

    @classmethod
    def decode(cls, parameter, value):
        if parameter is not None or value is None:
            raise codec.CdcMessageDecodeError

        return cls(value)

class SpiStatusEncoder(BaseCdcEncoder):

    def tokenize(self):
        return None, self.spi_status

class SpiStatusDecoder(BaseCdcDecoder):

    @classmethod
    def decode(cls, parameter, value):
        if parameter is not None or value is None:
            raise codec.CdcMessageDecodeError

        return cls(value)

class DataEncoder(BaseCdcEncoder):

    def tokenize(self):
        return bytes([len(self.data)]), self.data

class DataDecoder(BaseCdcDecoder):

    @classmethod
    def decode(cls, parameter, value):
        if parameter is None or value is None:
            raise codec.CdcMessageDecodeError

        return cls(value)

class ErrorResponse(NoneEncoder, NoneDecoder, base_codec.BaseCdcResponse):

    def __init__(self):
        super().__init__(codec.CdcStatus.ERROR)

class TestRequest(NoneEncoder, NoneDecoder, base_codec.BaseCdcRequest):
    pass

class TestResponse(NoneEncoder, NoneDecoder, base_codec.BaseCdcResponse):

    def __init__(self):
        super().__init__(codec.CdcStatus.OK)

class ResetRequest(NoneEncoder, NoneDecoder, base_codec.BaseCdcRequest):
    pass

class ResetResponse(StatusEncoder, StatusDecoder, base_codec.BaseCdcResponse):

    def __init__(self, status):
        super().__init__(status)

class TrResetRequest(NoneEncoder, NoneDecoder, base_codec.BaseCdcRequest):
    pass

class TrResetResponse(StatusEncoder, StatusDecoder, base_codec.BaseCdcResponse):

    def __init__(self, status):
        super().__init__(status)

class InfoRequest(NoneEncoder, NoneDecoder, base_codec.BaseCdcRequest):
    pass

class InfoResponse(InfoEncoder, InfoDecoder, base_codec.BaseCdcResponse):

    def __init__(self, type, version, id):
        super().__init__(codec.CdcStatus.OK)
        self.type = type
        self.version = version
        self.id = id

class TrInfoRequest(NoneEncoder, NoneDecoder, base_codec.BaseCdcRequest):
    pass

class TrInfoResponse(TrInfoEncoder, TrInfoDecoder, base_codec.BaseCdcResponse):

    def __init__(self, info):
        super().__init__(codec.CdcStatus.OK)
        self.info = info

class IndicationRequest(NoneEncoder, NoneDecoder, base_codec.BaseCdcRequest):
    pass

class IndicationResponse(StatusEncoder, StatusDecoder, base_codec.BaseCdcResponse):

    def __init__(self, status):
        super().__init__(status)

class SpiStatusRequest(NoneEncoder, NoneDecoder, base_codec.BaseCdcRequest):
    pass

class SpiStatusResponse(SpiStatusEncoder, SpiStatusDecoder, base_codec.BaseCdcResponse):

    def __init__(self, spi_status):
        super().__init__(codec.CdcStatus.OK)
        self.spi_status = spi_status

class DataSendRequest(DataEncoder, DataDecoder, base_codec.BaseCdcRequest):

    def __init__(self, data):
        self.data = data

class DataSendResponse(StatusEncoder, StatusDecoder, base_codec.BaseCdcResponse):

    def __init__(self, status):
        super().__init__(status)

class DataReceivedResponse(DataEncoder, DataDecoder, base_codec.BaseCdcResponse):

    ASYNC = True

    def __init__(self, data):
        super().__init__(codec.CdcStatus.OK)
        self.data = data

class SwitchToCustomClassRequest(NoneEncoder, NoneDecoder, base_codec.BaseCdcRequest):
    pass

class SwitchToCustomClassResponse(StatusEncoder, StatusDecoder, base_codec.BaseCdcResponse):

    def __init__(self, status):
        super().__init__(status)

class SwitchToUartRequest(NoneEncoder, NoneDecoder, base_codec.BaseCdcRequest):
    pass

class SwitchToUartResponse(StatusEncoder, StatusDecoder, base_codec.BaseCdcResponse):

    def __init__(self, status):
        super().__init__(status)

class SwitchToSpiRequest(NoneEncoder, NoneDecoder, base_codec.BaseCdcRequest):
    pass

class SwitchToSpiResponse(StatusEncoder, StatusDecoder, base_codec.BaseCdcResponse):

    def __init__(self, status):
        super().__init__(status)

base_codec.register_cdc_response(ErrorResponse, b"ERR")

base_codec.register_cdc_request(TestRequest, b"")
base_codec.register_cdc_response(TestResponse, b"OK")

base_codec.register_cdc_request(ResetRequest, b"R")
base_codec.register_cdc_response(ResetResponse, b"R")

base_codec.register_cdc_request(TrResetRequest, b"RT")
base_codec.register_cdc_response(TrResetResponse, b"RT")

base_codec.register_cdc_request(InfoRequest, b"I")
base_codec.register_cdc_response(InfoResponse, b"I")

base_codec.register_cdc_request(TrInfoRequest, b"IT")
base_codec.register_cdc_response(TrInfoResponse, b"IT")

base_codec.register_cdc_request(IndicationRequest, b"B")
base_codec.register_cdc_response(IndicationResponse, b"B")

base_codec.register_cdc_request(SpiStatusRequest, b"S")
base_codec.register_cdc_response(SpiStatusResponse, b"S")

base_codec.register_cdc_request(DataSendRequest, b"DS")
base_codec.register_cdc_response(DataSendResponse, b"DS")

base_codec.register_cdc_response(DataReceivedResponse, b"DR")

base_codec.register_cdc_request(SwitchToCustomClassRequest, b"U")
base_codec.register_cdc_response(SwitchToCustomClassResponse, b"U")

base_codec.register_cdc_request(SwitchToUartRequest, b"UU")
base_codec.register_cdc_response(SwitchToUartResponse, b"UU")

base_codec.register_cdc_request(SwitchToSpiRequest, b"US")
base_codec.register_cdc_response(SwitchToSpiResponse, b"US")

def tokenize_cdc_message(data):
    match = CdcToken.PATTERN.match(data)

    if match is None:
        raise codec.CdcMessageCodecError

    direction = match.group(1)
    identifier = match.group(2)
    data = match.group(3)

    if len(data) == 0:
        parameter = None
        value = None
    else:
        index = data.find(CdcToken.SEPARATOR)

        if index == 0:
            parameter = None
        else:
            parameter = data[:index]

        value = data[index + 1:]

    return direction, identifier, parameter, value

def decode_cdc_message(data):
    direction, identifier, parameter, value = tokenize_cdc_message(data)

    if direction == CdcToken.REQUEST:
        type = base_codec.get_cdc_request_type(identifier)
    elif direction == CdcToken.RESPONSE:
        type = base_codec.get_cdc_response_type(identifier)
    else:
        raise codec.CdcMessageDecodeError("Unknown direction!")

    if type is None:
        raise codec.CdcMessageDecodeError("Unknown message!")

    decoded = type.decode(parameter, value)

    logger.debug("Decoded '%s' as: %s.", data, decoded)

    return decoded
