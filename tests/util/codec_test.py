import unittest

from iqrf.util import codec


class EncoderTests(unittest.TestCase):

    def test_encode_exception(self):
        encoder = codec.Encoder()

        with self.assertRaises(NotImplementedError):
            encoder.encode()


class DencoderTests(unittest.TestCase):

    def test_dencode_exception(self):
        decoder = codec.Decoder()

        with self.assertRaises(NotImplementedError):
            decoder.decode()


class MessageTests(unittest.TestCase):

    def test_message_exception(self):
        message = codec.Message()

        with self.assertRaises(NotImplementedError):
            message.decode()

        with self.assertRaises(NotImplementedError):
            message.encode()


class RequestTests(unittest.TestCase):

    def test_request_exception(self):
        request = codec.Request()

        with self.assertRaises(NotImplementedError):
            request.decode()

        with self.assertRaises(NotImplementedError):
            request.encode()


class ResponseTests(unittest.TestCase):

    def test_response_exception(self):
        response = codec.Response()

        with self.assertRaises(NotImplementedError):
            response.decode()

        with self.assertRaises(NotImplementedError):
            response.encode()


class ReactionTests(unittest.TestCase):

    def test_reaction_exception(self):
        reaction = codec.Reaction()

        with self.assertRaises(NotImplementedError):
            reaction.decode()

        with self.assertRaises(NotImplementedError):
            reaction.encode()
