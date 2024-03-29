from setuptools import setup
# from src import pythonbasictools
# from src.pythonbasictools import __author__, __url__, __email__, __version__, __license__
import setuptools

# with open("README.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()
#
# with open("requirements.txt", "r", encoding="utf-8") as fh:
#     install_requires = fh.readlines()

setup(
    name='PythonBasicTools',
    # version=__version__,
    # description=pythonbasictools.__doc__,
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    # url=__url__,
    # author=__author__,
    # author_email=__email__,
    # license=__license__,
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    # install_requires=install_requires,
)


# build library
#  setup.py sdist bdist_wheel
# With pyproject.toml
# python -m pip install --upgrade build
# python -m build

# publish on PyPI
#   twine check dist/*
#   twine upload --repository-url https://test.pypi.org/legacy/ dist/*
#   twine upload dist/*

