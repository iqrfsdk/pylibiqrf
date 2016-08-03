import ctypes
import fnctl

from periphery import spi

spi.SPI._SPI_IOC_MESSAGE_2 = 0x40406b00

class RawSpiIO:

    def __init__(self, port):
        self._spi = spi.SPI(port, 0, 250000, bit_order="msb", bits_per_word=8, extra_flags=0)

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
        except OSError as e:
            raise SPIError(e.errno, "SPI initial transfer: " + e.strerror)

        for i in range(1, buf_len):
            xfer_data.tx_buf = buf_addr + i
            xfer_data.rx_buf = buf_addr + i

            if i == buf_len - 1:
                xfer_data.delay_usecs = 5
                xfer_data.cs_change = 0

            try:
                fcntl.ioctl(self._spi._fd, spi.SPI._SPI_IOC_MESSAGE_1, xfer_data)
            except OSError as e:
                raise SPIError(e.errno, "SPI transfer: " + e.strerror)

        if isinstance(data, bytes):
            return bytes(bytearray(buf))
        elif isinstance(data, bytearray):
            return bytearray(buf)
        elif isinstance(data, list):
            return buf.tolist()

    def close(self):
        self._spi.close()
