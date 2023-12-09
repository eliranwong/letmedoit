"""
LetMeDoIt AI Plugin - analyze files

analyze files with "AutoGen Retriever"

[FUNCTION_CALL]
"""


from letmedoit import config
import os
from letmedoit.autoretriever import AutoGenRetriever

def analyze_files(function_args):
    query = function_args.get("query") # required
    files = function_args.get("files") # required
    if os.path.exists(files):
        if os.path.isfile(files) and SharedUtil.is_valid_image_file(files):
            # call function "analyze image" instead if it is an image
            function_args = {
                "query": query,
                "files": [files],
            }
            config.print3("Running function: 'analyze_images'")
            return config.chatGPTApiAvailableFunctions["analyze_images"](function_args)
        config.stopSpinning()
        config.print2("AutoGen Retriever launched!")
        last_message = AutoGenRetriever().getResponse(files, query)
        config.currentMessages += last_message
        config.print2("AutoGen Retriever closed!")
        return ""

    return "[INVALID]"

functionSignature = {
    "name": "analyze_files",
    "description": "retrieve information from files",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Detailed queries about the given files",
            },
            "files": {
                "type": "string",
                "description": """Return a directory or non-image file path. Return an empty string '' if it is not given.""",
            },
        },
        "required": ["query", "files"],
    },
}

config.pluginsWithFunctionCall.append("analyze_files")
config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["analyze_files"] = analyze_files