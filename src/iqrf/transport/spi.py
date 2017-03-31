import sys

if sys.platform != "linux":
    raise NotImplementedError("Unfortunately, this module has not been "
                              "implemented on your platform yet.")

from . import spi_codec
from . import spi_io

from .spi_codec import *
from .spi_io import *

__all__ = (
    spi_codec.__all__ +
    spi_io.__all__
)
