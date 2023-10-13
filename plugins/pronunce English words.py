# install package gTTS to work with this plugin

import config
from utils.tts_utils import ttsUtil

try:
    from gtts import gTTS

    def pronunce_english_words(function_args):
        words = function_args.get("words") # required
        print("Loading text-to-speech feature ...")
        ttsUtil.play(words)
        return "Done!"

    functionSignature = {
        "name": "pronunce_english_words",
        "description": "pronounce English words or sentences",
        "parameters": {
            "type": "object",
            "properties": {
                "words": {
                    "type": "string",
                    "description": "words or sentences to be pronounced",
                },
            },
            "required": ["words"],
        },
    }

    config.chatGPTApiFunctionSignatures.insert(0, functionSignature)
    config.chatGPTApiAvailableFunctions["pronunce_english_words"] = pronunce_english_words
except:
    print("You need to install package 'gTTS' to work with plugin 'pronunce English words'! Run:\n> source venv/bin/activate\n> 'pip3 install gTTS'")