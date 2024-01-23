"""
LetMeDoIt AI Plugin - open web browser

open a url with default web browser

[FUNCTION_CALL]
"""

from letmedoit import config
from letmedoit.utils.shared_utils import SharedUtil

# Function method
def open_browser(function_args):
    url = function_args.get("url") # required
    if url:
        SharedUtil.openURL(url)
    return ""

# Function Signature
functionSignature = {
    "name": "open_browser",
    "description": f'''Open an url with default web browser''',
    "parameters": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The url",
            },
        },
        "required": ["url"],
    },
}

# Integrate the signature and method into LetMeDoIt AI
config.pluginsWithFunctionCall.append("open_browser")
config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["open_browser"] = open_browser
config.inputSuggestions.append("Open url: ")