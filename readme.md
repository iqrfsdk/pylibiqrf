<p align="center">
    <img src="https://raw.githubusercontent.com/iqrfsdk/pylibiqrf/master/artwork/logo.png">
</p>

<p align="center">
    <a href="https://travis-ci.org/iqrfsdk/pylibiqrf">
        <img src="https://travis-ci.org/iqrfsdk/pylibiqrf.svg?branch=master">
    </a>
    <a href="https://github.com/iqrfsdk/pylibiqrf/blob/master/license.txt">
      <img src="https://img.shields.io/:license-apache2-blue.svg">
    </a>
</p>

Python application programming interface for interacting with the IQRF
ecosystem.

## Installation

To install pylibiqrf, type:

```
$ python setup.py install
```

This will install the latest version of pylibiqrf alongside with its dependencies.
Please note that pylibiqrf requires Python version 3.5 or later.

## Documentation

pylibiqrf uses Sphinx to generate its documentation. If you wish to generate and
view it, install Sphinx and Sphinx RTD theme. You can do this by typing:

```
$ pip install sphinx
$ pip install sphinx_rtd_theme
```

After that you can generate the documentation using our documentation utility
by running:

```
$ python doc.py generate
```

And finally to view the documentation:

```
$ python doc.py view
```
