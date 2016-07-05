import unittest

TEST_DIRECTORIES = ["test/cdc"]

def main():
    for directory in TEST_DIRECTORIES:
        tests = unittest.TestLoader().discover(directory, pattern="*_test.py")
        print(unittest.TextTestRunner().run(tests))

if __name__ == "__main__":
    main()
