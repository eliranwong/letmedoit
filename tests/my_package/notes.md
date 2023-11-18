To create a Python package with a CLI command, you can follow these steps:

1. **Project Structure:**
   Create a directory structure for your project. For example:
   ```
   my_package/
   ├── my_package/
   │   ├── __init__.py
   │   └── cli.py
   │   └── main.py
   ├── setup.py
   └── README.md
   ```

2. **Write Your Code:**
   Inside `main.py`, put your main program logic:
   ```python
   # main.py
   def main():
       print("Hello, world!")

   if __name__ == "__main__":
       main()
   ```

3. **Command Line Interface (CLI):**
   Create a new file named `cli.py` to handle the command line interface:
   ```python
   # my_package/cli.py
   from my_package.main import main

   def cli():
       main()

   if __name__ == "__main__":
       cli()
   ```

4. **Setup Script:**
   Create a `setup.py` file to define package metadata and dependencies:
   ```python
   # setup.py
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
   ```

5. **Install and Test Locally:**
   Install your package locally to test it:
   ```bash
   pip install -e .
   ```

6. **Distribution:**
   To distribute your package, you can create a source distribution or a wheel:
   ```bash
   python setup.py sdist bdist_wheel
   ```

7. **Upload to PyPI:**
   If you want others to easily install your package using `pip`, you can upload it to PyPI. Make sure you have an account on PyPI, then install and use `twine` for uploading:
   ```bash
   pip install twine
   twine upload dist/*
   ```

8. **Install and Run:**
   Users can then install your package and use the CLI command:
   ```bash
   pip install my-package
   hello
   ```

This structure and setup will work on both macOS and Windows. Users can run the `hello` command from the terminal after installing your package via `pip`.
