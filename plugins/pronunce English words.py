# install package gTTS to work with this plugin

import config, os, subprocess

try:
    from gtts import gTTS

    # pip3 install googlesearch-python
    # Use google https://pypi.org/project/googlesearch-python/ to search internet for information, about which ChatGPT doesn't know.

    def pronunce_english_words(function_args):
        # retrieve argument values from a dictionary
        #print(function_args)
        words = function_args.get("words") # required

        print("Loading text-to-speech feature ...")

        audioFile = os.path.join(config.myHandAIFolder, "temp", "gtts.mp3")
        tts = gTTS(words)
        tts.save(audioFile)

        try:
            command = f'''cvlc --play-and-exit "{audioFile}" &> /dev/null'''
            subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        except:
            command = f"{config.open} audioFile"
            subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
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

    config.pronunce_english_words_signature = [functionSignature]
    config.chatGPTApiFunctionSignatures.insert(0, functionSignature)
    config.chatGPTApiAvailableFunctions["pronunce_english_words"] = pronunce_english_words
except:
    print("You need to install package 'gTTS' to work with plugin 'pronunce English words'! Run:\n> source venv/bin/activate\n> 'pip3 install gTTS'")