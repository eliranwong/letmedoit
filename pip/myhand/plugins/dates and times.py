"""
My Hand Bot Plugin - dates and times

Retrieve information about dates and times

[FUNCTION_CALL]
"""

from myhand import config
from myhand.utils.shared_utils import SharedUtil

def datetimes(function_args):
    code = function_args.get("code") # required
    information = SharedUtil.showAndExecutePythonCode(code)
    return information

functionSignature = {
    "name": "datetimes",
    "description": f'''Get information about dates and times''',
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code that integrates package pendulum to resolve my query",
            },
        },
        "required": ["code"],
    },
}

config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["datetimes"] = datetimes