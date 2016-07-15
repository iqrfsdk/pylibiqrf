import argparse

from iqrf import cdc
from time import sleep

ARGS = argparse.ArgumentParser(description="Raw IQRF DPA CDC communication example.")
ARGS.add_argument("-p", "--port", action="store", dest="port", required=True, type=str, help="The port name to connect to.")

def main():
    args = ARGS.parse_args()
    port = args.port
    device = None

    first_node_ledg_on = bytes([0x01, 0x00, 0x07, 0x01, 0xFF, 0xFF])
    first_node_ledg_off = bytes([0x01, 0x00, 0x07, 0x00, 0xFF, 0xFF])

    try:
        device = cdc.open(port)
        test = device.send(cdc.TestRequest(), timeout=5)

        if test.status == cdc.CdcStatus.OK:
            print("Requesting the first bonded node to turn its green LED on.")
            send = device.send(cdc.DataSendRequest(first_node_ledg_on))

            confirmation = device.receive(timeout=5)
            print("Confirmation:", confirmation.data)

            response = device.receive(timeout=5)
            print("Response:", response.data)

            print("The first bonded node's green LED was turned on.")

            sleep(3)

            print("Requesting the first bonded node to turn its green LED off.")
            send = device.send(cdc.DataSendRequest(first_node_ledg_off))

            confirmation = device.receive(timeout=5)
            print("Confirmation:", confirmation.data)

            response = device.receive(timeout=5)
            print("Response:", response.data)

            print("The first bonded node's green LED was turned off.")
        else:
            print("Test request failed!")

    except Exception as error:
        print("An error occured:", type(error), error)
    finally:
        if device is not None:
            device.close()

if __name__ == "__main__":
    main()
