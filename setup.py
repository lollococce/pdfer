# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name="pdfer",
    version="0.1.0",
    author="Lorenzo Coacci",
    author_email="lorenzo@coacci.it",
    description="The package will help you parse PDFs to data.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/lollococce/pdfer",
    keywords=['pdf', 'parsing', 'extract'],
    license=license,
    include_package_data=True,
    install_requires=[
        'sphinx',
        'pytest',
        'twine',
        'sphinx_rtd_theme',
        'sphinx',
        'golog',
        'PyPDF2'
    ],
    packages=find_packages(exclude=('tests', 'docs')),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
    ]
)
