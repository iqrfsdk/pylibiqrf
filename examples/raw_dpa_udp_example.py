import argparse
import time

from iqrf.transport import udp

ARGS = argparse.ArgumentParser(description="Raw IQRF DPA UDP communication example.")
ARGS.add_argument("-H", "--host", action="store", dest="host", required=True, type=str, help="The hostname of the remote UDP gateway.")
ARGS.add_argument("-p", "--port", action="store", dest="port", required=True, type=int, help="The UDP port to communicate over.")

def main():
    args = ARGS.parse_args()
    host = args.host
    port = args.port

    device = None

    first_node_ledg_on = bytes([0x22, 0x3, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x6, 0x1, 0x0, 0x7, 0x1, 0xff, 0xff, 0xc2, 0xf9])
    first_node_ledg_off = bytes([0x22, 0x3, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x6, 0x1, 0x0, 0x7, 0x0, 0xff, 0xff, 0xf5, 0xc9])

    try:
        device = udp.open(host, port)

        send = device.send(first_node_ledg_on)

        confirmation = device.receive(timeout=5)
        print("Confirmation:", confirmation)

        response = device.receive(timeout=5)
        print("Response:", response)

        print("The first bonded node's green LED was turned on.")

        time.sleep(3)

        print("Requesting the first bonded node to turn its green LED off.")
        send = device.send(first_node_ledg_off)

        confirmation = device.receive(timeout=5)
        print("Confirmation:", confirmation)

        response = device.receive(timeout=5)
        print("Response:", response)

        print("The first bonded node's green LED was turned off.")

    except Exception as error:
        print("An error occured:", type(error), error)
        raise error
    finally:
        if device is not None:
            device.close()

if __name__ == "__main__":
    main()
