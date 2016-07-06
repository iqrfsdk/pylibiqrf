"""Support for communication with IQRF devices using USB CDC."""

import enum
import re
import serial

from .log import logger

__all__ = [
    "CdcMessageCodecError", "CdcMessageEncodeError", "CdcMessageDecodeError",
    "CdcReadTimeoutError", "CdcMessage", "CdcIO",
    "encode_cdc_message", "decode_cdc_message", "open"
]

class CdcMessageCodecError(Exception):
    """General exception that indicates a CDC message codec error."""

    pass

class CdcMessageEncodeError(CdcMessageCodecError):
    """Exception signaling error during CDC message encoding."""

    pass

class CdcMessageDecodeError(CdcMessageCodecError):
    """Exception signaling error during CDC message decoding."""

    pass

class CdcReadTimeoutError(Exception):
    """An exception raised when read from CDC compatible device times out."""

class CdcMessageDirection(enum.Enum):
    """An enumeration of all possible directions that CDC message may have."""

    REQUEST = 0
    RESPONSE = 1

class CdcMessage(enum.Enum):
    """All known CDC messages understood by IQRF devices.

    Each member of the class specifies its own ``id``, ``direction``, ``token``,
    ``parameterizable`` flag and ``valuable`` flag. Aside from the ``id``
    property, these values define how the corresponding CDC message should be
    encoded and decoded.

    The format of all CDC messages looks as follows.

        [direction][body][terminator]

    Where direction is either ``request`` or ``response`` determined by byte
    values of ``>`` and ``<`` characters.

    The message body almost always consists a ``token`` and usually contains
    value and sometimes even parameter.

    All CDC messages are always terminated with ``\r`` character.

    Examples:
        * `>I\r`
        * `<I:GW-USB-03#02.01#03010000\r`
        * `>DS[0x05]:Hello\r`
        * `<DS:OK\r`

    If you are interested in more detailed dissection of a CDC message
    structure, you can refer to the source code of
    ``iqrf.cdc.encode_cdc_message`` and ``iqrf.cdc.encode_cdc_message`` methods.

    """

    ERROR = [0, CdcMessageDirection.RESPONSE, b"ERR", False, False]

    TEST = [1, CdcMessageDirection.REQUEST, b"", False, False]
    TEST_RESPONSE = [2, CdcMessageDirection.RESPONSE, b"OK", False, False]

    RESET = [3, CdcMessageDirection.REQUEST, b"R", False, False]
    RESET_RESPONSE = [4, CdcMessageDirection.RESPONSE, b"R", False, True]

    TR_RESET = [5, CdcMessageDirection.REQUEST, b"RT", False, False]
    TR_RESET_RESPONSE = [6, CdcMessageDirection.RESPONSE, b"RT", False, True]

    INFO = [7, CdcMessageDirection.REQUEST, b"I", False, False]
    INFO_RESPONSE = [8, CdcMessageDirection.RESPONSE, b"I", False, True]

    TR_INFO = [9, CdcMessageDirection.REQUEST, b"IT", False, False]
    TR_INFO_RESPONSE = [10, CdcMessageDirection.RESPONSE, b"IT", False, True]

    INDICATION = [11, CdcMessageDirection.REQUEST, b"B", False, False]
    INDICATION_RESPONSE = [12, CdcMessageDirection.RESPONSE, b"B", False, True]

    SPI_STATUS = [13, CdcMessageDirection.REQUEST, b"S", False, False]
    SPI_STATUS_RESPONSE = [14, CdcMessageDirection.RESPONSE, b"S", False, True]

    SEND_DATA = [15, CdcMessageDirection.REQUEST, b"DS", True, True]
    SEND_DATA_RESPONSE = [16, CdcMessageDirection.RESPONSE, b"DS", False, True]

    RECEIVED_DATA = [17, CdcMessageDirection.RESPONSE, b"DR", True, True]

    SWITCH_TO_CUSTOM_CLASS = [18, CdcMessageDirection.REQUEST, b"U", False, False]
    SWITCH_TO_CUSTOM_CLASS_RESPONSE = [19, CdcMessageDirection.RESPONSE, b"U", False, True]

    SWICH_TO_UART = [20, CdcMessageDirection.REQUEST, b"UU", False, False]
    SWICH_TO_UART_RESPONSE = [21, CdcMessageDirection.RESPONSE, b"UU", False, True]

    SWITCH_TO_SPI = [22, CdcMessageDirection.REQUEST, b"US", False, False]
    SWITCH_TO_SPI_RESPONSE = [22, CdcMessageDirection.RESPONSE, b"US", False, True]

    def __init__(self, value):
        self.id, self.direction, self.token, self.parameterizable, self.valuable = value

    @classmethod
    def get(cls, direction, token, parameterizable, valuable):
        for message in cls:
            if direction == message.direction and token == message.token:
                if parameterizable == message.parameterizable and valuable == message.valuable:
                    return message

        return None

class CdcMessageToken:
    """All possible tokens a CDC message might contain."""

    TERMINATOR = b"\r"
    REQUEST = b">"
    RESPONSE = b"<"
    SEPARATOR = b":"
    PARAMETER_SEPARATOR_LEFT = b"["
    PARAMETER_SEPARATOR_RIGHT = b"]"
    PARAMETER_PATTERN = re.compile(
        b"(.+?)\\" + PARAMETER_SEPARATOR_LEFT + b"(.+)\\" + PARAMETER_SEPARATOR_RIGHT + b"$"
    )

