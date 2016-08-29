# -*- coding: utf-8 -*-

"""
IQRF CDC IO
===========

An implementation of communication channel with IQRF USB CDC devices.

:copyright: (c) 2016 by Tomáš Rottenberg.
:license:  Apache 2, see license.txt for more details.

"""

import collections
import sys
import time

import serial

from .cdc_codec import CdcToken, CdcRequest, CdcResponse, CdcReaction, decode_cdc_message
from ..util.io import IoError, to_iotime, wait

__all__ = [
    "RawCdcIo", "BufferedCdcIo",
    "open"
]

class RawCdcIo:

    def __init__(self, port):
        self._serial = serial.Serial(port=port, baudrate=9600, timeout=None)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def remaining(self):
        return self._serial.in_waiting

    def read(self, size, timeout=None):
        delta, available = wait(self.remaining, lambda x: x > 0, timeout=timeout)
        return self._serial.read(min(size, available))

    def write(self, data, timeout=None):
        return self._serial.write(data)

    def close(self):
        self._serial.close()

class BufferedCdcIo(RawCdcIo):

    def __init__(self, port):
        super().__init__(port)

        self._buffer = bytearray()
        self._reactions = collections.deque()

    def _read_cdc_message(self, timeout=None):
        timeout = to_iotime(timeout)

        while True:
            start = time.time()
            if len(self._buffer) > 0:
                boundary = self._buffer.find(CdcToken.TERMINATOR)
                if boundary != -1:
                    boundary += 1
                    data = bytes(self._buffer[:boundary])
                    self._buffer = self._buffer[boundary:]

                    return decode_cdc_message(data)

            self._buffer.extend(self.read(1024, timeout=timeout))
            timeout -= time.time() - start

    def send(self, message, timeout=None):
        if not isinstance(message, CdcRequest):
            raise TypeError("Invalid message type!")

        timeout = to_iotime(timeout)

        start = time.time()
        self.write(message.encode(), timeout=timeout)
        timeout -= time.time() - start

        while True:
            start = time.time()
            message = self._read_cdc_message(timeout=timeout)

            if isinstance(message, CdcReaction):
                self._reactions.append(message)
            elif isinstance(message, CdcResponse):
                return message
            else:
                raise IoError

            timeout -= time.time() - start

    def receive(self, timeout=None):
        if len(self._reactions) > 0:
            return self._reactions.popleft()

        message = self._read_cdc_message(timeout=timeout)

        if not isinstance(message, CdcReaction):
            raise IoError

        return message

def open(port):
    return BufferedCdcIo(port)
