import os, sys, platform
from shutil import copyfile

# requires python 3.8+; required by package 'tiktoken'
pythonVersion = sys.version_info
if pythonVersion < (3, 8):
    print("Python version higher than 3.8 is required!")
    print("Closing ...")
    exit(1)
elif pythonVersion >= (3, 12):
    print("Some features may not work with python version newer than 3.11!")

# navigate to project directory
myHandFile = os.path.realpath(__file__)
myHandAIFolder = os.path.dirname(myHandFile)
if os.getcwd() != myHandAIFolder:
    os.chdir(myHandAIFolder)

# check current platform
thisPlatform = platform.system()

# the following code block is not for pip installation
## Activate virtual environment, if any
#venvDir = "venv"
#venvDirFullPath = os.path.join(myHandAIFolder, venvDir)
#if os.path.isdir(venvDirFullPath) and not sys.executable.startswith(venvDirFullPath):
#    try:
#        python = os.path.basename(sys.executable)
#        binDir = "Scripts" if thisPlatform == "Windows" else "bin"
#        if thisPlatform == "Windows":
#            if python.endswith(".exe"):
#                python = python[:-4]
#            # Activate virtual environment
#            activator = os.path.join(venvDirFullPath, binDir, "activate")
#            # Run main.py
#            os.system(f"{activator} & {python} {myHandFile}")
#        else:
#            # Activate virtual environment
#            activator = os.path.join(venvDirFullPath, binDir, "activate_this.py")
#            if not os.path.exists(activator):
#                copyfile("activate_this.py", activator)
#            with open(activator) as f:
#                code = compile(f.read(), activator, 'exec')
#                exec(code, dict(__file__=activator))
#            # Run main.py
#            os.system(f"{python} {myHandFile}")
#        venvActivated = True
#    except:
#        venvActivated = False
#    if venvActivated:
#        # exit non-venv process
#        exit(0)

# set up config
# create config.py if it does not exist
configFile = os.path.join(myHandAIFolder, "config.py")
if not os.path.isfile(configFile):
    open(configFile, "a", encoding="utf-8").close()

# import config and setup default
import traceback
from myhand import config
from myhand.utils.configDefault import *
config.myHandFile = myHandFile
config.myHandAIFolder = myHandAIFolder

# automatic update
config.pipIsUpdated = False
#if config.autoUpdate:
#    # update to the latest codes
#    try:
#        os.system("git pull")
#        print("You are running the latest version.")
#    except:
#        print(traceback.format_exc() if config.developer else "Error encountered!")
#    # upgrade python packages
#    from myhand.utils.install import *
#    with open("requirements.txt", "r") as fileObj:
#        for line in fileObj.readlines():
#            mod = line.strip()
#            if mod:
#                installmodule(f"--upgrade {mod}")

# import other libraries
from myhand.utils.shortcuts import *
from myhand.utils.assistant import MyHandAI
from myhand.utils.vlc_utils import VlcUtil
from prompt_toolkit.shortcuts import set_title, clear_title, clear
try:
    # hide pygame welcome message
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    import pygame
    pygame.mixer.init()
    config.isPygameInstalled = True
except:
    config.isPygameInstalled = False

def setOsOpenCmd():
    config.thisPlatform = thisPlatform
    if config.terminalEnableTermuxAPI:
        config.open = "termux-share"
    elif thisPlatform == "Linux":
        config.open = "xdg-open"
    elif thisPlatform == "Darwin":
        config.open = "open"
    elif thisPlatform == "Windows":
        config.open = "start"
    # name macOS
    if config.thisPlatform == "Darwin":
        config.thisPlatform = "macOS"

def aboutToQuit():
    with open(configFile, "w", encoding="utf-8") as fileObj:
        for name in dir(config):
            excludeConfigList = [
                "aliases",
                "addPathAt",
                "multilineInput",
                "conversationStarted",
                "dynamicToolBarText",
                "tokenLimits",
                "currentMessages",
                "pagerContent",
                "selectAll",
                "clipboard",
                "showKeyBindings",
                "divider",
                "systemCommandPromptEntry",
                "stop_event",
                "spinner_thread",
                "tts",
                "isPygameInstalled",
                "isVlcPlayerInstalled",
                "accept_default",
                "defaultEntry",
                "pipIsUpdated",
                "setConfig",
                "excludeConfigList",
                "tempContent",
                "tempChunk",
                "chatGPTApiPredefinedContextTemp",
                "thisPlatform",
                "myHandAI",
                "terminalColors",
                "myHandFile",
                "myHandAIFolder",
                "open",
                "inputSuggestions", # used with plugins; user input suggestions
                "chatGPTTransformers", # used with plugins; transform ChatGPT response message
                "predefinedInstructions", # used with plugins; pre-defined instructions
                "predefinedContexts", # used with plugins; pre-defined contexts
                # used with plugins; function call
                "execute_python_code_signature",
                "execute_termux_command_signature",
                "integrate_google_searches_signature",
                "heal_python_signature",
                "chatGPTApiFunctionSignatures",
                "chatGPTApiAvailableFunctions",
                "pythonFunctionResponse", # used with plugins; function call when function name is 'python'
                # MyHandAI methods shared from Class MyHandAI
                "getFiles",
                "stopSpinning",
                "toggleMultiline",
                "print",
                "getWrappedHTMLText",
                "fineTuneUserInput",
                "launchPager",
                "addPagerText",
                "getFunctionMessageAndResponse",
            ]
            excludeConfigList = excludeConfigList + config.excludeConfigList
            if not name.startswith("__") and not name in excludeConfigList:
                try:
                    value = eval(f"config.{name}")
                    fileObj.write("{0} = {1}\n".format(name, pprint.pformat(value)))
                except:
                    pass

def set_log_file_max_lines(log_file, max_lines):
    if os.path.isfile(log_file):
        # Read the contents of the log file
        with open(log_file, "r", encoding="utf-8") as fileObj:
            lines = fileObj.readlines()
        # Count the number of lines in the file
        num_lines = len(lines)
        if num_lines > max_lines:
            # Calculate the number of lines to be deleted
            num_lines_to_delete = num_lines - max_lines
            if num_lines_to_delete > 0:
                # Open the log file in write mode and truncate it
                with open(log_file, "w", encoding="utf-8") as fileObj:
                    # Write the remaining lines back to the log file
                    fileObj.writelines(lines[num_lines_to_delete:])
            filename = os.path.basename(log_file)
            print(f"{num_lines_to_delete} old lines deleted from log file '{filename}'.")

def main():
    set_title("My Hand Bot")
    setOsOpenCmd()
    createShortcuts()
    config.excludeConfigList = []
    config.isVlcPlayerInstalled = VlcUtil.isVlcPlayerInstalled()
    # check log files; remove old lines if more than 3000 lines is found in a log file
    for i in ("chats", "paths", "commands"):
        filepath = os.path.join(config.myHandAIFolder, "history", i)
        set_log_file_max_lines(filepath, 3000)
    MyHandAI().startChats()
    aboutToQuit()
    clear_title()

if __name__ == "__main__":
    main()
