from setuptools import setup
import os, shutil

# Notes: Steps to change package name
# 1. change folder name "letmedoit" to <pacakge_name>
# 2. edit package/package_name.txt and change its content to <pacakge_name>
# 3. search for "from letmedoit" and replace with "from <package_name>"

# package name
package_name_0 = os.path.join("package_name.txt")
with open(package_name_0, "r", encoding="utf-8") as fileObj:
    package = fileObj.read()
package_name_1 = os.path.join(package, "package_name.txt") # package readme
shutil.copy(package_name_0, package_name_1)

# delete old shortcut files
apps = {
    "myhand": ("MyHand", "MyHand Bot"),
    "letmedoit": ("LetMeDoIt", "LetMeDoIt AI"),
    "taskwiz": ("TaskWiz", "TaskWiz AI"),
    "cybertask": ("CyberTask", "CyberTask AI"),
}
appName, appFullName = apps[package]
shortcutFiles = (f"{appName}.bat", f"{appName}.command", f"{appName}.desktop")
for shortcutFile in shortcutFiles:
    shortcut = os.path.join(package, shortcutFile)
    if os.path.isfile(shortcut):
        os.remove(shortcut)

# update package readme
latest_readme = os.path.join("..", "README.md") # github repository readme
package_readme = os.path.join(package, "README.md") # package readme
shutil.copy(latest_readme, package_readme)
with open(package_readme, "r", encoding="utf-8") as fileObj:
    long_description = fileObj.read()

# get required packages
install_requires = []
with open(os.path.join(package, "requirements.txt"), "r") as fileObj:
    for line in fileObj.readlines():
        mod = line.strip()
        if mod:
            install_requires.append(mod)

# make sure config.py is empty
open(os.path.join(package, "config.py"), "w").close()

# https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/
setup(
    name=package,
    version="3.0.3",
    python_requires=">=3.8, <3.12",
    description=f"{appFullName}, an advanced AI assistant, leveraging the capabilities of AI models, to resolve daily tasks for you.",
    long_description=long_description,
    author="Eliran Wong",
    author_email="support@letmedoit.ai",
    packages=[
        package,
    ],
    package_data={
        package: ["*.*"],
    },
    license="GNU General Public License (GPL)",
    install_requires=install_requires,
    extras_require={
        'genai': ["google-genai>=1.1.0"],  # Dependencies for running Vertex AI
    },
    entry_points={
        "console_scripts": [
            f"{package}={package}.main:main",
            f"lmdi={package}.main:main",
            f"{package}lite={package}.main:lite",
            f"lmdil={package}.main:lite",
        ],
    },
    keywords="ai assistant openai chatgpt gemini autogen rag interpreter auto-heal",
    url="https://letmedoit.ai",
    project_urls={
        "Source": "https://github.com/eliranwong/letmedoit",
        "Tracker": "https://github.com/eliranwong/letmedoit/issues",
        "Documentation": "https://github.com/eliranwong/letmedoit/wiki",
        "Funding": "https://www.paypal.me/letmedoitai",
    },
    classifiers=[
        # Reference: https://pypi.org/classifiers/

        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Topic :: Utilities',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
