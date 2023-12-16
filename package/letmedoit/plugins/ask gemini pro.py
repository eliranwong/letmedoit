"""
LetMeDoIt AI Plugin - ask gemini pro

Ask Google Gemini Pro for information

[FUNCTION_CALL]
"""


from letmedoit import config
from letmedoit.geminipro import GeminiPro

def ask_gemini_pro(function_args):
    query = function_args.get("query") # required
    config.stopSpinning()
    GeminiPro().run(query)
    return ""

functionSignature = {
    "name": "ask_gemini_pro",
    "description": "Ask Gemini Pro for information",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The request in detail",
            },
        },
        "required": ["query"],
    },
}

config.pluginsWithFunctionCall.append("ask_gemini_pro")
config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["ask_gemini_pro"] = ask_gemini_pro