"""
LetMeDoIt AI Plugin - ask Codey

Ask Google Codey for information about coding

[FUNCTION_CALL]
"""


from letmedoit import config
from letmedoit.palm2 import VertexAIModel

def ask_codey(function_args):
    query = function_args.get("query") # required
    config.stopSpinning()
    VertexAIModel().run(query, temperature=config.llmTemperature)
    return ""

functionSignature = {
    "name": "ask_codey",
    "description": "Ask Codey for information about coding",
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

config.pluginsWithFunctionCall.append("ask_codey")
config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["ask_codey"] = ask_codey
config.inputSuggestions.append("Ask Codey: ")