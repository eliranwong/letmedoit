# install package gTTS to work with this plugin

import config, os
from utils.shared_utils import SharedUtil

if SharedUtil.isPackageInstalled("micro"):

    def edit_text(function_args):
        filename = function_args.get("filename") # required
        # in case folder name is mistaken
        if os.path.isdir(filename):
            os.system(f"""{config.open} {filename}""")
            return "Finished! Directory opened!"
        else:
            tool = f"micro {filename}" if filename else "micro"
            config.stopSpinning()
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
                    "description": "Text file path given by user. Return an empty string if not given.",
                },
            },
            "required": ["filename"],
        },
    }

    config.chatGPTApiFunctionSignatures.append(functionSignature)
    config.chatGPTApiAvailableFunctions["edit_text"] = edit_text
else:
    print("Install text editor 'micro' to work with plugin 'edit text'.")