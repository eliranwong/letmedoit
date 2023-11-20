from setuptools import setup, find_packages
import os

with open(os.path.join("myhand", "README.md"), "r", encoding="utf-8") as fileObj:
    long_description = fileObj.read()

# https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/
setup(
    name="myhand",
    version="1.0.9",
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
    url="https://github.com/eliranwong/myhand",
    license="GNU General Public License (GPL)",
    install_requires=[
        "requests",
        "openai==1.3.3",
        "prompt_toolkit",
        "Pygments",
        "datetime",
        "netifaces",
        "geocoder",
        "googlesearch-python",
        "art",
        "apsw",
        "gTTS",
        "google-cloud-texttospeech",
        "yt-dlp",
        "pyperclip",
        "colorama",
        "tiktoken",
        "docker",
        "unstructured[all-docs]",
        "pillow",
        "pyautogen[retrievechat,teachable,mathchat]==0.2.0b5",
        "chromadb",
        "pygame",
    ],
    entry_points={
        "console_scripts": [
            "myhand=myhand.cli:cli",
        ],
    },
    keywords="ai openai chatgpt rag autogen open interpreter auto-heal",
    project_urls={
        "Source": "https://github.com/eliranwong/myhand",
        "Tracker": "https://github.com/eliranwong/myhand/issues",
        "Documentation": "https://github.com/eliranwong/myhand/wiki",
        "Funding": "https://www.paypal.me/MarvelBible",
},
)
