"""
LetMeDoIt AI Plugin - analyze webpage

analyze web content with "AutoGen Retriever"

[FUNCTION_CALL]
"""


from letmedoit import config
from letmedoit.utils.shared_utils import SharedUtil
import os
from letmedoit.autoretriever import AutoGenRetriever

def analyze_web_content(function_args):
    query = function_args.get("query") # required
    url = function_args.get("url") # required
    if not url or not SharedUtil.is_valid_url(url):
        config.print(f"'{url}' is not a valid url" if url else "No url is provided!")
        return "[INVALID]"
    config.stopSpinning()
    filename = SharedUtil.downloadWebContent(url)
    AutoGenRetriever().getResponse(filename, query)
    return ""

functionSignature = {
    "name": "analyze_web_content",
    "description": "retrieve information from a webpage if an url is provided",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Questions that users ask about the given url",
            },
            "url": {
                "type": "string",
                "description": """Return the given url. Return an empty string '' if it is not given.""",
            },
        },
        "required": ["query", "url"],
    },
}

config.pluginsWithFunctionCall.append("analyze_web_content")
config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["analyze_web_content"] = analyze_web_content