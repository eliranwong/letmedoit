"""
LetMeDoIt AI Plugin - remove image background

Remove image background

[FUNCTION_CALL]
"""

from letmedoit import config
from letmedoit.utils.shared_utils import SharedUtil
import os, json

def remove_image_background(function_args):
    code = function_args.get("code") # required
    information = SharedUtil.showAndExecutePythonCode(code)
    if information:
        filepath = json.loads(information)["information"]
        if os.path.isfile(filepath):
            config.print3(f"File saved at: {filepath}")
            try:
                os.system(f'''{config.open} "{filepath}"''')
            except:
                pass
    return ""

functionSignature = {
    "name": "remove_image_background",
    "description": f'''Remove image background''',
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code that integrates package rembg to resolve my request. Always save the removed-background image in png format and use 'print' function to print its full path only, without additional description or comment, in the last line of your code.",
            },
        },
        "required": ["code"],
    },
}

config.pluginsWithFunctionCall.append("remove_image_background")
config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["remove_image_background"] = remove_image_background