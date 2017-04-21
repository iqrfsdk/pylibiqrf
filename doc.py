import argparse
import os.path
import subprocess
import sys
import webbrowser

try:
    import iqrf
except ImportError:
    iqrf = None

try:
    import sphinx
except ImportError:
    sphinx = None

try:
    import sphinx_rtd_theme
except ImportError:
    sphinx_rtd_theme = None

INDEX_FILE = os.path.realpath("./docs/build/html/index.html")

ARGS = argparse.ArgumentParser(description="Documentation utility.")
ARGS.add_argument("action", action="store", choices=["generate", "view"], type=str, help="The action to be performed.")


def execute(command):
    args = command.split()
    process = subprocess.Popen(args, stdout=subprocess.PIPE)
    for line in iter(process.stdout.readline, b""):
        sys.stdout.write(line.decode())
    process.stdout.close()
    return process.wait()


def main():
    args = ARGS.parse_args()
    action = args.action

    if action == "generate":
        if iqrf is None:
            print("The module must be installed first!")
            print("Please run 'python setup.py install' to install the module.")
            return

        if sphinx is None:
            print("To generate the documentation, Sphinx is required!")
            print("Please install the 'sphinx' Python package.")
            return

        if sphinx_rtd_theme is None:
            print("The documentation requires Sphinx RTD theme to continue!")
            print("Please install the 'sphinx_rtd_theme' Python package.")
            return

        if sys.platform == "win32":
            exit_code = execute("cmd /C cd /D .\\docs && del /F /Q .\\build && make.bat html")
        else:
            exit_code = execute("make -C ./docs clean html")

        sys.exit(exit_code)

    elif action == "view":
        if not os.path.isfile(INDEX_FILE):
            print("File '" + INDEX_FILE + "' doesn't exist or is not a file.")
            print("You have to generate the documentation first.")
            print("Please run 'python doc.py generate'.")
            return

        webbrowser.open("file://" + INDEX_FILE)

if __name__ == "__main__":
    main()
