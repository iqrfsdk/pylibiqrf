# -*- coding: utf-8 -*-

"""

Example of asynchronous UDP communication with IQRF gateway.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module implements a simple asynchronous UDP client that is capable of
sending very basic commands to a remote IQRF gateway.

The module is compatible with Python 3.5+.

Example usages:
    - udp_aio.py --help
    - udp_aio.py --host 10.1.30.62 --port 55000

:copyright: (c) 2016 by Tomáš Rottenberg.
:license: MIT, see license.txt for more details.

"""

import argparse
import asyncio
import time

from collections import deque

class DpaMessage:

    # TODO: Add methods for checking messages, calculating checksums, etc.

    def __init__(self, data):
        self.data = data

    def __str__(self):
        return "DpaMessage([{}])".format(self.data)

    def encode(self):
        return bytes(self.data)

    @staticmethod
    def decode(data):
        return DpaMessage(list(data))

class AsyncUdpHandler:

    def __init__(self, parent):
        self.parent = parent

    def connection_made(self, transport):
        pass

    def datagram_received(self, data, address):
        future = self.parent.response_futures.popleft()
        future.set_result(data)

    def error_received(self, exception):
        print("Error: ", exception)

    def connection_lost(self, exception):
        self.parent.loop.stop()

class AsyncUdpClient:

    def __init__(self, loop, address):
        self.address = address
        self.loop = loop
        self.response_futures = deque()
        self.handler_factory = lambda: AsyncUdpHandler(self)

    def start(self):
        self.task = asyncio.Task(self.loop.create_datagram_endpoint(self.handler_factory, remote_addr=self.address))
        self.transport, self.protocol = self.loop.run_until_complete(self.task)

    def stop(self):
        self.transport.close()
        self.loop.close()

    def send_message(self, data):
        future = asyncio.Future()
        self.transport.sendto(data)
        self.response_futures.append(future)
        return future

ARGS = argparse.ArgumentParser(description="IQRF gateway UDP AIO example.")
ARGS.add_argument("--host", action="store", dest="host", required=True, help="The name or address of the remote host.")
ARGS.add_argument("--port", action="store", dest="port", required=True, type=int, help="The port number of the remote host.")

def main():
    args = ARGS.parse_args()

    loop = asyncio.get_event_loop()

    client = AsyncUdpClient(loop, (args.host, args.port))
    client.start()

    enable_led = DpaMessage([34, 3, 0, 0, 0, 0, 0, 0, 6, 0, 0, 6, 1, 255, 255, 241, 237])
    disable_led = DpaMessage([34, 3, 0, 0, 0, 0, 0, 0, 6, 0, 0, 6, 0, 255, 255, 198, 221])

    try:
        response_future = client.send_message(enable_led.encode())
        loop.run_until_complete(asyncio.wait_for(response_future, 3))
        response = response_future.result()
        print("Sent: ", enable_led)
        print("Received: ", DpaMessage.decode(response))

        time.sleep(1)

        response_future = client.send_message(disable_led.encode())
        loop.run_until_complete(asyncio.wait_for(response_future, 3))
        response = response_future.result()
        print("Sent: ", disable_led)
        print("Received: ", DpaMessage.decode(response))
    except asyncio.TimeoutError:
        print("Operation timed out. Please check your internet connection and retry.")

    client.stop()

if __name__ == "__main__":
    main()
