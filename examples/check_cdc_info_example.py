import argparse

from iqrf.transport import cdc

ARGS = argparse.ArgumentParser(description="IQRF USB CDC communication example.")
ARGS.add_argument("-p", "--port", action="store", dest="port", required=True, type=str, help="The port name to connect to.")

def main():
    args = ARGS.parse_args()
    port = args.port
    device = None

    try:
        device = cdc.open(port)
        test = device.send(cdc.TestRequest(), timeout=5)

        if test.status == cdc.CdcStatus.OK:
            print("Indicating the device...")
            device.send(cdc.IndicationRequest())

            print("Requesting device info...")

            info = device.send(cdc.InfoRequest())

            print("Communicating with {} v{}.".format(info.type, info.version))
            print("The internal ID of this device is: {}.".format(info.id))
        else:
            print("Test request failed!")

    except Exception as error:
        print("An error occured:", type(error), error)
    finally:
        if device is not None:
            device.close()

if __name__ == "__main__":
    main()
