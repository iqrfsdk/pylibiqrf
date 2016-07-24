# -*- coding: utf-8 -*-

"""
IQRF CDC IO
===========

An implementation of communication channel with IQRF USB CDC devices.

:copyright: (c) 2016 by Tomáš Rottenberg.
:license:  Apache 2, see license.txt for more details.

"""

import collections
import serial
import sys
import time

from . import cdc_codec

__all__ = [
    "ReadTimeoutError",
    "RawCdcIO", "BufferedCdcIO",
    "open"
]

class ReadTimeoutError(Exception):
    pass

class RawCdcIO:

    def __init__(self, port):
        self._serial = serial.Serial(port=port, baudrate=9600, timeout=None)

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
            time.sleep(0.05)

        raise ReadTimeoutError

    def read(self, size, timeout=None):
        available = self._wait_until_readable(timeout)
        return self._serial.read(min(size, available))

    def write(self, data):
        return self._serial.write(data)

    def close(self):
        self._serial.close()

class BufferedCdcIO(RawCdcIO):

    def __init__(self, port):
        super().__init__(port)

        self._buffer = bytearray()
        self._reactions = collections.deque()

    def _read_cdc_response(self, timeout=None):
        stop = False
        while True:
            if len(self._buffer) > 0:
                boundary = self._buffer.find(cdc_codec.CdcToken.TERMINATOR)
                if boundary != -1:
                    boundary += 1
                    data = bytes(self._buffer[:boundary])
                    self._buffer = self._buffer[boundary:]

                    message = cdc_codec.decode_cdc_message(data)

                    if isinstance(message, cdc_codec.CdcResponse):
                        return message
                    elif isinstance(message, cdc_codec.CdcReaction):
                        self._reactions.append(message)
                    else:
                        raise cdc.CdcCodecError

            if stop:
                return None

            self._buffer.extend(self.read(1024, timeout=timeout))

            if timeout is not None and timeout == 0:
                stop = True

    def _read_cdc_reaction(self, timeout=None):
        stop = False
        while True:
            if len(self._buffer) > 0:
                boundary = self._buffer.find(cdc_codec.CdcToken.TERMINATOR)
                if boundary != -1:
                    boundary += 1
                    data = bytes(self._buffer[:boundary])
                    self._buffer = self._buffer[boundary:]

                    message = cdc_codec.decode_cdc_message(data)

                    if not isinstance(message, cdc_codec.CdcReaction):
                        raise cdc_codec.CdcCodecError

                    return message

            if stop:
                return None

            self._buffer.extend(self.read(1024, timeout=timeout))

            if timeout is not None and timeout == 0:
                stop = True

    def _write_cdc_request(self, message):
        if not isinstance(message, cdc_codec.CdcRequest):
            raise cdc_codec.CdcCodecError

        self.write(message.encode())

    def send(self, message, timeout=None):
        if timeout is not None and timeout <= 0:
            raise NotImplementedError("Non-blocking calls are currently not supported!")

        self._write_cdc_request(message)
        return self._read_cdc_response(timeout=timeout)

    def receive(self, timeout=None):
        if timeout is not None and timeout <= 0:
            raise NotImplementedError("Non-blocking calls are currently not supported!")

        if len(self._reactions) > 0:
            return self._reactions.popleft()

        return self._read_cdc_reaction(timeout=timeout)

def open(port):
    return BufferedCdcIO(port)
