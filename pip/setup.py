from setuptools import setup
import os, shutil

# update package readme
latest_readme = os.path.join("..", "README.md") # github repository readme
package_readme = os.path.join("myhand", "README.md") # package readme
shutil.copy(latest_readme, package_readme)
with open(package_readme, "r", encoding="utf-8") as fileObj:
    long_description = fileObj.read()

# get required packages
install_requires = []
with open(os.path.join("myhand", "requirements.txt"), "r") as fileObj:
    for line in fileObj.readlines():
        mod = line.strip()
        if mod:
            install_requires.append(mod)

# make sure config.py is empty
with open(os.path.join("myhand", "config.py"), 'w'):
    pass

# https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/
setup(
    name="myhand",
    version="1.1.8",
    python_requires=">=3.8, <3.12",
    description="An advanced AI assistant, leveraging the capabilities of ChatGPT API, capable of engaging in conversations, executing codes with auto-healing, and assisting you with a wide range of tasks.",
    long_description=long_description,
    author="Eliran Wong",
    author_email="support@myhand.bot",
    packages=[
        "myhand",
        "myhand.files",
        "myhand.history",
        "myhand.icons",
        "myhand.plugins",
        "myhand.plugins.bibleTools.",
        "myhand.plugins.bibleTools.bibleData.bibles",
        "myhand.plugins.bibleTools.bibleData.",
        "myhand.plugins.bibleTools.utils",
        "myhand.temp",
        "myhand.utils",
    ],
    package_data={
        "myhand": ["*.*"],
        "myhand.files": ["*.*"],
        "myhand.history": ["*.*"],
        "myhand.icons": ["*.*"],
        "myhand.plugins": ["*.*"],
        "myhand.plugins.bibleTools.": ["*.*"],
        "myhand.plugins.bibleTools.bibleData.bibles": ["*.*"],
        "myhand.plugins.bibleTools.bibleData.": ["*.*"],
        "myhand.plugins.bibleTools.utils": ["*.*"],
        "myhand.temp": ["*.*"],
        "myhand.utils": ["*.*"],
    },
    license="GNU General Public License (GPL)",
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "myhand=myhand.cli:cli",
        ],
    },
    keywords="ai openai chatgpt rag autogen open-interpreter auto-heal",
    url="https://myhand.bot",
    project_urls={
        "Source": "https://github.com/eliranwong/myhand",
        "Tracker": "https://github.com/eliranwong/myhand/issues",
        "Documentation": "https://github.com/eliranwong/myhand/wiki",
        "Funding": "https://www.paypal.me/MarvelBible",
},
)
