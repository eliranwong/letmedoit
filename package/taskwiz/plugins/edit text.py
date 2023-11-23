"""
My Hand Bot Plugin - edit text

edit text files

[FUNCTION_CALL]
"""

from taskwiz import config
import os, re, sys
from taskwiz.utils.shared_utils import SharedUtil

# persistent
# users can customise 'textEditor' and 'textFileExtensions' in config.py
persistentConfigs = (
    #("textEditor", "micro -softwrap true -wordwrap true"), # read options at https://github.com/zyedidia/micro/blob/master/runtime/help/options.md
    ("textFileExtensions", ['txt', 'md', 'py']), # edit this option to support more or less extensions
)
config.setConfig(persistentConfigs)

if config.customTextEditor:
    textEditor = re.sub(" .*?$", "", config.customTextEditor)
    if not textEditor or not SharedUtil.isPackageInstalled(textEditor):
        config.customTextEditor = ""

def edit_text(function_args):
    customTextEditor = config.customTextEditor if config.customTextEditor else f"{sys.executable} {os.path.join(config.myHandAIFolder, 'eTextEdit.py')}"
    filename = function_args.get("filename") # required
    # in case folder name is mistaken
    if os.path.isdir(filename):
        os.system(f"""{config.open} {filename}""")
        return "Finished! Directory opened!"
    else:
        command = f"{customTextEditor} {filename}" if filename else customTextEditor
        config.stopSpinning()
        os.system(command)
        return "Finished! Text editor closed!"

functionSignature = {
    "name": "edit_text",
    "description": f'''Edit text files with extensions: '*.{"', '*.".join(config.textFileExtensions)}'.''',
    "parameters": {
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "Text file path given by user. Return an empty string if not given.",
            },
        },
        "required": ["filename"],
    },
}

config.pluginsWithFunctionCall.append("edit_text")
config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["edit_text"] = edit_text