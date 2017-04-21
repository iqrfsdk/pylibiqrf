import argparse
import time

from iqrf.transport import spi

ARGS = argparse.ArgumentParser(description="Raw IQRF DPA SPI communication example.")
ARGS.add_argument("-p", "--port", action="store", dest="port", required=True, type=str, help="The port name to connect to.")


def main():
    args = ARGS.parse_args()
    port = args.port
    device = None

    first_node_ledg_on = bytes([0x01, 0x00, 0x07, 0x01, 0xff, 0xff])
    first_node_ledg_off = bytes([0x01, 0x00, 0x07, 0x00, 0xff, 0xff])

    try:
        device = spi.open(port)

        send = device.send(spi.DataSendRequest(first_node_ledg_on), timeout=5)

        confirmation = device.receive(timeout=5)
        print("Confirmation:", confirmation.data)

        response = device.receive(timeout=5)
        print("Response:", response.data)

        print("The first bonded node's green LED was turned on.")

        time.sleep(3)

        print("Requesting the first bonded node to turn its green LED off.")
        send = device.send(spi.DataSendRequest(first_node_ledg_off), timeout=5)

        confirmation = device.receive(timeout=5)
        print("Confirmation:", confirmation.data)

        response = device.receive(timeout=5)
        print("Response:", response.data)

        print("The first bonded node's green LED was turned off.")

    except Exception as error:
        print("An error occured:", type(error), error)
        raise error
    finally:
        if device is not None:
            device.close()

if __name__ == "__main__":
    main()
