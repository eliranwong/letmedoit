# set up config
import os
if not os.path.isfile("config.py"):
    open("config.py", "a", encoding="utf-8").close()
import config
from utils.configDefault import *
# set up shortcuts
config.myHandFile = os.path.realpath(__file__)
from utils.shortcuts import *
# import other libraries
import platform, sys
from utils.shortcuts import *
from utils.chats import MyHandAI

if __name__ == '__main__':

    def setOsOpenCmd():
        thisPlatform = platform.system()
        if config.terminalEnableTermuxAPI:
            config.open = "termux-share"
        elif thisPlatform == "Linux":
            config.open = "xdg-open"
        elif thisPlatform == "Darwin":
            config.open = "open"
        elif thisPlatform == "Windows":
            config.open = "start"

    def aboutToQuit():
        with open("config.py", "w", encoding="utf-8") as fileObj:
            for name in dir(config):
                excludeFromSavingList = (
                    "myHandFile",
                    "cwd",
                    "open",
                    "chatGPTTransformers", # used with plugins; transform ChatGPT response message
                    "predefinedContexts", # used with plugins; pre-defined contexts
                    "inputSuggestions", # used with plugins; user input suggestions
                    "execute_python_code_signature",
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

    setOsOpenCmd()
    myHand = MyHandAI()
    myHand.startChats()
    aboutToQuit()

    # TODO
    # add keyboard shortcuts
    # format text output
    # improve wiki pages
    # documentation on how to create plugins
    # add help link
    # add dialog to enable / disable enhanced screening
    # add interface to customise temperature
    # add dialog to enable / disable individual plugins