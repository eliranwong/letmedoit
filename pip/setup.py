from setuptools import setup, find_packages

# https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/
setup(
    name="myhand",
    version="1.0.0",
    python_requires=">=3.8, <3.12",
    description='MyHand Bot, your advanced AI assistant, capable of engaging in conversations, executing codes, and assisting you with a wide range of tasks.',
    author="Eliran Wong",
    author_email="support@myhand.bot",
    packages=find_packages(),
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
)
