"""
My Hand Bot Plugin - dates and times

Retrieve information about dates and times
"""

from myhand import config
from myhand.utils.shared_utils import SharedUtil
import re, os

def generate_maps(function_args):
    code = function_args.get("code") # required
    information = SharedUtil.showAndExecutePythonCode(code)
    htmlPattern = """\.save\(["']([^\(\)]+\.html)["']\)"""
    match = re.search(htmlPattern, code)
    if match:
        htmlFile = match.group(1)
        os.system(f"{config.open} {htmlFile}")
    elif information:
        return information
    return ""

functionSignature = {
    "name": "generate_maps",
    "description": f'''Create maps''',
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code that integrates package folium to resolve my request. Greated maps are saved in html format",
            },
        },
        "required": ["code"],
    },
}

config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["generate_maps"] = generate_maps