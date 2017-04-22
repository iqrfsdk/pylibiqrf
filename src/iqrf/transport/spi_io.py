# -*- coding: utf-8 -*-

"""
IQRF SPI IO
===========

An implementation of communication channel with IQRF SPI devices.

:copyright: (c) 2016 by Tomáš Rottenberg.
:license:  Apache 2, see license.txt for more details.

"""

import array
import collections
import ctypes
import fcntl

from periphery import gpio, spi

from .spi_codec import (
    DataSendRequest, DataSendResponse,
    SpiCodecError,
    SpiRequest,
    SpiToken,
    TrInfoRequest, TrInfoResponse,
    _DataReceiveRequest, _DataReceiveResponse,
    DataReceivedReaction
)

from ..util.io import IoError, to_iotime, wait

__all__ = [
    "SpiError",
    "RawSpiIo", "BufferedSpiIo",
    "open"
]

spi.SPI._SPI_IOC_MESSAGE_2 = 0x40406b00


class SpiError(IoError):
    pass


class RawSpiIo:

    def __init__(self, port):
        try:
            self._ce0_pin = gpio.GPIO(8, "low")
            self._pwr_pin = gpio.GPIO(23, "high")
            self._spi = spi.SPI(port, 0, 250000, bit_order="msb", bits_per_word=8, extra_flags=0)
        except IOError as error:
            raise SpiError(error)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def transfer(self, data):
        if not isinstance(data, bytes) and not isinstance(data, bytearray) and not isinstance(data, list):
            raise TypeError("Invalid data type, should be bytes, bytearray, or list.")

        try:
            buf = array.array('B', data)
        except OverflowError:
            raise ValueError("Invalid data bytes.")

        buf_addr, buf_len = buf.buffer_info()

        xfer_init = spi._CSpiIocTransfer()
        xfer_init.tx_buf = 0
        xfer_init.rx_buf = 0
        xfer_init.len = 0
        xfer_init.delay_usecs = 5
        xfer_init.speed_hz = 250000
        xfer_init.bits_per_word = 8
        xfer_init.cs_change = 0
        xfer_init.tx_nbits = 0
        xfer_init.rx_nbits = 0

        xfer_data = spi._CSpiIocTransfer()
        xfer_data.tx_buf = buf_addr
        xfer_data.rx_buf = buf_addr
        xfer_data.len = 1
        xfer_data.delay_usecs = 150
        xfer_data.speed_hz = 250000
        xfer_data.bits_per_word = 8
        xfer_data.cs_change = 0
        xfer_data.tx_nbits = 0
        xfer_data.rx_nbits = 0

        if buf_len > 1:
            xfer_data.cs_change = 1

        try:
            spi_xfer = (spi._CSpiIocTransfer * 2)()
            spi_xfer[0] = xfer_init
            spi_xfer[1] = xfer_data

            fcntl.ioctl(self._spi._fd, spi.SPI._SPI_IOC_MESSAGE_2, ctypes.addressof(spi_xfer))
        except OSError as error:
            raise SpiError(error.errno, "SPI initial transfer: " + error.strerror)

        for i in range(1, buf_len):
            xfer_data.tx_buf = buf_addr + i
            xfer_data.rx_buf = buf_addr + i

            if i == buf_len - 1:
                xfer_data.delay_usecs = 5
                xfer_data.cs_change = 0

            try:
                fcntl.ioctl(self._spi._fd, spi.SPI._SPI_IOC_MESSAGE_1, xfer_data)
            except OSError as error:
                raise SpiError(error.errno, "SPI transfer: " + error.strerror)

        if isinstance(data, bytes):
            return bytes(bytearray(buf))
        elif isinstance(data, bytearray):
            return bytearray(buf)
        elif isinstance(data, list):
            return buf.tolist()

    def close(self):
        try:
            self._spi.close()
            self._pwr_pin.close()
            self._ce0_pin.close()
        except IOError as error:
            raise SpiError(error)


class BufferedSpiIo(RawSpiIo):

    def __init__(self, port):
        super().__init__(port)

        self._reactions = collections.deque()

    def _wait_until_readable(self, timeout=None):
        _, result = wait(lambda: self.transfer([SpiToken.COMMAND_CHECK]), lambda x: x[0] in range(SpiToken.DATA_READY_MIN, SpiToken.DATA_READY_MAX), timeout=timeout)
        readable = result[0]
        return 64 if readable == SpiToken.DATA_READY_MIN else readable - SpiToken.DATA_READY_MIN

    def send(self, message, timeout=None):
        if not isinstance(message, SpiRequest):
            raise TypeError("Invalid message type!")

        while True:
            timeout = to_iotime(timeout)
            delta, result = wait(lambda: self.transfer([SpiToken.COMMAND_CHECK]), lambda x: x[0] == SpiToken.STATUS_COMMUNICATION_MODE or x[0] in range(SpiToken.DATA_READY_MIN, SpiToken.DATA_READY_MAX), timeout=timeout)

            timeout -= delta
            result = result[0]

            if result == SpiToken.STATUS_COMMUNICATION_MODE:
                break
            else:
                readable = 64 if result == SpiToken.DATA_READY_MIN else result - SpiToken.DATA_READY_MIN

                transfer = self.transfer(_DataReceiveRequest(readable).encode())
                response = _DataReceiveResponse.decode(transfer)

                self._reactions.append(DataReceivedReaction(response.data))

        transfer = self.transfer(message.encode())

        if isinstance(message, TrInfoRequest):
            return TrInfoResponse.decode(transfer)
        elif isinstance(message, DataSendRequest):
            return DataSendResponse.decode(transfer)
        else:
            raise SpiCodecError

    def receive(self, timeout=None):
        if len(self._reactions) > 0:
            return self._reactions.popleft()

        readable = self._wait_until_readable(timeout)

        transfer = self.transfer(_DataReceiveRequest(readable).encode())
        response = _DataReceiveResponse.decode(transfer)
        return DataReceivedReaction(response.data)


def open(port):
    return BufferedSpiIo(port)
