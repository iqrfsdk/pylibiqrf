import sys
import time

class IoError(IOError):
    pass

class IoTimeoutError(IoError):
    pass

def to_iotime(time):
    if time is None:
        time = sys.maxsize

    return time

def wait(expression, condition, timeout=None):
    timeout = to_iotime(timeout)

    delta = 0

    while delta < timeout:
        start = time.time()
        result = expression()
        delta += time.time() - start

        if delta > timeout:
            raise IoTimeoutError

        start = time.time()
        evaluation = condition(result)
        delta += time.time() - start

        if delta > timeout:
            raise IoTimeoutError

        start = time.time()
        if evaluation:
            return delta, result
        else:
            time.sleep(0.05)
        delta += time.time() - start

    raise IoTimeoutError
