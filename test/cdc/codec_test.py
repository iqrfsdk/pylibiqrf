import unittest

from iqrf.cdc.codec import (
    CdcMessage,
    decode_cdc_message
)

SIMPLE_MESSAGES = {
    b"<ERR\r": (CdcMessage.COMMUNICATION_ERROR, None, None),
    b">\r": (CdcMessage.COMMUNICATION_REQUEST, None, None),
    b"<OK\r": (CdcMessage.COMMUNICATION_RESPONSE, None, None),
    b">R\r": (CdcMessage.DEVICE_RESET_REQUEST, None, None),
    b">RT\r": (CdcMessage.MODULE_RESET_REQUEST, None, None),
    b">I\r": (CdcMessage.DEVICE_INFO_REQUEST, None, None),
    b">B\r": (CdcMessage.CONNECTIVITY_INDICATION_REQUEST, None, None),
    b">S\r": (CdcMessage.SPI_STATUS_REQUEST, None, None)
}

VALUE_MESSAGES = {
    b"<R:OK\r": (CdcMessage.DEVICE_RESET_RESPONSE, None, b"OK"),
    b"<I:GW-USB-03#02.01#03010000\r": (CdcMessage.DEVICE_INFO_RESPONSE, None, b"GW-USB-03#02.01#03010000"),
    b"<B:OK\r": (CdcMessage.CONNECTIVITY_INDICATION_RESPONSE, None, b"OK"),
    b"<DS:OK\r": (CdcMessage.SEND_DATA_RESPONSE, None, b"OK"),
    b"<DS:ERR\r": (CdcMessage.SEND_DATA_RESPONSE, None, b"ERR"),
    b"<DS:BUSY\r": (CdcMessage.SEND_DATA_RESPONSE, None, b"BUSY")
}

PARAMETER_MESSAGES = {
    b">DS[0x05]:Hello\r": (CdcMessage.SEND_DATA_REQUEST, b"0x05", b"Hello"),
    b"<DR[0x02]:Hi\r": (CdcMessage.RECEIVED_DATA_RESPONSE, b"0x02", b"Hi")
}

class DecoderTests(unittest.TestCase):

    def test_simple_message_decoding(self):
        for encoded, decoded in SIMPLE_MESSAGES.items():
            self.assertEqual(decode_cdc_message(encoded), decoded)

    def test_value_message_decoding(self):
        for encoded, decoded in VALUE_MESSAGES.items():
            self.assertEqual(decode_cdc_message(encoded), decoded)

    def test_parameter_message_decoding(self):
        for encoded, decoded in PARAMETER_MESSAGES.items():
            self.assertEqual(decode_cdc_message(encoded), decoded)

if __name__ == '__main__':
    unittest.main()
