# -*- coding: utf-8 -*-

"""
IQRF CDC Codec
==============

This is a concrete implementation of IQRF CDC serialization.

:copyright: (c) 2016 by Tomáš Rottenberg.
:license:  Apache 2, see license.txt for more details.

"""

import re
import enum

from ..util.codec import (
    CodecError, Encoder, Decoder,
    Request, Reaction, Response
)
from ..util.common import CommonEqualityMixin
from ..util.log import logger

__all__ = [
    "CdcCodecError", "CdcEncodeError", "CdcDecodeError",

    "CdcRequest", "CdcResponse",

    "CdcStatus",

    "ErrorResponse",
    "TestRequest", "TestResponse",
    "ResetRequest", "ResetResponse",
    "TrResetRequest", "TrResetResponse",
    "InfoRequest", "InfoResponse",
    "TrInfoRequest", "TrInfoResponse",
    "IndicationRequest", "IndicationResponse",
    "SpiStatusRequest", "SpiStatusResponse",
    "DataSendRequest", "DataSendResponse",
    "DataReceivedReaction",
    "SwitchToCustomClassRequest", "SwitchToCustomClassResponse",
    "SwitchToUartRequest", "SwitchToUartResponse",
    "SwitchToSpiRequest", "SwitchToSpiResponse",

    "register_cdc_request", "register_cdc_response",
    "get_cdc_request_type", "get_cdc_request_id",
    "get_cdc_response_type", "get_cdc_response_id",
    "decode_cdc_message"
]


class CdcCodecError(CodecError):
    """An error indicating general CDC codec exception."""

    pass


class CdcEncodeError(CdcCodecError):
    """An error thrown when exception raises during CDC message encoding."""

    pass


class CdcDecodeError(CdcCodecError):
    """An error thrown when exception raises during CDC message decoding."""

    pass


class CdcStatus(enum.Enum):
    """Represents a status of a CDC response message."""

    OK = 0,
    BUSY = 1,
    ERROR = 2


class CdcRequest(Request, CommonEqualityMixin):
    """Abstract base for all CDC request messages."""

    pass


class CdcResponse(Response, CommonEqualityMixin):
    """Abstract base for all CDC response messages."""

    def __init__(self, status):
        self._status = status

    @property
    def status(self):
        """Returns the status of this response.

        :return: An instance of :class:`CdcStatus` representing the status of
            this response.
        :rtype: CdcStatus
        """

        return self._status


class CdcReaction(Reaction, CommonEqualityMixin):
    """Abstract base for all CDC reaction messages."""

    pass

REQUESTS = {}
RESPONSES = {}
REACTIONS = {}


def register_cdc_request(cls, id):
    if not issubclass(cls, CdcRequest):
        raise ValueError("Not a request type!")

    if cls in REQUESTS:
        raise ValueError("Duplicate request type!")

    REQUESTS[cls] = id
    logger.debug("Registering CDC request: (%s:%s).", cls, id)


def register_cdc_response(cls, id):
    if not issubclass(cls, CdcResponse):
        raise ValueError("Not a response type!")

    if cls in RESPONSES:
        raise ValueError("Duplicate response type!")

    RESPONSES[cls] = id
    logger.debug("Registering CDC response: (%s:%s).", cls, id)


def register_cdc_reaction(cls, id):
    if not issubclass(cls, CdcReaction):
        raise ValueError("Not a reaction type!")

    if cls in REACTIONS:
        raise ValueError("Duplicate reaction type!")

    REACTIONS[cls] = id
    logger.debug("Registering CDC reaction: (%s:%s).", cls, id)


def get_cdc_request_type(id):
    for request_type, request_id in REQUESTS.items():
        if id == request_id:
            return request_type

    return None


def get_cdc_request_id(type):
    for request_type, request_id in REQUESTS.items():
        if type == request_type:
            return request_id

    return None


def get_cdc_response_type(id):
    for response_type, response_id in RESPONSES.items():
        if id == response_id:
            return response_type

    return None


def get_cdc_response_id(type):
    for response_type, response_id in RESPONSES.items():
        if type == response_type:
            return response_id

    return None


def get_cdc_reaction_type(id):
    for reaction_type, reaction_id in REACTIONS.items():
        if id == reaction_id:
            return reaction_type

    return None


def get_cdc_reaction_id(type):
    for reaction_type, reaction_id in REACTIONS.items():
        if type == reaction_type:
            return reaction_id

    return None


