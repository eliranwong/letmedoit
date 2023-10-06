# set up config
import os, traceback
if not os.path.isfile("config.py"):
    open("config.py", "a", encoding="utf-8").close()
import config
from utils.configDefault import *
# set up shortcuts
config.myHandFile = os.path.realpath(__file__)
from utils.shortcuts import *
# import other libraries
import platform
from utils.shortcuts import *
from utils.chats import MyHandAI

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
        with open("config.py", "w", encoding="utf-8") as fileObj:
            for name in dir(config):
                excludeFromSavingList = (
                    "runMode",
                    "tempContent",
                    "thisPlatform",
                    "myHandAI",
                    "terminalColors",
                    "myHandFile",
                    "myHandAIFolder",
                    "open",
                    "chatGPTTransformers", # used with plugins; transform ChatGPT response message
                    "predefinedContexts", # used with plugins; pre-defined contexts
                    "inputSuggestions", # used with plugins; user input suggestions
                    "execute_python_code_signature",
                    "execute_termux_command_signature",
                    "integrate_google_searches_signature",
                    "chatGPTApiFunctionSignatures", # used with plugins; function calling
                    "chatGPTApiAvailableFunctions", # used with plugins; function calling
                    "pythonFunctionResponse", # used with plugins; function calling when function name is 'python'
                )
                if not name.startswith("__") and not name in excludeFromSavingList:
                    try:
                        value = eval(f"config.{name}")
                        fileObj.write("{0} = {1}\n".format(name, pprint.pformat(value)))
                    except:
                        pass

    def getLatestUpdate():
        try:
            os.system("git pull")
        except:
            print("Failed to automatically update!")

    getLatestUpdate()
    setOsOpenCmd()
    myHand = MyHandAI()
    myHand.startChats()
    aboutToQuit()
