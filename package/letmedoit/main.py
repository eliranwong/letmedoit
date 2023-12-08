import os, sys, platform, shutil, argparse

# requires python 3.8+; required by package 'tiktoken'
pythonVersion = sys.version_info
if pythonVersion < (3, 8):
    print("Python version higher than 3.8 is required!")
    print("Closing ...")
    exit(1)
elif pythonVersion >= (3, 12):
    print("Some features may not work with python version newer than 3.11!")

# navigate to project directory
letMeDoItFile = os.path.realpath(__file__)
letMeDoItAIFolder = os.path.dirname(letMeDoItFile)
if os.getcwd() != letMeDoItAIFolder:
    os.chdir(letMeDoItAIFolder)

# check current platform
thisPlatform = platform.system()

# the following code block is not for pip installation
## Activate virtual environment, if any
#venvDir = "venv"
#venvDirFullPath = os.path.join(letMeDoItAIFolder, venvDir)
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
#            os.system(f"{activator} & {python} {letMeDoItFile}")
#        else:
#            # Activate virtual environment
#            activator = os.path.join(venvDirFullPath, binDir, "activate_this.py")
#            if not os.path.exists(activator):
#                copyfile("activate_this.py", activator)
#            with open(activator) as f:
#                code = compile(f.read(), activator, 'exec')
#                exec(code, dict(__file__=activator))
#            # Run main.py
#            os.system(f"{python} {letMeDoItFile}")
#        venvActivated = True
#    except:
#        venvActivated = False
#    if venvActivated:
#        # exit non-venv process
#        exit(0)

# set up config
# create config.py if it does not exist
configFile = os.path.join(letMeDoItAIFolder, "config.py")
if not os.path.isfile(configFile):
    open(configFile, "a", encoding="utf-8").close()

# import config and setup default
#import traceback
from letmedoit import config
from pathlib import Path

apps = {
    "myhand": ("MyHand", "MyHand Bot"),
    "letmedoit": ("LetMeDoIt", "LetMeDoIt AI"),
    "taskwiz": ("TaskWiz", "TaskWiz AI"),
    "cybertask": ("CyberTask", "CyberTask AI"),
}

basename = os.path.basename(letMeDoItAIFolder)
if not hasattr(config, "letMeDoItName") or not config.letMeDoItName:
    config.letMeDoItName = apps[basename][-1] if basename in apps else "LetMeDoIt AI"
config.letMeDoItFile = letMeDoItFile
config.letMeDoItAIFolder = letMeDoItAIFolder

# package name
with open(os.path.join(config.letMeDoItAIFolder, "package_name.txt"), "r", encoding="utf-8") as fileObj:
    package = fileObj.read()

def getPreferredDir():
    preferredDir = os.path.join(os.path.expanduser('~'), package)
    try:
        Path(preferredDir).mkdir(parents=True, exist_ok=True)
    except:
        pass
    return preferredDir if os.path.isdir(preferredDir) else ""
config.getPreferredDir = getPreferredDir

def restartApp():
    print(f"Restarting {config.letMeDoItName} ...")
    os.system(f"{sys.executable} {config.letMeDoItFile}")
    exit(0)
config.restartApp = restartApp

from letmedoit.utils.configDefault import *
from letmedoit.utils.install import *
from letmedoit.utils.shared_utils import SharedUtil

# automatic update
config.pipIsUpdated = False
def updateApp():
    print(f"Checking '{package}' version ...")
    installed_version = SharedUtil.getPackageInstalledVersion(package)
    if installed_version is None:
        print("Installed version information is not accessible!")
    else:
        print(f"Installed version: {installed_version}")
    latest_version = SharedUtil.getPackageLatestVersion(package)
    if latest_version is None:
        print("Latest version information is not accessible at the moment!")
    elif installed_version is not None:
        print(f"Latest version: {latest_version}")
        if latest_version > installed_version:
            if thisPlatform == "Windows":
                print("Automatic upgrade feature is yet to be supported on Windows!")
                print(f"Run 'pip install --upgrade {package}' to manually upgrade this app!")
            else:
                try:
                    # delete old shortcut files
                    appName = config.letMeDoItName.split()[0]
                    shortcutFiles = (f"{appName}.bat", f"{appName}.command", f"{appName}.desktop")
                    for shortcutFile in shortcutFiles:
                        shortcut = os.path.join(config.letMeDoItAIFolder, shortcutFile)
                        if os.path.isfile(shortcut):
                            os.remove(shortcut)
                    # upgrade package
                    installmodule(f"--upgrade {package}")
                    restartApp()
                except:
                    print(f"Failed to upgrade '{package}'!")

# import other libraries
import pprint
from letmedoit.utils.shortcuts import *
from letmedoit.utils.assistant import LetMeDoItAI
from letmedoit.utils.vlc_utils import VlcUtil
from prompt_toolkit.shortcuts import set_title, clear_title
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