def decode_cdc_message(data, check_terminator=True):
    """Decodes a CDC message from a byte-like object."""

    logger.debug("Decoding: %s", data)

    # Check whether the passed bytes end with proper terminator token.
    if check_terminator and not data.endswith(CdcMessageToken.TERMINATOR):
        raise CdcMessageDecodeError("Message must end with carriage return!")

    # If the terminator was present, remove it from the data.
    if check_terminator:
        data = data[:-len(CdcMessageToken.TERMINATOR)]

    # Determine the direction and remove the direction token from the data.
    if data.startswith(CdcMessageToken.REQUEST):
        direction = CdcMessageDirection.REQUEST
        data = data[len(CdcMessageToken.REQUEST):]
    elif data.startswith(CdcMessageToken.RESPONSE):
        direction = CdcMessageDirection.RESPONSE
        data = data[len(CdcMessageToken.RESPONSE):]
    else:
        raise CdcMessageDecodeError("Invalid direction!")

    # Split the data using the value separator, which is usually 'b":"'.
    # If the value is present, this returns an array of length 2.
    # Otherwise an array with exactly one entry will be returned.
    keyed_data = data.split(CdcMessageToken.SEPARATOR)

    if len(keyed_data) == 1:
        # No value present.
        token = keyed_data[0]
        parameter = None
        value = None

    elif len(keyed_data) == 2:
        # Value is present.

        # If the match succeeds that means the message contains a parameter.
        match = CdcMessageToken.PARAMETER_PATTERN.match(keyed_data[0])

        if match is not None:
            # Parse the parameter.
            token = match.group(1)
            parameter = match.group(2)

        else:
            # No parameter present.
            token = keyed_data[0]
            parameter = None

        value = keyed_data[1]

    else:
        raise CdcMessageDecodeError("Only one value messages are supported!")

    logger.debug("Decoded as: %r, %s, %r, %r.", direction, token, parameter, value)

    message = CdcMessage.get(direction, token, parameter != None, value != None)

    if message is None:
        raise CdcMessageDecodeError("No such message!")

    return (message, parameter, value)

def encode_cdc_message(message, parameter=None, value=None):
    """Encodes a CDC message from a CdcMessage parameter and value."""

    # Determine the direction.
    if message.direction == CdcMessageDirection.REQUEST:
        direction = CdcMessageToken.REQUEST
    elif message.direction == CdcMessageDirection.RESPONSE:
        direction = CdcMessageToken.RESPONSE
    else:
        raise CdcMessageEncodeError("Invalid direction!")

    # Add value.
    if value is not None:
        if not message.valuable:
            raise CdcMessageEncodeError("Attempted to attach value to invaluable message.")

        value = CdcMessageToken.SEPARATOR + value
    else:
        if message.valuable:
            raise CdcMessageEncodeError("Value expected!")

        value = b""

    # Add parameter.
    if parameter is not None:
        if not message.parameterizable:
            raise CdcMessageEncodeError("Attempted to attach parameter to unparameterizable message.")

        parameter = b"".join([
            CdcMessageToken.PARAMETER_SEPARATOR_LEFT, parameter, CdcMessageToken.PARAMETER_SEPARATOR_RIGHT
        ])

    else:
        if message.parameterizable:
            raise CdcMessageEncodeError("Parameter expected!")

        parameter = b""

    # Join all the data and return.
    return b"".join([direction, message.token, parameter, value, CdcMessageToken.TERMINATOR])

class CdcIO:
    """This class implements basic interface for reading from and writing to a \
    USB CDC compatible IQRF device.

    """

    def __init__(self, device, timeout=1):
        self._timeout = timeout
        self._serial = serial.Serial(device, 9600, timeout=self._timeout)
        self._max_read_size = 1024
        self._buffer = bytearray()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def remaining(self):
        return self._serial.in_waiting

    def read(self, size=-1):
        if size is None or size < 0:
            size = max(self._max_read_size, self.remaining())
        elif size == 0:
            return b""

        read = self._serial.read(size)

        if len(read) == 0 and self._timeout > 0:
            raise CdcReadTimeoutError()

        return read

    def read_cdc_message(self):
        """Reads as much bytes as possible, buffering the result and attempts \
        to decode a CDC message from the buffer.

        If there is not enough data in the buffer, this method tries to
        continuously read data from the underlying device until at least one CDC
        message is read.

        """

        while True:
            boundary = self._buffer.find(CdcMessageToken.TERMINATOR)
            if boundary != -1:
                boundary += 1
                data = bytes(self._buffer[:boundary])
                self._buffer = self._buffer[boundary:]

                return decode_cdc_message(data)

            self._buffer.extend(self.read())

    def write(self, data):
        return self._serial.write(data)

    def write_cdc_message(self, message, parameter=None, value=None):
        """Encodes the passed CDC message and sends it to the underlying device."""

        return self._serial.write(encode_cdc_message(message, parameter=parameter, value=value))

    def close(self):
        self._serial.close()

def open(device, timeout=1):
    """An opener method for performing IO operations with IQRF USB CDC device.

    This method supports context management.

    """

    return CdcIO(device, timeout=timeout)
