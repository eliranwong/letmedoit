from setuptools import setup
import os, shutil

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
with open(os.path.join("taskwiz", "config.py"), 'w'):
    pass

# https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/
setup(
    name="taskwiz",
    version="1.1.9",
    python_requires=">=3.8, <3.12",
    description="TaskWiz AI, an advanced AI assistant, leveraging the capabilities of ChatGPT API, capable of engaging in conversations, executing codes with auto-healing, and assisting you with a wide range of tasks.",
    long_description=long_description,
    author="Eliran Wong",
    author_email="support@taskwiz.bot",
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
            "taskwiz=taskwiz.cli:cli",
        ],
    },
    keywords="ai openai chatgpt rag autogen open-interpreter auto-heal",
    url="https://taskwiz.ai",
    project_urls={
        "Source": "https://github.com/eliranwong/taskwiz",
        "Tracker": "https://github.com/eliranwong/taskwiz/issues",
        "Documentation": "https://github.com/eliranwong/taskwiz/wiki",
        "Funding": "https://www.paypal.me/MarvelBible",
},
)
