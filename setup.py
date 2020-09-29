# -*- coding: utf-8 -*-
# @Time   : 2020-09-29 4:31 PM
# @Author : Zhiyi Lu
# @Email  : zhiyilv@outlook.com
# @File   : setup.py
# @Desc   : to install lutar


import setuptools
import io
import os


# Package meta-data.
NAME = "lutar"
DESCRIPTION = "Lu's Useful Technical Analysis Repository"
URL = "https://github.com/zhiyilv/lutar"
EMAIL = "zhiyilv@outlook.com"
AUTHOR = "Zhiyi Lu"
REQUIRES_PYTHON = ">=3.6.0"
VERSION = "0.1"

PACKAGES = setuptools.find_packages()
PACKAGES_DATA = {}

# What packages are required for this module to be executed?
REQUIRED = ["pandas", "joblib"]

# What packages are optional?
EXTRAS = {"serializing": [], "database": []}

CLASSIFIERS = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Operating System :: OS Independent",
    "Development Status :: 2 - Pre-Alpha",
]

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

setuptools.setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=PACKAGES,
    install_requires=REQUIRED,
    zip_safe=False,
    package_data=PACKAGES_DATA,
)
