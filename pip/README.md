# MyHand

"myHand" is AI assistant, powered by ChatGPT, that can both chat and run tasks on local devices.

## Watch this Video! MyHand Bot introduces itself!

[![Watch the video](https://img.youtube.com/vi/Dfsl-Cxx0bQ/maxresdefault.jpg)](https://youtu.be/Dfsl-Cxx0bQ)

Though myHand is built on ChatGPT, myHand goes beyond being a mere ChatGPT assistant by embodying the essence of "Actions speak louder than words." Unlike standard ChatGPT, myHand not only engages in conversational interactions but also actively performs tasks on behalf of users, demonstrating its commitment to practical action and tangible results.

Repository: https://github.com/eliranwong/myhand

Developed by: [Eliran Wong](https://github.com/eliranwong)

# Requirements

1. Internet access

2. Windows / macOS / Linux / ChromeOS / Android / iOS with [Python](https://www.python.org) versions 3.8-3.11; read [Install a Supported Python Version](https://github.com/eliranwong/myhand/wiki/Install-a-Supported-Python-Version)

3. ChatGPT API key (read https://github.com/eliranwong/myhand/wiki/ChatGPT-API-Key)

# Recent Additions

[Plugin - anaylze images](https://github.com/eliranwong/myhand/wiki/Plugins-%E2%80%90-Analyze-Images)

![analyze_image_demo](https://github.com/eliranwong/myhand/assets/25262722/e8767d02-bcc7-47f7-8169-29a0325e9ef9)

[Plugin - anaylze files](https://github.com/eliranwong/myhand/wiki/Plugins-%E2%80%90-Analyze-Files)

![integration_autogen_retriever](https://github.com/eliranwong/myhand/assets/25262722/0e31735c-5126-41ac-881c-eb8abce2aace)

# Documentation

Read https://github.com/eliranwong/myhand/wiki

# Install

## Install with pip

> pip install myhand

> myhand

## Install with pip and venv (recommended)

> python3 -m venv myhand

> source myhand/bin/activate

> pip install myhand

> myhand

# Quick Quide

https://github.com/eliranwong/myhand/wiki/Quick-Guide

# Upgrade with pip

> pip install --upgrade myhand

# Features

myHand is an advanced AI assistant that brings a wide range of powerful features to enhance your virtual assistance experience. Here are some key features of myHand:

* Open source

* Cross-Platform Compatibility

* Access to Real-time Internet Information

* Versatile Task Execution

* Harnessing the Power of Python

* Customizable and Extensible

* Seamless Integration with Other Virtual Assistants

* Natural Language Support

Read more at https://github.com/eliranwong/myhand/wiki/Features

# Highlight - Plugins

Developers can write their own plugins to add functionalities or to run customised tasks with MyHand

Read more at https://github.com/eliranwong/myhand/wiki/Plugins-%E2%80%90-Overview

Check our built-in plugins at: https://github.com/eliranwong/myhand/tree/main/plugins

# Highlight - Command Execution

Latest: MyHand Bot is now equipped with an [auto-healing feature for Python code](https://github.com/eliranwong/myhand/wiki/Python-Code-Auto%E2%80%90heal-Feature).

MyHand goes beyond just being a chatbot by offering a unique and powerful capability - the ability to execute commands and perform computing tasks on your behalf. Unlike a mere chatbot, MyHand can interact with your computer system and carry out specific commands to accomplish various computing tasks. This feature allows you to leverage the expertise and efficiency of MyHand to automate processes, streamline workflows, and perform complex tasks with ease. However, it is essential to remember that with great power comes great responsibility, and users should exercise caution and use this feature at their own risk.

Command execution helps:

1. to get the requested information, e.g.

> tell me the current time

2. to execute computing tasks on local device, e.g.

> go to my Desktop

> list all files with names started with "Screenshot"

> delete them

> convert music.wav into music.mp3

3. to interact with third-party applications, e.g.

> open "my_music.mp3" with VLC player

> open Safari and search for "ChatGPT"

4. to interact with os assistant, e.g.

> open Siri

[Enhanced Mode](https://github.com/eliranwong/myhand/wiki/Command-Execution#two-command-execution-mode)

## Tips! Quick Swap between "Enhanced" and "Auto" Modes

You can use keyboard shortcuts, "ctrl + e", to quickly swap between the "enhanced" and the "auto modes.

[Disclaimer](https://github.com/eliranwong/myhand/wiki/Command-Execution#disclaimer)

[Confirmation Prompt Options for Command Execution](https://github.com/eliranwong/myhand/wiki/Command-Execution#confirmation-prompt-options-for-command-execution)

Read more at https://github.com/eliranwong/myhand/wiki/Command-Execution

# Comparison with ChatGPT

myHand offers advanced features beyond standard ChatGPT, including task execution on local devices and real-time access to the internet.

Read https://github.com/eliranwong/myhand/wiki/Compare-with-ChatGPT

# Comparison with ShellGPT

[ShellGPT](https://github.com/TheR1D/shell_gpt) only supports platform that run shell command-prompt.  Therefore, ShellGPT does not support Windows.

In most cases, MyHand run Python codes for task execution. This makes MyHand terms of platforms, MyHand was developed and tested on Windows, macOS, Linux, ChromeOS and Termux (Android).

In addition, MyHand offers more options for risk managements:

https://github.com/eliranwong/myhand/wiki/Command-Execution#confirmation-prompt-options-for-command-execution

# Comparison with Open Interpreter

Both MyHand Bot and the [Open Interpreter](https://github.com/KillianLucas/open-interpreter) have the ability to execute code on a local device to accomplish specific tasks. Both platforms employ the same principle for code execution, which involves using ChatGPT function calls along with the Python exec() function.

However, MyHand Bot offers additional advantages, particularly in terms of [customization and extensibility through the use of plugins](https://github.com/eliranwong/myhand/wiki/Plugins-%E2%80%90-Overview). These plugins allow users to tailor MyHand Bot to their specific needs and enhance its functionality beyond basic code execution.

One key advantage of MyHand Bot is the seamless integration with the Open Interpreter. You can conveniently launch the Open Interpreter directly from MyHand Bot by running the command "!interpreter" [[read more](https://github.com/eliranwong/myhand/assets/25262722/4233b3c8-364e-466b-8218-c2dca7c134e5)]. This integration eliminates the need to choose between the two platforms; you can utilize both simultaneously.

Additionally, myHand integrates [AutoGen Assistant and Retriever](https://github.com/eliranwong/myhand/wiki/Integration-with-AutoGen), making it convenient to have all these powerful tools in one place.

# Comparison with Siri and Others

Unlike popular options such as Siri (macOS, iOS), Cortana (Windows), and Google Assistant (Android), myHand offers enhanced power, customization, flexibility, and compatibility.

Read https://github.com/eliranwong/myhand/wiki/Features

# Integrateion with AutoGen and Open Interpreter

[Integration with AutoGen](https://github.com/eliranwong/myhand/wiki/Integration-with-AutoGen)

[Launch Open Interpreter from MyHand Bot](https://github.com/eliranwong/myhand/wiki/Integration-with-Open-Interpreter)

![integrate_autogen_retriever_1](https://github.com/eliranwong/myhand/assets/25262722/9ab39e40-d51e-44d4-9266-eba1dd3b5f97)

# Mobile Support

MyHand is also tested on [Termux](https://termux.dev/en/). MyHand also integrates [Termux:API](https://wiki.termux.com/wiki/Termux:API) for task execution.

For examples, users can run on Android:

> open Google Chrome and perform a search for "ChatGPT"

> share text "Hello World!" on Android

Read more at: https://github.com/eliranwong/myhand/wiki/Android-Support
