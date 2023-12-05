"""
LetMeDoIt AI Plugin - aliases

add aliases
"""

from letmedoit import config
import sys, os

# add python python to work with virtual environment
config.aliases["!autoassist"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'autoassist.py')}"
config.aliases["!automath"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'automath.py')}"
config.aliases["!autoretriever"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'autoretriever.py')}"
config.aliases["!autoteachable"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'autoteachable.py')}"
config.aliases["!autobuilder"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'autobuilder.py')}"
config.aliases["!etextedit"] = f"!{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'eTextEdit.py')}"

config.inputSuggestions += ["!autoassist", "!autobuilder", "!automath", "!autoretriever", "!autoteachable", "!etextedit", "autoassist", "autobuilder", "automath", "autoretriever", "autoteachable", "etextedit"]

# Example to set an alias to open-interpreter
#config.aliases["!interpreter"] = f"!env OPENAI_API_KEY={config.openaiApiKey} ~/open-interpreter/venv/bin/interpreter"