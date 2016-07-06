"""A simple USB CDC communication test example.

Usage:
    * python cdc_test_example.py --help
    * python cdc_test_example.py -p COM5
    * python cdc_test_example.py --port /dev/ttyACM0

If you don't know the name of the serial port you want to connect,
you can use following.

    python -m serial.tools.list_ports

This command will run serial port detector and return all available serial
ports.

"""

import argparse
import iqrf.cdc

ARGS = argparse.ArgumentParser(description="IQRF USB CDC communication test.")
ARGS.add_argument("-p", "--port", action="store", dest="port", required=True, type=str, help="The port name to connect to.")

def main():
    args = ARGS.parse_args()

    port = args.port

    try:
        print("Connecting to the IQRF device on '{}'.".format(port))
        device = iqrf.cdc.open(port)

        print("Requesting communication test.")
        device.write_cdc_message(iqrf.cdc.CdcMessage.TEST)

        response, _, _ = device.read_cdc_message()

        if response == iqrf.cdc.CdcMessage.TEST_RESPONSE:
            print("Communication test was successful!")
        else:
            print("An unexpected response received!")
    except Exception as e:
        print("An error occured:", e)

if __name__ == "__main__":
    main()
