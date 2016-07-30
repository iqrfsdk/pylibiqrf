import subprocess
import sys

try:
    import pylint
except ImportError:
    pylint = None

def execute(command):
    args = command.split()
    process = subprocess.Popen(args, stdout=subprocess.PIPE)
    for line in iter(process.stdout.readline, b""):
        sys.stdout.write(line.decode())
    process.stdout.close()
    return process.wait()

def main():
    if pylint is None:
        print("To use the lint script, 'pylint' module must be installed!")
        print("Please run 'pip install pylint' to install the module.")
        return

    execute("pylint src/iqrf")

if __name__ == "__main__":
    main()
