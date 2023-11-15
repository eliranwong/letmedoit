"""
myHand.ai plugin - aliases

add aliases
"""

import config, sys, os

config.aliases["!autogen"] = f"!{sys.executable} {os.path.join(config.myHandAIFolder, 'autogen_mini.py')}"
config.aliases["!etextedit"] = f"!{sys.executable} {os.path.join(config.myHandAIFolder, 'eTextEdit.py')}",

config.inputSuggestions += ["!autogen", "!etextedit"]

# Example to set an alias to open-interpreter
#config.aliases["!interpreter"] = "!~/open-interpreter/venv/bin/interpreter"