import io
import serial

__all__ = ["CdcIO", "open"]

class CdcIO:

    def __init__(self, device):
        self._serial = serial.Serial(device, 9600, timeout=1)
        self._max_read_size = 1024

    def remaining(self):
        return self._serial.in_waiting

    def read(self, size=-1):
        if size is None or size < 0:
            size = self._max_read_size

        return self._serial.read(size)

    def write(self, data):
        return self._serial.write(data)

    def flush(self):
        return self._serial.flush()

    def close(self):
        self._serial.close()

def open(device):
    return CdcIO(device)
