import enum

from ..util.codec import CodecError, Request, Reaction, Response
from ..util.common import CommonEqualityMixin

__all__ = [
    "SpiCodecError", "SpiEncodeError", "SpiDecodeError",

    "SpiStatus",

    "SpiRequest", "SpiResponse", "SpiReaction",

    "TrInfoRequest", "TrInfoResponse",
    "DataSendRequest", "DataSendResponse",
    "DataReceivedReaction"
]


class SpiCodecError(CodecError):
    pass


class SpiEncodeError(SpiCodecError):
    pass


class SpiDecodeError(SpiCodecError):
    pass


class SpiStatus(enum.Enum):

    READY = 0,
    BUSY = 1,
    INACTIVE = 2


class SpiRequest(Request, CommonEqualityMixin):
    pass


class SpiResponse(Response, CommonEqualityMixin):
    pass


class SpiReaction(Reaction, CommonEqualityMixin):
    pass


class SpiToken(object):

    COMMAND_CHECK = 0x00
    COMMAND_READ_WRITE = 0xf0
    COMMAND_TR_INFO = 0xf5

    STATUS_INACTIVE = 0x00
    STATUS_SUSPENDED = 0x07
    STATUS_CRC_OK = 0x3f
    STATUS_CRC_ERROR = 0x3e
    STATUS_COMMUNICATION_MODE = 0x80
    STATUS_PROGRAMMING_MODE = 0x81
    STATUS_DEBUG_MODE = 0x82
    STATUS_HW_ERROR = 0xff

    DATA_READY_MIN = 0x40
    DATA_READY_MAX = 0x7f


def calculate_crc(data, offset, length):
    crc = 0x5f
    for i in range(offset, length):
        crc ^= data[i]

    return crc


def encode_command_type(direction, length):
    return (direction << 0x07 & 0x80) | length


def decode_command_type(byte):
    return (byte & 0x80) >> 0x07, byte & 0x7f


def generate_clock_data(length):
    return [0x00 for i in range(length)]

# class StatusRequest(SpiRequest):
#
#     def encode(self):
#         return bytes([SpiToken.COMMAND_CHECK])
#
# class StatusResponse(SpiResponse):
#
#     def __init__(self, status, status_code):
#         self.status = status
#         self.status_code = status_code
#
#     @classmethod
#     def decode(cls, data):
#         status_code = ord(data)
#
#         if status_code == SpiToken.STATUS_INACTIVE:
#             return cls(SpiStatus.INACTIVE, status_code)
#
#         if status_code == SpiToken.STATUS_SUSPENDED:
#             return cls(SpiStatus.INACTIVE, status_code)
#
#         if status_code == SpiToken.STATUS_CRC_OK:
#             return cls(SpiStatus.READY, status_code)
#
#         if status_code == SpiToken.STATUS_CRC_ERROR:
#             return cls(SpiStatus.READY, status_code)
#
#         if status_code == SpiToken.STATUS_COMMUNICATION_MODE:
#             return cls(SpiStatus.READY, status_code)
#
#         if status_code == SpiToken.STATUS_PROGRAMMING_MODE:
#             return cls(SpiStatus.BUSY, status_code)
#
#         if status_code == SpiToken.STATUS_DEBUG_MODE:
#             return cls(SpiStatus.BUSY, status_code)
#
#         if status_code == SpiToken.STATUS_HW_ERROR:
#             return cls(SpiStatus.INACTIVE, status_code)
#
#         if status_code in range(SpiToken.DATA_READY_MIN,
#                                 SpiToken.DATA_READY_MAX):
#             return cls(SpiStatus.BUSY, status_code)
#
#         raise SpiDecodeError


class TrInfoRequest(SpiRequest):

    def encode(self):
        data = []
        data.append(SpiToken.COMMAND_TR_INFO)
        data.append(encode_command_type(0, 16))
        data.extend(generate_clock_data(16))
        data.append(calculate_crc(data, 0, len(data)))
        data.append(SpiToken.COMMAND_CHECK)

        return bytes(data)


class TrInfoResponse(SpiResponse):

    def __init__(self, data):
        self.data = data

    @classmethod
    def decode(cls, data):
        data = list(data)

        if len(data) != 20:
            raise SpiDecodeError

        if data[-1] != SpiToken.STATUS_CRC_OK:
            raise SpiDecodeError

        if calculate_crc(data, 2, 18) ^ encode_command_type(0, 16) != data[18]:
            raise SpiDecodeError

        data = data[2:-2]

        return cls(data)


class DataSendRequest(SpiRequest):

    def __init__(self, data):
        self.data = data

    def encode(self):
        data = []
        data.append(SpiToken.COMMAND_READ_WRITE)
        data.append(encode_command_type(1, len(self.data)))
        data.extend(self.data)
        data.append(calculate_crc(data, 0, len(data)))
        data.append(SpiToken.COMMAND_CHECK)

        return bytes(data)


class DataSendResponse(SpiResponse):

    @classmethod
    def decode(cls, data):
        data = list(data)

        if data[-1] != SpiToken.STATUS_CRC_OK:
            raise SpiDecodeError

        if calculate_crc(data, 2, len(data) - 2) ^ \
           encode_command_type(1, len(data) - 4) != data[-2]:
            raise SpiDecodeError

        return cls()


class _DataReceiveRequest(SpiRequest):

    def __init__(self, length):
        self.length = length

    def encode(self):
        data = []
        data.append(SpiToken.COMMAND_READ_WRITE)
        data.append(encode_command_type(0, self.length))
        data.extend(generate_clock_data(self.length))
        data.append(calculate_crc(data, 0, len(data)))
        data.append(SpiToken.COMMAND_CHECK)

        return bytes(data)


class _DataReceiveResponse(SpiRequest):

    def __init__(self, data):
        self.data = data

    @classmethod
    def decode(cls, data):
        data = list(data)

        if data[-1] != SpiToken.STATUS_CRC_OK:
            raise SpiDecodeError

        if calculate_crc(data, 2, len(data) - 2) ^ \
           encode_command_type(0, len(data) - 4) != data[-2]:
            raise SpiDecodeError

        return cls(bytes(data[2:-2]))


class DataReceivedReaction(SpiReaction):

    def __init__(self, data):
        self.data = data
