import collections
import serial
import sys
import time

from . import codec
from . import iqrf_codec

__all__ = [
    "CdcReadTimeoutError",
    "RawCdcIO", "BufferedCdcIO",
    "open"
]

class CdcReadTimeoutError(Exception):
    pass

class RawCdcIO:

    def __init__(self, device):
        self._serial = serial.Serial(device, 9600, timeout=None)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def _remaining(self):
        return self._serial.in_waiting

    def _wait_until_readable(self, timeout):
        if timeout is not None and timeout == 0:
            return self._remaining()

        limit = time.time() + timeout if timeout is not None else sys.maxsize

        while time.time() < limit:
            available = self._remaining()
            if available > 0:
                return available

        raise CdcReadTimeoutError()

    def read(self, size, timeout=None):
        available = self._wait_until_readable(timeout)
        return self._serial.read(min(size, available))

    def write(self, data):
        return self._serial.write(data)

    def close(self):
        self._serial.close()

class BufferedCdcIO(RawCdcIO):

    def __init__(self, device):
        super().__init__(device)

        self._buffer = bytearray()
        self._async_buffer = bytearray()
        self._async_response_queue = collections.deque()

    def _read_cdc_response(self, timeout=None):
        stop = False
        while True:
            if len(self._buffer) > 0:
                boundary = self._buffer.find(iqrf_codec.CdcToken.TERMINATOR)
                if boundary != -1:
                    boundary += 1
                    data = bytes(self._buffer[:boundary])
                    self._buffer = self._buffer[boundary:]

                    message = iqrf_codec.decode_cdc_message(data)

                    if not isinstance(message, codec.CdcResponse):
                        raise IOError

                    if message.is_async():
                        self._async_message_queue.append(message)
                    else:
                        return message

            if stop:
                return None

            self._buffer.extend(self.read(1024, timeout=timeout))

            if timeout is not None and timeout == 0:
                stop = True

    def _read_async_cdc_response(self, timeout=None):
        stop = False
        while True:
            if len(self._async_buffer) > 0:
                boundary = self._async_buffer.find(iqrf_codec.CdcToken.TERMINATOR)
                if boundary != -1:
                    boundary += 1
                    data = bytes(self._async_buffer[:boundary])
                    self._async_buffer = self._async_buffer[boundary:]

                    message = iqrf_codec.decode_cdc_message(data)

                    if not isinstance(message, codec.CdcResponse):
                        raise IOError

                    if message.is_async():
                        return message
                    else:
                        raise IOError("Not an async response!")

            if stop:
                return None

            self._async_buffer.extend(self.read(1024, timeout=timeout))

            if timeout is not None and timeout == 0:
                stop = True

    def _write_cdc_request(self, message):
        if not isinstance(message, codec.CdcRequest):
            raise IOError("Not a request!")

        self.write(message.encode())

    def send(self, message, timeout=None):
        if timeout is not None and timeout <= 0:
            raise NotImplementedError("Non-blocking calls are currently not supported!")

        self._write_cdc_request(message)
        return self._read_cdc_response(timeout=timeout)

    def receive(self, timeout=None):
        if timeout is not None and timeout <= 0:
            raise NotImplementedError("Non-blocking calls are currently not supported!")

        if len(self._async_message_queue) > 0:
            return self._async_message_queue.popleft()

        return self._read_async_cdc_response(timeout=timeout)

def open(device):
    return BufferedCdcIO(device)