def saveConfig():
    with open(configFile, "w", encoding="utf-8") as fileObj:
        for name in dir(config):
            excludeConfigList = [
                "includeIpInSystemMessageTemp",
                "initialCompletionCheck",
                "promptStyle1",
                "promptStyle2",
                "runSpecificFuntion",
                "pluginsWithFunctionCall",
                "restartApp",
                "getPreferredDir",
                "saveConfig",
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
                "predefinedContextTemp",
                "thisPlatform",
                "letMeDoItAI",
                "terminalColors",
                "letMeDoItFile",
                "letMeDoItAIFolder",
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
                # LetMeDoItAI methods shared from Class LetMeDoItAI
                "getFiles",
                "stopSpinning",
                "toggleMultiline",
                "print",
                "print2",
                "print3",
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
config.saveConfig = saveConfig

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
    print(f"launching {config.letMeDoItName} ...")

    # Create the parser
    parser = argparse.ArgumentParser(description="LetMeDoIt AI cli options")
    # Add arguments
    parser.add_argument("default", nargs="?", default=None, help="default entry")
    parser.add_argument('-c', '--context', action='store', dest='context', help="specify pre-defined context with -r flag")
    parser.add_argument('-f', '--file', action='store', dest='file', help="read file text as default entry with -f flag")
    parser.add_argument('-i', '--ip', action='store', dest='ip', help="set 'true' to include or 'false' to exclude ip in system message with -i flag")
    parser.add_argument('-n', '--nocheck', action='store', dest='nocheck', help="set 'true' to bypass completion check at startup with -n flag")
    parser.add_argument('-r', '--run', action='store', dest='run', help="run default entry with -r flag")
    parser.add_argument('-rf', '--runfile', action='store', dest='runfile', help="read file text as default entry and run with -rf flag")
    parser.add_argument('-u', '--update', action='store', dest='update', help="set 'true' to force or 'false' to bypass automatic update with -u flag")
    # Parse arguments
    args = parser.parse_args()
    # Check what kind of arguments were provided and perform actions accordingly

    # update to the latest version
    if args.update:
        if args.update.lower() == "true":
            updateApp()
    # determined by config.autoUpgrade if -u flag is not used
    elif config.autoUpgrade:
        updateApp()

    # initial completion check at startup
    config.initialCompletionCheck = False if args.nocheck and args.nocheck.lower() == "true" else True

    # include ip in system message
    config.includeIpInSystemMessageTemp = True if args.ip and args.ip.lower() == "true" else False

    # specify pre-defined context
    if args.context:
        config.predefinedContextTemp = config.predefinedContext
        config.predefinedContext = args.context

    if args.runfile or args.file:
        try:
            filename = args.runfile if args.runfile else args.file
            filename = os.path.expanduser(filename)
            config.defaultEntry = ""
            if os.path.isfile(filename):
                if os.path.basename(filename) == "selected_files.txt":
                    dirNo = 1
                    fileNo = 1
                    with open(filename, "r", encoding="utf-8") as fileObj:
                        for line in fileObj.readlines():
                            strippedLine = line.strip()
                            if os.path.isdir(strippedLine):
                                config.defaultEntry += f'''Folder {dirNo}: "{strippedLine}"\n'''
                                dirNo += 1
                            elif os.path.isfile(strippedLine):
                                config.defaultEntry += f'''File {fileNo}: "{strippedLine}"\n'''
                                fileNo += 1
                            elif strippedLine:
                                config.defaultEntry += line
                else:
                    with open(filename, "r", encoding="utf-8") as fileObj:
                        config.defaultEntry = fileObj.read()
            else:
                print(f"'{filename}' does not exist!")
        except:
            config.defaultEntry = ""
        config.accept_default = True if args.runfile else False
        for i in ("selected_files", "selected_text"):
            shutil.rmtree(os.path.join(os.path.expanduser('~'), config.letMeDoItName.split()[0].lower(), f"{i}.txt"), ignore_errors=True)
    elif args.run:
        config.defaultEntry = args.run.strip()
        config.accept_default = True
    elif args.default:
        config.defaultEntry = args.default.strip()
        config.accept_default = False
    else:
        config.defaultEntry = ""
        config.accept_default = False

    set_title(config.letMeDoItName)
    setOsOpenCmd()
    createShortcuts()
    config.excludeConfigList = []
    config.isVlcPlayerInstalled = VlcUtil.isVlcPlayerInstalled()
    # check log files; remove old lines if more than 3000 lines is found in a log file
    for i in ("chats", "paths", "commands"):
        filepath = os.path.join(config.historyParentFolder if config.historyParentFolder else config.letMeDoItAIFolder, "history", i)
        set_log_file_max_lines(filepath, 3000)
    LetMeDoItAI().startChats()
    # Do the following tasks before exit
    # backup configurations
    saveConfig()
    preferredDir = getPreferredDir()
    if os.path.isdir(preferredDir):
        shutil.copy(configFile, os.path.join(preferredDir, "config_backup.py"))
    # delete temporary content
    try:
        tempFolder = os.path.join(config.letMeDoItAIFolder, "temp")
        shutil.rmtree(tempFolder, ignore_errors=True)
        Path(tempFolder).mkdir(parents=True, exist_ok=True)
    except:
        pass
    # clear title
    clear_title()

if __name__ == "__main__":
    main()
