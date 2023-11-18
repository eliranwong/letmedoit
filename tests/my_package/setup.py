from setuptools import setup, find_packages

setup(
    name="my-package",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
    # List your dependencies here
    ],
    entry_points={
        "console_scripts": [
            "hello=my_package.cli:cli",
        ],
    },
)
