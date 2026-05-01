import setuptools
from setuptools import setup

setup(
    name="PythonBasicTools",
    long_description="file: README.md",
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
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
