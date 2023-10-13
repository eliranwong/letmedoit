# set up config
import os
# go the project home directory
myHandFile = os.path.realpath(__file__)
myHandAIFolder = os.path.dirname(myHandFile)
if os.getcwd() != myHandAIFolder:
    os.chdir(myHandAIFolder)
# create config.py if it does not exist
configFile = os.path.join(myHandAIFolder, "config.py")
if not os.path.isfile(configFile):
    open(configFile, "a", encoding="utf-8").close()
# import config and setup default 
import config
from utils.configDefault import *
config.myHandFile = myHandFile
config.myHandAIFolder = myHandAIFolder

# set up shortcuts
from utils.shortcuts import *
# import other libraries
import platform
from utils.shortcuts import *
from utils.chats import MyHandAI
from utils.vlc_utils import VlcUtil
from prompt_toolkit.shortcuts import set_title, clear_title, clear
try:
    # hide pygame welcome message
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    import pygame
    pygame.mixer.init()
    config.isPygameInstalled = True
except:
    config.isPygameInstalled = False

if __name__ == '__main__':

    def setOsOpenCmd():
        config.thisPlatform = thisPlatform = platform.system()
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
                    "chatGPTTransformers", # used with plugins; transform ChatGPT response message
                    "predefinedInstructions", # used with plugins; pre-defined instructions
                    "predefinedContexts", # used with plugins; pre-defined contexts
                    "inputSuggestions", # used with plugins; user input suggestions
                    "execute_python_code_signature",
                    "execute_termux_command_signature",
                    "integrate_google_searches_signature",
                    "chatGPTApiFunctionSignatures", # used with plugins; function calling
                    "chatGPTApiAvailableFunctions", # used with plugins; function calling
                    "pythonFunctionResponse", # used with plugins; function calling when function name is 'python'
                ]
                excludeConfigList = excludeConfigList + config.excludeConfigList
                if not name.startswith("__") and not name in excludeConfigList:
                    try:
                        value = eval(f"config.{name}")
                        fileObj.write("{0} = {1}\n".format(name, pprint.pformat(value)))
                    except:
                        pass

    def getLatestUpdate():
        try:
            os.system("git pull")
            clear()
            print("You are running the latest version.")
        except:
            print("Automatic update failed!")

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

    set_title("myHand.AI")
    getLatestUpdate()
    setOsOpenCmd()
    config.pipIsUpdated = False
    config.excludeConfigList = []
    config.isVlcPlayerInstalled = VlcUtil.isVlcPlayerInstalled()
    # check log files; remove old lines if more than 3000 lines is found in a log file
    for i in ("chats", "paths", "commands"):
        filepath = os.path.join(config.myHandAIFolder, "history", i)
        set_log_file_max_lines(filepath, 3000)
    myHand = MyHandAI()
    myHand.startChats()
    aboutToQuit()
    clear_title()
