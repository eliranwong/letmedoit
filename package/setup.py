from setuptools import setup
import os, shutil

# package name
with open(os.path.join("taskwiz", "package_name.txt"), "r", encoding="utf-8") as fileObj:
    package = fileObj.read()

# delete old shortcut files
apps = {
    "myhand": ("MyHand", "MyHand Bot"),
    "taskwiz": ("TaskWiz", "TaskWiz AI"),
    "cybertask": ("CyberTask", "CyberTask AI"),
}
appName = apps[package][0]
shortcutFiles = (f"{appName}.bat", f"{appName}.command", f"{appName}.desktop")
for shortcutFile in shortcutFiles:
    shortcut = os.path.join("taskwiz", shortcutFile)
    if os.path.isfile(shortcut):
        os.remove(shortcut)

# update package readme
latest_readme = os.path.join("..", "README.md") # github repository readme
package_readme = os.path.join("taskwiz", "README.md") # package readme
shutil.copy(latest_readme, package_readme)
with open(package_readme, "r", encoding="utf-8") as fileObj:
    long_description = fileObj.read()

# get required packages
install_requires = []
with open(os.path.join("taskwiz", "requirements.txt"), "r") as fileObj:
    for line in fileObj.readlines():
        mod = line.strip()
        if mod:
            install_requires.append(mod)

# make sure config.py is empty
with open(os.path.join("taskwiz", "config.py"), "w") as fileObj:
    taskWizName = apps[package][-1]
    fileObj.write(f"taskWizName = '{taskWizName}'")

# https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/
setup(
    name=package,
    version="1.3.3",
    python_requires=">=3.8, <3.12",
    description="TaskWiz AI, an advanced AI assistant, leveraging the capabilities of ChatGPT API, capable of engaging in conversations, executing codes with auto-healing, and assisting you with a wide range of tasks.",
    long_description=long_description,
    author="Eliran Wong",
    author_email="support@taskwiz.ai",
    packages=[
        "taskwiz",
        "taskwiz.files",
        "taskwiz.history",
        "taskwiz.icons",
        "taskwiz.plugins",
        "taskwiz.plugins.bibleTools.",
        "taskwiz.plugins.bibleTools.bibleData.bibles",
        "taskwiz.plugins.bibleTools.bibleData.",
        "taskwiz.plugins.bibleTools.utils",
        "taskwiz.temp",
        "taskwiz.utils",
    ],
    package_data={
        "taskwiz": ["*.*"],
        "taskwiz.files": ["*.*"],
        "taskwiz.history": ["*.*"],
        "taskwiz.icons": ["*.*"],
        "taskwiz.plugins": ["*.*"],
        "taskwiz.plugins.bibleTools.": ["*.*"],
        "taskwiz.plugins.bibleTools.bibleData.bibles": ["*.*"],
        "taskwiz.plugins.bibleTools.bibleData.": ["*.*"],
        "taskwiz.plugins.bibleTools.utils": ["*.*"],
        "taskwiz.temp": ["*.*"],
        "taskwiz.utils": ["*.*"],
    },
    license="GNU General Public License (GPL)",
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            f"{package}=taskwiz.cli:cli",
        ],
    },
    keywords="ai assistant openai chatgpt rag autogen interpreter auto-heal",
    url="https://taskwiz.ai",
    project_urls={
        "Source": "https://github.com/eliranwong/taskwiz",
        "Tracker": "https://github.com/eliranwong/taskwiz/issues",
        "Documentation": "https://github.com/eliranwong/taskwiz/wiki",
        "Funding": "https://www.paypal.me/MarvelBible",
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
