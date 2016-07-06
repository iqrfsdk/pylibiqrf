import unittest
from iqrf.cdc import CdcMessage, encode_cdc_message, decode_cdc_message

SIMPLE_MESSAGES = {
    b"<ERR\r": (CdcMessage.ERROR, None, None),
    b">\r": (CdcMessage.TEST, None, None),
    b"<OK\r": (CdcMessage.TEST_RESPONSE, None, None),
    b">R\r": (CdcMessage.RESET, None, None),
    b">RT\r": (CdcMessage.TR_RESET, None, None),
    b">I\r": (CdcMessage.INFO, None, None),
    b">B\r": (CdcMessage.INDICATION, None, None),
    b">S\r": (CdcMessage.SPI_STATUS, None, None)
}

VALUE_MESSAGES = {
    b"<R:OK\r": (CdcMessage.RESET_RESPONSE, None, b"OK"),
    b"<I:GW-USB-03#02.01#03010000\r": (CdcMessage.INFO_RESPONSE, None, b"GW-USB-03#02.01#03010000"),
    b"<B:OK\r": (CdcMessage.INDICATION_RESPONSE, None, b"OK"),
    b"<DS:OK\r": (CdcMessage.SEND_DATA_RESPONSE, None, b"OK"),
    b"<DS:ERR\r": (CdcMessage.SEND_DATA_RESPONSE, None, b"ERR"),
    b"<DS:BUSY\r": (CdcMessage.SEND_DATA_RESPONSE, None, b"BUSY")
}

PARAMETER_MESSAGES = {
    b">DS[0x05]:Hello\r": (CdcMessage.SEND_DATA, b"0x05", b"Hello"),
    b"<DR[0x02]:Hi\r": (CdcMessage.RECEIVED_DATA, b"0x02", b"Hi")
}

class EncoderTests(unittest.TestCase):

    def test_simple_message_encoding(self):
        for encoded, decoded in SIMPLE_MESSAGES.items():
            self.assertEqual(encode_cdc_message(*decoded), encoded)

    def test_value_message_encoding(self):
        for encoded, decoded in VALUE_MESSAGES.items():
            self.assertEqual(encode_cdc_message(*decoded), encoded)

    def test_parameter_message_encoding(self):
        for encoded, decoded in PARAMETER_MESSAGES.items():
            self.assertEqual(encode_cdc_message(*decoded), encoded)

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

class EncoderDecoderTests(unittest.TestCase):

    def test_simple_message_encoding_and_decoding(self):
        for encoded, decoded in SIMPLE_MESSAGES.items():
            re_encoded = encode_cdc_message(*decoded)
            re_decoded = decode_cdc_message(encoded)

            self.assertEqual(encoded, re_encoded)
            self.assertEqual(decoded, re_decoded)

            self.assertEqual(encode_cdc_message(*re_decoded), encoded)
            self.assertEqual(decode_cdc_message(re_encoded), decoded)

    def test_value_message_encoding_and_decoding(self):
        for encoded, decoded in VALUE_MESSAGES.items():
            re_encoded = encode_cdc_message(*decoded)
            re_decoded = decode_cdc_message(encoded)

            self.assertEqual(encoded, re_encoded)
            self.assertEqual(decoded, re_decoded)

            self.assertEqual(encode_cdc_message(*re_decoded), encoded)
            self.assertEqual(decode_cdc_message(re_encoded), decoded)

    def test_parameter_message_encoding_and_decoding(self):
        for encoded, decoded in PARAMETER_MESSAGES.items():
            re_encoded = encode_cdc_message(*decoded)
            re_decoded = decode_cdc_message(encoded)

            self.assertEqual(encoded, re_encoded)
            self.assertEqual(decoded, re_decoded)

            self.assertEqual(encode_cdc_message(*re_decoded), encoded)
            self.assertEqual(decode_cdc_message(re_encoded), decoded)
