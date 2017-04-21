import unittest

from iqrf.transport import cdc

SIMPLE_MESSAGES = {
    b"<ERR\r": cdc.ErrorResponse(),
    b">\r": cdc.TestRequest(),
    b"<OK\r": cdc.TestResponse(),
    b">R\r": cdc.ResetRequest(),
    b">RT\r": cdc.TrResetRequest(),
    b">I\r": cdc.InfoRequest(),
    b">B\r": cdc.IndicationRequest(),
    b">S\r": cdc.SpiStatusRequest()
}

VALUE_MESSAGES = {
    b"<R:OK\r": cdc.ResetResponse(cdc.CdcStatus.OK),
    b"<I:GW-USB-03#02.01#03010000\r": cdc.InfoResponse("GW-USB-03", "02.01", "03010000"),
    b"<B:OK\r": cdc.IndicationResponse(cdc.CdcStatus.OK),
    b"<DS:OK\r": cdc.DataSendResponse(cdc.CdcStatus.OK),
    b"<DS:BUSY\r": cdc.DataSendResponse(cdc.CdcStatus.BUSY),
    b"<DS:ERR\r": cdc.DataSendResponse(cdc.CdcStatus.ERROR),
    b"<IT:\x81\x00\x02:8$y\x08\r": cdc.TrInfoResponse(b"\x81\x00\x02:8$y\x08")
}

PARAMETER_MESSAGES = {
    b">DS\x06:Hello.\r": cdc.DataSendRequest(b"Hello."),
    b"<DR\x03:Hi!\r": cdc.DataReceivedReaction(b"Hi!")
}


class EncoderTests(unittest.TestCase):

    def test_simple_message_encoding(self):
        for encoded, decoded in SIMPLE_MESSAGES.items():
            self.assertEqual(encoded, decoded.encode())

    def test_value_message_encoding(self):
        for encoded, decoded in VALUE_MESSAGES.items():
            self.assertEqual(encoded, decoded.encode())

    def test_parameter_message_encoding(self):
        for encoded, decoded in PARAMETER_MESSAGES.items():
            self.assertEqual(encoded, decoded.encode())


class DecoderTests(unittest.TestCase):

    def test_simple_message_decoding(self):
        for encoded, decoded in SIMPLE_MESSAGES.items():
            self.assertEqual(cdc.decode_cdc_message(encoded), decoded)

    def test_value_message_decoding(self):
        for encoded, decoded in VALUE_MESSAGES.items():
            self.assertEqual(cdc.decode_cdc_message(encoded), decoded)

    def test_parameter_message_decoding(self):
        for encoded, decoded in PARAMETER_MESSAGES.items():
            self.assertEqual(cdc.decode_cdc_message(encoded), decoded)


class EncoderDecoderTests(unittest.TestCase):

    def test_simple_message_encoding_and_decoding(self):
        for encoded, decoded in SIMPLE_MESSAGES.items():
            re_encoded = decoded.encode()
            re_decoded = cdc.decode_cdc_message(encoded)

            self.assertEqual(encoded, re_encoded)
            self.assertEqual(decoded, re_decoded)

            self.assertEqual(re_decoded.encode(), encoded)
            self.assertEqual(cdc.decode_cdc_message(re_encoded), decoded)

    def test_value_message_encoding_and_decoding(self):
        for encoded, decoded in VALUE_MESSAGES.items():
            re_encoded = decoded.encode()
            re_decoded = cdc.decode_cdc_message(encoded)

            self.assertEqual(encoded, re_encoded)
            self.assertEqual(decoded, re_decoded)

            self.assertEqual(re_decoded.encode(), encoded)
            self.assertEqual(cdc.decode_cdc_message(re_encoded), decoded)

    def test_parameter_message_encoding_and_decoding(self):
        for encoded, decoded in PARAMETER_MESSAGES.items():
            re_encoded = decoded.encode()
            re_decoded = cdc.decode_cdc_message(encoded)

            self.assertEqual(encoded, re_encoded)
            self.assertEqual(decoded, re_decoded)

            self.assertEqual(re_decoded.encode(), encoded)
            self.assertEqual(cdc.decode_cdc_message(re_encoded), decoded)