class CdcToken(object):

    TERMINATOR = b"\r"
    REQUEST = b">"
    RESPONSE = b"<"
    PATTERN = re.compile(b"(" + REQUEST + b"|" + RESPONSE + b")([A-Z]{0,3})(.*?)" + TERMINATOR + b"$")
    SEPARATOR = b":"
    OK = b"OK"
    BUSY = b"BUSY"
    ERROR = b"ERR"


class CdcEncoder(Encoder):

    def tokenize(self):
        """Turns the object into smaller pieces called tokens which can be
        serialized to bytes. This method is called directly from the
        :func:`Encoder.encode` method and is meant to guarantee higher
        modularity."""

        raise NotImplementedError

    def encode(self):
        parameter, value = self.tokenize()
        message_type = type(self)

        if isinstance(self, CdcRequest):
            direction = CdcToken.REQUEST
            identifier = get_cdc_request_id(message_type)
        elif isinstance(self, CdcResponse):
            direction = CdcToken.RESPONSE
            identifier = get_cdc_response_id(message_type)
        elif isinstance(self, CdcReaction):
            direction = CdcToken.RESPONSE
            identifier = get_cdc_reaction_id(message_type)
        else:
            raise CdcEncodeError("Not a CDC message!")

        if direction is None or identifier is None:
            raise CdcEncodeError("Unknown CDC message type!")

        if value is None:
            encoded = b"".join([direction, identifier, CdcToken.TERMINATOR])
        else:
            if parameter is None:
                encoded = b"".join([direction, identifier, CdcToken.SEPARATOR,
                                    value, CdcToken.TERMINATOR])
            else:
                encoded = b"".join([direction, identifier, parameter,
                                    CdcToken.SEPARATOR, value,
                                    CdcToken.TERMINATOR])

        logger.debug("Encoded %s to: '%s'.", self, encoded)

        return encoded


class CdcDecoder(Decoder):
    pass


class NoneEncoder(CdcEncoder):

    def tokenize(self):
        return None, None


class NoneDecoder(CdcDecoder):

    @classmethod
    def decode(cls, parameter, value):
        if parameter is not None or value is not None:
            raise CdcDecodeError("Both parameter and value must be None!")

        return cls()


class StatusEncoder(CdcEncoder):

    def tokenize(self):
        if self.status == CdcStatus.OK:
            status = CdcToken.OK
        elif self.status == CdcStatus.BUSY:
            status = CdcToken.BUSY
        elif self.status == CdcStatus.ERROR:
            status = CdcToken.ERROR
        else:
            raise CdcEncodeError("Unknown status token!")

        return None, status


class StatusDecoder(CdcDecoder):

    @classmethod
    def decode(cls, parameter, value):
        if parameter is not None or value is None:
            raise CdcDecodeError

        if value == CdcToken.OK:
            status = CdcStatus.OK
        elif value == CdcToken.BUSY:
            status = CdcStatus.BUSY
        elif value == CdcToken.ERROR:
            status = CdcStatus.ERROR
        else:
            raise CdcDecodeError("Illegal status token!")

        return cls(status)


class InfoEncoder(CdcEncoder):

    def tokenize(self):
        return (None, self.type.encode() + b"#" + self.version.encode()
                + b"#" + self.id.encode())


class InfoDecoder(CdcDecoder):

    @classmethod
    def decode(cls, parameter, value):
        if parameter is not None or value is None:
            raise CdcDecodeError

        return cls(*[info.decode() for info in value.split(b"#")])


class TrInfoEncoder(CdcEncoder):

    def tokenize(self):
        return None, self.info


class TrInfoDecoder(CdcDecoder):

    @classmethod
    def decode(cls, parameter, value):
        if parameter is not None or value is None:
            raise CdcDecodeError

        return cls(value)


class SpiStatusEncoder(CdcEncoder):

    def tokenize(self):
        return None, self.spi_status


class SpiStatusDecoder(CdcDecoder):

    @classmethod
    def decode(cls, parameter, value):
        if parameter is not None or value is None:
            raise CdcDecodeError

        return cls(value)


class DataEncoder(CdcEncoder):

    def tokenize(self):
        return bytes([len(self.data)]), self.data


class DataDecoder(CdcDecoder):

    @classmethod
    def decode(cls, parameter, value):
        if parameter is None or value is None:
            raise CdcDecodeError

        return cls(value)


class ErrorResponse(NoneEncoder, NoneDecoder, CdcResponse):

    def __init__(self):
        super().__init__(CdcStatus.ERROR)


class TestRequest(NoneEncoder, NoneDecoder, CdcRequest):
    pass


class TestResponse(NoneEncoder, NoneDecoder, CdcResponse):

    def __init__(self):
        super().__init__(CdcStatus.OK)


class ResetRequest(NoneEncoder, NoneDecoder, CdcRequest):
    pass


