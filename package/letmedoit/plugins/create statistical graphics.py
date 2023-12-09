"""
LetMeDoIt AI Plugin - dates and times

Retrieve information about dates and times

[FUNCTION_CALL]
"""

from letmedoit import config
from letmedoit.utils.shared_utils import SharedUtil
import os, re

def create_statistical_graphics(function_args):
    config.stopSpinning()

    code = function_args.get("code") # required
    information = SharedUtil.showAndExecutePythonCode(code)

    pngPattern = """\.savefig\(["']([^\(\)]+\.png)["']\)"""
    match = re.search(pngPattern, code)
    if match:
        pngFile = match.group(1)
        os.system(f"{config.open} {pngFile}")
        return f"Saved as '{pngFile}'"
    elif information:
        return information
    return ""

functionSignature = {
    "name": "create_statistical_graphics",
    "description": f'''Create statistical plots, such as pie charts or bar charts, to visualize statistical data''',
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code that integrates package seaborn to resolve my request. Use TkAgg as backend. Greated plots are saved in png format",
            },
        },
        "required": ["code"],
    },
}

config.pluginsWithFunctionCall.append("create_statistical_graphics")
config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["create_statistical_graphics"] = create_statistical_graphics