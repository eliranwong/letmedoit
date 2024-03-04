import os
thisFile = os.path.realpath(__file__)
packageFolder = os.path.dirname(thisFile)
package = os.path.basename(packageFolder)
if os.getcwd() != packageFolder:
    os.chdir(packageFolder)

from letmedoit import config
config.isTermux = True if os.path.isdir("/data/data/com.termux/files/home") else False
config.letMeDoItAIFolder = packageFolder
apps = {
    "myhand": ("MyHand", "MyHand Bot"),
    "letmedoit": ("LetMeDoIt", "LetMeDoIt AI"),
    "taskwiz": ("TaskWiz", "TaskWiz AI"),
    "cybertask": ("CyberTask", "CyberTask AI"),
}
basename = os.path.basename(packageFolder)
if not hasattr(config, "letMeDoItName") or not config.letMeDoItName:
    config.letMeDoItName = apps[basename][-1] if basename in apps else "LetMeDoIt AI"
from letmedoit.utils.config_tools import setConfig
config.setConfig = setConfig
## alternative to include config restoration method
#from letmedoit.utils.config_tools import *
from letmedoit.utils.shared_utils import SharedUtil
config.includeIpInSystemMessageTemp = True
config.getLocalStorage = SharedUtil.getLocalStorage
config.print = config.print2 = config.print3 = print
config.addFunctionCall = SharedUtil.addFunctionCall
config.divider = "--------------------"
SharedUtil.setOsOpenCmd()

from PySide6.QtWidgets import QApplication, QInputDialog
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.formatted_text import PygmentsTokens
from pygments.lexers.python import PythonLexer
import json, argparse, sys


class JustDoIt:

    def __init__(self) -> None:
        SharedUtil.setAPIkey()
        SharedUtil.runPlugins()
        def stopSpinning():
            ...
        config.stopSpinning = stopSpinning

    def run(self, default="") -> None:
        QApplication(sys.argv)
        gui_title = "LetMeDoIt AI"
        about = "Enter your request:"
        def runGui(thisDefault) -> bool:
            dialog = QInputDialog()

            dialog.setInputMode(QInputDialog.TextInput)
            dialog.setWindowTitle(gui_title)
            dialog.setLabelText(about)
            dialog.setTextValue(thisDefault)

            # Set size of dialog here
            dialog.resize(500, 100)  # You can adjust the values according to your requirement

            if dialog.exec():
                request = dialog.textValue()
                self.resolve(request)
                return True
            else:
                return False
        if config.isTermux:
            if not default:
                print(gui_title)
                print(about)
                default = input(">>> ")
            self.resolve(default)
        else:
            while runGui(default):
                default = ""

    def resolve(self, request) -> str:
        messages=SharedUtil.resetMessages(prompt=request)
        completion = config.oai_client.chat.completions.create(
            model=config.chatGPTApiModel,
            messages=messages,
            n=1,
            temperature=config.llmTemperature,
            max_tokens=SharedUtil.getDynamicTokens(messages, config.chatGPTApiFunctionSignatures.values()),
            tools=SharedUtil.convertFunctionSignaturesIntoTools(config.chatGPTApiFunctionSignatures.values()),
            tool_choice="auto",
            #stream=True,
        )
        output = completion.choices[0].message
        if output.content:
            response = output.content
        elif output.tool_calls:
            for tool_call in output.tool_calls:
                tool = tool_call.function
                name, arguments = tool.name, tool.arguments
                response = config.chatGPTApiAvailableFunctions[name](json.loads(arguments))
        else:
            response = ""
        # ignore response for now
        return response

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description="justdoit cli options")
    # Add arguments
    parser.add_argument("default", nargs="?", default=None, help="default entry")
    # Parse arguments
    args = parser.parse_args()
    # Get options
    default = args.default.strip() if args.default and args.default.strip() else ""
    # gui
    JustDoIt().run(default)

if __name__ == '__main__':
    main()