class ResetResponse(StatusEncoder, StatusDecoder, CdcResponse):

    def __init__(self, status):
        super().__init__(status)


class TrResetRequest(NoneEncoder, NoneDecoder, CdcRequest):
    pass


class TrResetResponse(StatusEncoder, StatusDecoder, CdcResponse):

    def __init__(self, status):
        super().__init__(status)


class InfoRequest(NoneEncoder, NoneDecoder, CdcRequest):
    pass


class InfoResponse(InfoEncoder, InfoDecoder, CdcResponse):

    def __init__(self, type, version, id):
        super().__init__(CdcStatus.OK)
        self.type = type
        self.version = version
        self.id = id


class TrInfoRequest(NoneEncoder, NoneDecoder, CdcRequest):
    pass


class TrInfoResponse(TrInfoEncoder, TrInfoDecoder, CdcResponse):

    def __init__(self, info):
        super().__init__(CdcStatus.OK)
        self.info = info


class IndicationRequest(NoneEncoder, NoneDecoder, CdcRequest):
    pass


class IndicationResponse(StatusEncoder, StatusDecoder, CdcResponse):

    def __init__(self, status):
        super().__init__(status)


class SpiStatusRequest(NoneEncoder, NoneDecoder, CdcRequest):
    pass


class SpiStatusResponse(SpiStatusEncoder, SpiStatusDecoder, CdcResponse):

    def __init__(self, spi_status):
        super().__init__(CdcStatus.OK)
        self.spi_status = spi_status


class DataSendRequest(DataEncoder, DataDecoder, CdcRequest):

    def __init__(self, data):
        self.data = data


class DataSendResponse(StatusEncoder, StatusDecoder, CdcResponse):

    def __init__(self, status):
        super().__init__(status)


class DataReceivedReaction(DataEncoder, DataDecoder, CdcReaction):

    def __init__(self, data):
        self.data = data


class SwitchToCustomClassRequest(NoneEncoder, NoneDecoder, CdcRequest):
    pass


class SwitchToCustomClassResponse(StatusEncoder, StatusDecoder, CdcResponse):

    def __init__(self, status):
        super().__init__(status)


class SwitchToUartRequest(NoneEncoder, NoneDecoder, CdcRequest):
    pass


class SwitchToUartResponse(StatusEncoder, StatusDecoder, CdcResponse):

    def __init__(self, status):
        super().__init__(status)


class SwitchToSpiRequest(NoneEncoder, NoneDecoder, CdcRequest):
    pass


class SwitchToSpiResponse(StatusEncoder, StatusDecoder, CdcResponse):

    def __init__(self, status):
        super().__init__(status)

register_cdc_response(ErrorResponse, b"ERR")

register_cdc_request(TestRequest, b"")
register_cdc_response(TestResponse, b"OK")

register_cdc_request(ResetRequest, b"R")
register_cdc_response(ResetResponse, b"R")

register_cdc_request(TrResetRequest, b"RT")
register_cdc_response(TrResetResponse, b"RT")

register_cdc_request(InfoRequest, b"I")
register_cdc_response(InfoResponse, b"I")

register_cdc_request(TrInfoRequest, b"IT")
register_cdc_response(TrInfoResponse, b"IT")

register_cdc_request(IndicationRequest, b"B")
register_cdc_response(IndicationResponse, b"B")

register_cdc_request(SpiStatusRequest, b"S")
register_cdc_response(SpiStatusResponse, b"S")

register_cdc_request(DataSendRequest, b"DS")
register_cdc_response(DataSendResponse, b"DS")

register_cdc_reaction(DataReceivedReaction, b"DR")

register_cdc_request(SwitchToCustomClassRequest, b"U")
register_cdc_response(SwitchToCustomClassResponse, b"U")

register_cdc_request(SwitchToUartRequest, b"UU")
register_cdc_response(SwitchToUartResponse, b"UU")

register_cdc_request(SwitchToSpiRequest, b"US")
register_cdc_response(SwitchToSpiResponse, b"US")


def tokenize_cdc_message(data):
    match = CdcToken.PATTERN.match(data)

    if match is None:
        raise CdcDecodeError

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
        type = get_cdc_request_type(identifier)
    elif direction == CdcToken.RESPONSE:
        type = get_cdc_response_type(identifier)

        if type is None:
            type = get_cdc_reaction_type(identifier)
    else:
        raise CdcDecodeError("Unknown direction!")

    if type is None:
        raise CdcDecodeError("Unknown message!")

    decoded = type.decode(parameter, value)

    logger.debug("Decoded '%s' as: %s.", data, decoded)

    return decoded
