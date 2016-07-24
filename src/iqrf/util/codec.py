# -*- coding: utf-8 -*-

"""
Codec
=====

Codec module is a very simple abstraction that allows building modular and
scalable data serializers.

:copyright: (c) 2016 by Tomáš Rottenberg.
:license:  Apache 2, see license.txt for more details.

"""

import enum

__all__ = [
    "CodecError", "EncodeError", "DecodeError",
    "Encoder", "Decoder",
    "Message", "Request", "Response", "Reaction"
]

class CodecError(Exception):
    """An error indicating general codec exception."""

    pass

class EncodeError(CodecError):
    """An error thrown when exception raises during encoding."""

    pass

class DecodeError(CodecError):
    """An error thrown when exception raises during decoding."""

    pass

class Encoder:
    """A mixin that turns regular classes into encodable messages."""

    def tokenize(self):
        """Turns the object into smaller pieces called tokens which can be
        serialized to bytes. This method is usually called directly from the
        :func:`Encoder.encode` method and is meant to guarantee higher
        modularity."""

        raise NotImplementedError

    def encode(self):
        """Encodes the message to bytes."""

        raise NotImplementedError

class Decoder:
    """A mixin that gives regular classes the ability to be deserialized from
    bytes. Note that this mixin doesn't provide a recognition algorithm that
    would match a byte message to the corresponding class."""

    @classmethod
    def decode(cls, **kwargs):
        """Decodes the message from the given tokens."""

        raise NotImplementedError

class Message:
    """Abstract message that is capable of serialization."""

    def encode(self):
        """Encodes the message to byte. A common practice is to add the desired
        sublcass of :class:`Encoder` mixin to your message declaration to
        support this functionality."""

        raise NotImplementedError

    @classmethod
    def decode(cls, **kwargs):
        """Decodes the message from the given tokens. A common practice is to
        add the desired sublcass of :class:`Decoder` mixin to your message class
        declaration to support this functionality."""

        raise NotImplementedError

class Request(Message):
    """A message that is expected to be responded to with a an instance of the
    :class:`Response` class."""

    pass

class Response(Message):
    """A message that is sent as a response to a received instance of the
    :class:`Request` class."""

    pass

class Reaction(Message):
    """A message that can be sent at any time without any kind of foregoing
    request and is simply a reaction to the ongoing events."""

    pass
