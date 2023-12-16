"""
LetMeDoIt AI Plugin - solve math problems

solve math problems with integrated "AutoGen Math Solver"

[FUNCTION_CALL]
"""


from letmedoit import config
from letmedoit.automath import AutoGenMath

def solve_math(function_args):
    query = function_args.get("query") # required
    config.stopSpinning()
    config.print2("AutoGen Math Solver launched!")
    last_message = AutoGenMath().getResponse(query)
    config.currentMessages += last_message
    config.print2("AutoGen Math Solver closed!")
    return ""

functionSignature = {
    "name": "solve_math",
    "description": "solve math problems",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Math problem in detail",
            },
        },
        "required": ["query"],
    },
}

config.pluginsWithFunctionCall.append("solve_math")
config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["solve_math"] = solve_math