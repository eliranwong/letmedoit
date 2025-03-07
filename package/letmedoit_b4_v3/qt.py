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
if not hasattr(config, "letMeDoItName") or not config.letMeDoItName:
    config.letMeDoItName = apps[package][-1] if package in apps else "LetMeDoIt AI"
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

import sys
from letmedoit.gui.chatgui import ChatGui
from PySide6.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    ChatGui(standalone=True).show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()