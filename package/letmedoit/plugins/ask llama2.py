"""
LetMeDoIt AI Plugin - ask Llama2

Ask Llama2 for information

[FUNCTION_CALL]
"""


from letmedoit import config
from letmedoit.ollamachat import OllamaChat

def ask_llama2(function_args):
    query = function_args.get("query") # required
    config.stopSpinning()
    OllamaChat().run(query, model="llama2")
    return ""

functionSignature = {
    "name": "ask_llama2",
    "description": "Ask Llama2 to chat or provide information",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The request in detail, including any supplementary information",
            },
        },
        "required": ["query"],
    },
}

config.addFunctionCall(name="ask_llama2", signature=functionSignature, method=ask_llama2)
config.inputSuggestions.append("Ask Llama2: ")