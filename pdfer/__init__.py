#
# Copyright (C) 2008-2021 Lorenzo Coacci
#
# pylint: disable=logging-format-interpolation,too-many-lines
#

# import submodules you want to install
from .pdf import (
    PDF
)


__docformat__ = "restructuredtext"

__version__ = '0.1.0'

# module level doc-string
__doc__ = """
pdfer - a library to parse data from a PDF
==========================================

**pdfer** is a Python package providing many different useful functions

Main Features
-------------
Here are just a few of the things that pdfer does well:
  - Parse PDF to text
  - OCR from PDF to images to text
  - Handle PDF actions (copy, add page, rotate, etc)
"""
