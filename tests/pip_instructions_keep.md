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
   pip install wheel
   python3 setup.py sdist bdist_wheel
   ```

7. Add API Tokens
Log in pypi account
Enable 2-factor-authentication 2FA
Add API Tokens

8. **Upload to PyPI:**
   If you want others to easily install your package using `pip`, you can upload it to PyPI. Make sure you have an account on PyPI, then install and use `twine` for uploading:
   ```bash
   pip install twine
   twine upload dist/*
   ```

[pypi]
  username = __token__
  password = ***********************************

9. **Install and Run:**
   Users can then install your package and use the CLI command:
   ```bash
   pip install my-package
   hello
   ```

This structure and setup will work on both macOS and Windows. Users can run the `hello` command from the terminal after installing your package via `pip`.

# To enable 2FA

To set up Two-Factor Authentication (2FA) with an authentication application for
your PyPI account, you will need to follow these general steps:

1. **Download an Authentication Application**: You will need a Time-based One
-Time Password (TOTP) application on your device. Common choices include Google 
Authenticator, Authy, or similar apps available in your device's app store.

2. **Log in to Your PyPI Account**: Access your PyPI account by logging in 
through the [PyPI website](https://pypi.org/).

3. **Access Account Settings**: Once logged in, navigate to your account 
settings.

4. **Add 2FA**: Look for an option that says "Add 2FA with authentication 
application" or similar. Select this option to begin the setup process.

5. **Scan QR Code**: The PyPI website will provide you with a QR code. Open your
authentication application and use it to scan this QR code. This will link your 
PyPI account with the authentication app.

6. **Enter the Generated Code**: After scanning the QR code, your authentication
app will generate a 6-digit code. Enter this code on the PyPI website to verify 
the setup.

7. **Complete the Setup**: Follow any additional prompts to complete the setup 
process. Make sure to save any backup codes provided during the setup in a 
secure location, as these can be used to access your account if your 
authentication device is unavailable.

For detailed instructions and help, you can refer to the [PyPI help page](https
://pypi.org/help/) or the [blog post about securing PyPI accounts with 2FA](
https://blog.pypi.org/posts/2023-05-25-securing-pypi-with-2fa/).

Please note that the exact steps may vary slightly depending on updates to the 
PyPI website or the authentication application you choose to use. Always follow 
the most current instructions provided by PyPI during the setup process.