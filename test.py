import unittest
import sys

TEST_DIRECTORIES = [
    "test/cdc"
]

def main():

    exit_code = 0

    for directory in TEST_DIRECTORIES:
        tests = unittest.TestLoader().discover(directory, pattern="*_test.py")
        result = unittest.TextTestRunner().run(tests)

        if not result.wasSuccessful():
            exit_code = 1

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
