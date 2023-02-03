import pathlib

from setuptools import setup, find_packages

README = (pathlib.Path(__file__).parent / "README.md").read_text()

setup(
    name='anodot-simple-config',
    description="A library for working with application configuration",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/anodot/anodot-simple-config",
    author="Anodot",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    packages=find_packages(),
    include_package_data=True,
    version='1.0.0'
)
