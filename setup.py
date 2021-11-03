from setuptools import setup
from src.pythonbasictools.version import __version__
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='PythonBasicTools',
    version=__version__,
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/JeremieGince/PythonBasicTools',
    author='Jérémie Gince',
    author_email='gincejeremie@gmail.com',
    license='Apache 2.0',
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "psutil>=5.8.0",
    ],
)


# build library
#  setup.py sdist bdist_wheel

# publish on PyPI
#   twine check dist/*
#   twine upload --repository-url https://test.pypi.org/legacy/ dist/*
#   twine upload dist/*

