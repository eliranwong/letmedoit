from letmedoit import config
from letmedoit.health_check import HealthCheck
if not hasattr(config, "currentMessages"):
    HealthCheck.setBasicConfig()
    config.saveConfig()
    #print("Configurations updated!")
from letmedoit.utils.prompts import Prompts
from letmedoit.utils.terminal_system_command_prompt import SystemCommandPrompt
import platform

def setOsOpenCmd():
    thisPlatform = platform.system()
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

def main():
    config.systemCommandPromptEntry = ""
    config.print = print
    setOsOpenCmd()
    Prompts()
    SystemCommandPrompt().run(allowPathChanges=True)

if __name__ == '__main__':
    main()