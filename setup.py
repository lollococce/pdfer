# -*- coding: utf-8 -*-
#
# Copyright (C) 2008-2021 Lorenzo Coacci
#
# pylint: disable=logging-format-interpolation,too-many-lines
# import submodules you want to install

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name="pdfer",
    version="0.1.6",
    author="Lorenzo Coacci",
    author_email="lorenzo@coacci.it",
    description="The package will help you manage and parse PDFs to text with OCR and not.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/lollococce/pdfer",
    keywords=['pdf', 'parsing', 'extract', 'ocr'],
    license=license,
    include_package_data=True,
    install_requires=[
        # default libraries
        'sphinx',
        'pytest',
        'twine',
        'sphinx_rtd_theme',
        # monitoring logging etc
        'golog',
        # pdf libraries
        'PyPDF2',
        'tabula-py',
        # OCR
        'pdf2image',
        'pytesseract',
        'opencv-python',
        'pyocr'
    ],
    packages=find_packages(exclude=('tests', 'docs')),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
    ]
)
