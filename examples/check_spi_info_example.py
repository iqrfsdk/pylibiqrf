import argparse

from iqrf.transport import spi

ARGS = argparse.ArgumentParser(description="IQRF SPI communication example.")
ARGS.add_argument("-p", "--port", action="store", dest="port", required=True, type=str, help="The port name to connect to.")

def main():
    args = ARGS.parse_args()
    port = args.port
    device = None

    try:
        device = spi.open(port)

        print("Requesting module info...")

        info = device.send(spi.TrInfoRequest(), timeout=5)

        print("The module responded with {}".format(info.data))

    except Exception as error:
        print("An error occured:", type(error), error)
        raise error
    finally:
        if device is not None:
            device.close()

if __name__ == "__main__":
    main()
