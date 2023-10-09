# myHand.ai

"myHand" is AI assistant, powered by ChatGPT, that can both chat and run tasks on local devices.

<img width="1204" alt="myHand_screenshot" src="https://github.com/eliranwong/myHand.ai/assets/25262722/ccfcfa11-b13d-4870-9c4c-8167526342b2">

Though myHand is built on ChatGPT, myHand goes beyond being a mere ChatGPT assistant by embodying the essence of "Actions speak louder than words." Unlike standard ChatGPT, myHand not only engages in conversational interactions but also actively performs tasks on behalf of users, demonstrating its commitment to practical action and tangible results.

Repository: https://github.com/eliranwong/myHand.ai

Developed by: [Eliran Wong](https://github.com/eliranwong)

# Requirements

1. Internet access

2. Windows / macOS / Linux / ChromeOS / Android / iOS / any devices that supports [Python](https://www.python.org)

3. ChatGPT API key (read https://github.com/eliranwong/myHand.ai/wiki/ChatGPT-API-Key)

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

Read more at https://github.com/eliranwong/myHand.ai/wiki/Features

# Highlight - Command Execution

myHand.ai goes beyond just being a chatbot by offering a unique and powerful capability - the ability to execute commands and perform computing tasks on your behalf. Unlike a mere chatbot, myHand.ai can interact with your computer system and carry out specific commands to accomplish various computing tasks. This feature allows you to leverage the expertise and efficiency of myHand.ai to automate processes, streamline workflows, and perform complex tasks with ease. However, it is essential to remember that with great power comes great responsibility, and users should exercise caution and use this feature at their own risk.

Command execution helps:

1. to get the requested information, e.g.

> tell me the current time

2. to execute computing tasks on local device, e.g.

> go to my Desktop

> list all files with names started with "Screenshot"

> delete them

3. to interact with third-party applications, e.g.

> open "my_music.mp3" with VLC player

> open Safari and search for "ChatGPT"

4. to interact with os assistant, e.g.

> open Siri

[Enhanced Mode](https://github.com/eliranwong/myHand.ai/wiki/Command-Execution#two-command-execution-mode)

[Disclaimer](https://github.com/eliranwong/myHand.ai/wiki/Command-Execution#disclaimer)

[Confirmation Prompt Options for Command Execution](https://github.com/eliranwong/myHand.ai/wiki/Command-Execution#confirmation-prompt-options-for-command-execution)

Read more at https://github.com/eliranwong/myHand.ai/wiki/Command-Execution

# Comparison with ChatGPT

myHand offers advanced features beyond standard ChatGPT, including task execution on local devices and real-time access to the internet.

Read https://github.com/eliranwong/myHand.ai/wiki/Compare-with-ChatGPT

# Comparison with ShellGPT

[ShellGPT](https://github.com/TheR1D/shell_gpt) only supports platform that run shell command-prompt.  Therefore, ShellGPT does not support Windows.

In most cases, myHand.ai run Python codes for task execution. This makes myHand.ai terms of platforms, myHand.ai was developed and tested on Windows, macOS, Linux, ChromeOS and Termux (Android).

In addition, myHand.ai offers more options for risk managements:

https://github.com/eliranwong/myHand.ai/wiki/Command-Execution#confirmation-prompt-options-for-command-execution

# Comparison with Siri and Others

Unlike popular options such as Siri (macOS, iOS), Cortana (Windows), and Google Assistant (Android), myHand offers enhanced power, customization, flexibility, and compatibility.

Read https://github.com/eliranwong/myHand.ai/wiki/Features

# Mobile Support

myHand.ai is also tested on [Termux](https://termux.dev/en/). myHand.ai also integrates [Termux:API](https://wiki.termux.com/wiki/Termux:API) for task execution.

For examples, users can run on Android:

> open Google Chrome and perform a search for "ChatGPT"

> share text "Hello World!" on Android

Read more at: https://github.com/eliranwong/myHand.ai/wiki/Android-Support

# Documentation

Read https://github.com/eliranwong/myHand.ai/wiki

# Setup or Installation

> git clone https://github.com/eliranwong/myHand.ai.git

> cd myHand.ai

## macOS or Linux Users

> python3 -m venv venv

> source venv/bin/activate

> pip3 install -r requirements.txt

> python3 myHand.py

## Windows Users

Double-click the file "setup.bat"

# Quick Start

Double-click desktop shortcut, which is created on first run.

Alternately, run in terminal:

> cd myHand.ai

> source venv/bin/activate

> python3 myHand.py

# Quick Operations

* Enter "..." for options

* Enter "" (blank entry) to change context quickly

* Enter ".quit" to quit

# Update

myHand.ai updates to the latest code on startup, by running:

> git pull
