"""
LetMeDoIt AI Plugin - create maps

Create maps

[FUNCTION_CALL]
"""

from letmedoit import config
from letmedoit.utils.shared_utils import SharedUtil
import re, os

def create_map(function_args):
    code = function_args.get("code") # required
    information = SharedUtil.showAndExecutePythonCode(code)
    htmlPattern = """\.save\(["']([^\(\)]+\.html)["']\)"""
    match = re.search(htmlPattern, code)
    if match:
        htmlFile = match.group(1)
        os.system(f"{config.open} {htmlFile}")
        return f"Saved as '{htmlFile}'"
    elif information:
        return information
    return ""

functionSignature = {
    "name": "create_map",
    "description": f'''Create maps''',
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code that integrates package folium to resolve my request. Created maps are saved in html format",
            },
        },
        "required": ["code"],
    },
}

config.pluginsWithFunctionCall.append("create_map")
config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["create_map"] = create_map