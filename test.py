import logging
import sys
import unittest

TEST_DIRECTORIES = [
    "tests/cdc"
]

def main():

    exit_code = 0
    # logging.basicConfig(level=logging.DEBUG)

    for directory in TEST_DIRECTORIES:
        tests = unittest.TestLoader().discover(directory, pattern="*_test.py")
        result = unittest.TextTestRunner().run(tests)

        if not result.wasSuccessful():
            exit_code = 1

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
