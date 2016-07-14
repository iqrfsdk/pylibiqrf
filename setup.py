from setuptools import setup

with open("readme.md") as stream:
    long_description = stream.read()

setup(
    name="pylibiqrf",
    description="Python application programming interface for interacting with the IQRF ecosystem.",
    version="0.0.1",
    author="Tomáš Rottenberg",
    author_email="frzerostbite@gmail.com",
    url="https://github.com/iqrfsdk/pylibiqrf",
    package_dir={"": "src"},
    packages=["iqrf", "iqrf.cdc"],
    license="Apache 2",
    long_description=long_description,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache 2 License",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Topic :: Communications",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        "pyserial >= 3.1.1"
    ]
)
