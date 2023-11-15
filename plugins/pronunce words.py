"""
myHand.ai plugin - pronunce words

add predefined contexts about pastoral care
"""

try:
    from gtts import gTTS
except:
    from utils.install import *
    installmodule(f"--upgrade gTTS")

import config
from utils.tts_utils import TTSUtil


from gtts import gTTS

def pronunce_words(function_args):
    words = function_args.get("words") # required
    language = function_args.get("language") # required
    config.print("Loading speech feature ...")
    TTSUtil.play(words, language)
    return "Finished! Speech engine closed!"

functionSignature = {
    "name": "pronunce_words",
    "description": "pronounce words or sentences",
    "parameters": {
        "type": "object",
        "properties": {
            "words": {
                "type": "string",
                "description": "Words to be pronounced",
            },
            "language": {
                "type": "string",
                "description": "Language of the words",
                "enum": config.ttsLanguages,
            },
        },
        "required": ["words", "language"],
    },
}

config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["pronunce_words"] = pronunce_words
