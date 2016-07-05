import enum
import re

from ..log import logger

__all__ = ["CdcMessage", "decode_cdc_message"]

class CdcMessageCodecError(Exception):
    pass

class CdcMessageEncodeError(CdcMessageCodecError):
    pass

class CdcMessageDecodeError(CdcMessageCodecError):
    pass

class CdcMessageDirection(enum.Enum):
    REQUEST = 0
    RESPONSE = 1

class CdcMessage(enum.Enum):
    COMMUNICATION_ERROR = [0, CdcMessageDirection.RESPONSE, b"ERR", False, False]

    COMMUNICATION_REQUEST = [1, CdcMessageDirection.REQUEST, b"", False, False]
    COMMUNICATION_RESPONSE = [2, CdcMessageDirection.RESPONSE, b"OK", False, False]

    DEVICE_RESET_REQUEST = [3, CdcMessageDirection.REQUEST, b"R", False, False]
    DEVICE_RESET_RESPONSE = [4, CdcMessageDirection.RESPONSE, b"R", False, True]

    MODULE_RESET_REQUEST = [5, CdcMessageDirection.REQUEST, b"RT", False, False]
    MODULE_RESET_RESPONSE = [6, CdcMessageDirection.RESPONSE, b"RT", False, True]

    DEVICE_INFO_REQUEST = [7, CdcMessageDirection.REQUEST, b"I", False, False]
    DEVICE_INFO_RESPONSE = [8, CdcMessageDirection.RESPONSE, b"I", False, True]

    MODULE_INFO_REQUEST = [9, CdcMessageDirection.REQUEST, b"IT", False, False]
    MODULE_INFO_RESPONSE = [10, CdcMessageDirection.RESPONSE, b"IT", False, True]

    CONNECTIVITY_INDICATION_REQUEST = [11, CdcMessageDirection.REQUEST, b"B", False, False]
    CONNECTIVITY_INDICATION_RESPONSE = [12, CdcMessageDirection.RESPONSE, b"B", False, True]

    SPI_STATUS_REQUEST = [13, CdcMessageDirection.REQUEST, b"S", False, False]
    SPI_STATUS_RESPONSE = [14, CdcMessageDirection.RESPONSE, b"S", False, True]

    SEND_DATA_REQUEST = [15, CdcMessageDirection.REQUEST, b"DS", True, True]
    SEND_DATA_RESPONSE = [16, CdcMessageDirection.RESPONSE, b"DS", False, True]

    RECEIVED_DATA_RESPONSE = [17, CdcMessageDirection.RESPONSE, b"DR", True, True]

    SWITCH_TO_CUSTOM_CLASS_REQUEST = [18, CdcMessageDirection.REQUEST, b"U", False, False]
    SWITCH_TO_CUSTOM_CLASS_RESPONSE = [19, CdcMessageDirection.RESPONSE, b"U", False, True]

    SWITCH_TO_UART_REQUEST = [20, CdcMessageDirection.REQUEST, b"UU", False, False]
    SWITCH_TO_UART_RESPONSE = [21, CdcMessageDirection.RESPONSE, b"UU", False, True]

    SWITCH_TO_SPI_REQUEST = [22, CdcMessageDirection.REQUEST, b"US", False, False]
    SWITCH_TO_SPI_RESPONSE = [22, CdcMessageDirection.RESPONSE, b"US", False, True]

def _get_id(message):
    return message.value[0]

def _get_direction(message):
    return message.value[1]

def _get_token(message):
    return message.value[2]

def _supports_parameter(message):
    return message.value[3]

def _supports_value(message):
    return message.value[4]

def _get_message_type_by_parameters(direction, token, parameter, value):
    for message in CdcMessage:
        if direction == _get_direction(message) and \
        token == _get_token(message) and \
        parameter == _supports_parameter(message) and \
        value == _supports_value(message):
            return message

    return None

def _get_response_type_by_token(token):
    for message in CdcMessage:
        if _is_response(message) and token == _get_token(message):
            return message

    return None

CDC_MESSAGE_TERMINATOR = b"\r"

CDC_REQUEST_IDENTIFIER = b">"
CDC_RESPONSE_IDENTIFIER = b"<"

CDC_VALUE_SEPARATOR = b":"

CDC_PARAMETER_REGEX = b"(.+?)\[(.+)\]$"

def decode_cdc_message(data):
    if not data.endswith(CDC_MESSAGE_TERMINATOR):
        raise CdcMessageDecodeError(
            "All messages must end with '{}'".format(CDC_MESSAGE_TERMINATOR)
        )

    if data.startswith(CDC_REQUEST_IDENTIFIER):
        direction = CdcMessageDirection.REQUEST
        data = data[len(CDC_REQUEST_IDENTIFIER):-len(CDC_MESSAGE_TERMINATOR)]
    elif data.startswith(CDC_RESPONSE_IDENTIFIER):
        direction = CdcMessageDirection.RESPONSE
        data = data[len(CDC_RESPONSE_IDENTIFIER):-len(CDC_MESSAGE_TERMINATOR)]
    else:
        raise CdcMessageDecodeError("Invalid direction!")

    keyed_data = data.split(CDC_VALUE_SEPARATOR)

    if len(keyed_data) == 1:
        token = keyed_data[0]
        parameter = None
        value = None

    elif len(keyed_data) == 2:
        match = re.match(CDC_PARAMETER_REGEX, keyed_data[0])

        if match is not None:
            token = match.group(1)
            parameter = match.group(2)

        else:
            token = keyed_data[0]
            parameter = None

        value = keyed_data[1]

    else:
        raise CdcMessageDecodeError("Invalid values!")

    logger.debug(
        "Decoder matched {} to [direction={}, token={}, parameter={}, value={}]".format(
            data, direction, token, parameter, value
        )
    )

    message_type = _get_message_type_by_parameters(
        direction, token, parameter != None, value != None
    )

    if message_type is None:
        raise CdcMessageDecodeError(
            "No message matching ({}, {}, {}, {})".format(
                direction, token, parameter != None, value != None
            )
        )

    return (message_type, parameter, value)
