"""
LetMeDoIt AI Plugin - ask PaLM 2

Ask Google PaLM 2 for information

[FUNCTION_CALL]
"""


from letmedoit import config
from letmedoit.palm2 import VertexAIModel

def ask_palm2(function_args):
    query = function_args.get("query") # required
    config.stopSpinning()
    VertexAIModel().run(query, temperature=config.llmTemperature)
    return ""

functionSignature = {
    "name": "ask_palm2",
    "description": "Ask PaLM 2 for information",
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

config.pluginsWithFunctionCall.append("ask_palm2")
config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["ask_palm2"] = ask_palm2
config.inputSuggestions.append("Ask PaLM 2: ")