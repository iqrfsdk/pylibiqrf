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
:license: Apache 2, see license.txt for more details.

"""

import argparse
import asyncio
import time

from collections import deque
from iqrf.dpa import DpaMessage

class AsyncUdpHandler:

    def __init__(self, parent):
        self.parent = parent
        self.processing = None
        self.response_buffer = []

    def connection_made(self, transport):
        pass

    def datagram_received(self, data, address):
        if not self.processing:
            if len(self.parent.response_futures) < 1:
                return

            self.processing = self.parent.response_futures.popleft()

        self.response_buffer.append(data)

        future, responses = self.processing
        responses -= 1

        if responses > 0:
            self.processing = (future, responses)
        else:
            future.set_result(self.response_buffer[:])

            self.response_buffer = []
            self.processing = None

    def error_received(self, exception):
        print("Error:", exception)

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

    def send(self, data, responses = 0):
        if responses > 0:
            future = asyncio.Future()
            self.response_futures.append((future, responses))
            self.transport.sendto(data)
            return future
        else:
            print("called")
            self.transport.sendto(data)

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
        response_future = client.send(enable_led.encode(), responses = 1)
        loop.run_until_complete(asyncio.wait_for(response_future, 3))
        response = response_future.result()[0]
        print("Sent:", enable_led)
        print("Received:", DpaMessage.decode(response))

        time.sleep(1)

        response_future = client.send(disable_led.encode(), responses = 1)
        loop.run_until_complete(asyncio.wait_for(response_future, 3))
        response = response_future.result()[0]
        print("Sent:", disable_led)
        print("Received:", DpaMessage.decode(response))
    except asyncio.TimeoutError:
        print("Operation timed out. Please check your internet connection and retry.")

    client.stop()

if __name__ == "__main__":
    main()
