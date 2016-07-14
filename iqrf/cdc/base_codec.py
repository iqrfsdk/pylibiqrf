from . import codec
from ..log import logger

__all__ = [
    "BaseCdcRequest", "BaseCdcResponse",
    "register_cdc_request", "register_cdc_response",
    "get_cdc_request_type", "get_cdc_request_id",
    "get_cdc_response_type", "get_cdc_response_id"
]

class BaseCdcRequest(codec.CdcRequest):

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

class BaseCdcResponse(codec.CdcResponse):

    ASYNC = False

    def __init__(self, status):
        self._status = status

    def __eq__(self, other):
        return  isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def status(self):
        return self._status

    @classmethod
    def is_async(cls):
        return cls.ASYNC

REQUESTS = {}
RESPONSES = {}

def register_cdc_request(cls, id):
    if not issubclass(cls, codec.CdcRequest):
        raise ValueError("Not a request type!")

    if cls in REQUESTS:
        raise ValueError("Duplicate request type!")

    REQUESTS[cls] = id
    logger.debug("Registering request: (%s:%s).", cls, id)

def register_cdc_response(cls, id):
    if not issubclass(cls, codec.CdcResponse):
        raise ValueError("Not a response type!")

    if cls in RESPONSES:
        raise ValueError("Duplicate response type!")

    RESPONSES[cls] = id
    logger.debug("Registering response: (%s:%s).", cls, id)

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
