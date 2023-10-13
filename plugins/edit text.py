# install package gTTS to work with this plugin

import config
from utils.shared_utils import SharedUtil

if SharedUtil.isPackageInstalled("micro"):

    def edit_text(function_args):
        filename = function_args.get("filename") # required
        tool = f"micro {filename}" if filename else "micro"
        config.stop_event.set()
        config.spinner_thread.join()
        SharedUtil.textTool(tool, "")
        return "Finished! Text editor closed!"

    functionSignature = {
        "name": "edit_text",
        "description": "edit a text file",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Full or relative path of the text file that is to be edited. Return an empty string if not given.",
                },
            },
            "required": ["filename"],
        },
    }

    config.chatGPTApiFunctionSignatures.append(functionSignature)
    config.chatGPTApiAvailableFunctions["edit_text"] = edit_text
else:
    print("Install text editor 'micro' to work with plugin 'edit text'.")