"""
LetMeDoIt AI Plugin - analyze audio file

analyze audio file

[FUNCTION_CALL]
"""

from letmedoit import config
from letmedoit.utils.shared_utils import SharedUtil
import os

# Function method
def analyze_audio(function_args):
    def check_file_format(file_path):
        # List of allowed file extensions
        allowed_extensions = ('.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm')
        # Getting the file extension
        _, file_extension = os.path.splitext(file_path)
        # Checking if the file extension is in the list of allowed extensions
        return True if file_extension.lower() in allowed_extensions else False

    audio_file = function_args.get("audio") # required

    if audio_file and os.path.isfile(audio_file):
        if not check_file_format(audio_file):
            config.print3("This feature supports the following input file types only: '.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm'!")
            return ""
        elif os.path.getsize(audio_file) / (1024*1024) > 25:
            config.print3("Audio files are currently limited to 25 MB!")
            return ""
        try:
            with open(audio_file, "rb") as audio_file:
                transcript = config.oai_client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file, 
                response_format="text"
                )
            transcript = f"The transcript of the audio is: {transcript}"
            if config.developer:
                config.print2(config.divider)
                config.print3(transcript)
                config.print2(config.divider)
                config.print2("Answer to your enquiry:")
            return transcript
        except:
            SharedUtil.showErrors()
    return "[INVALID]"

# Function Signature
functionSignature = {
    "intent": [
        "analyze files",
    ],
    "examples": [
        "analyze audio",
    ],
    "name": "analyze_audio",
    "description": f'''Answer questions about the content of an audio file or transcribe a audio speech file into text''',
    "parameters": {
        "type": "object",
        "properties": {
            "audio": {
                "type": "string",
                "description": "Return the audio file path that I specified in my requests. Return an empty string '' if it is not specified.",
            },
        },
        "required": ["audio"],
    },
}

# Integrate the signature and method into LetMeDoIt AI
config.addFunctionCall(signature=functionSignature, method=analyze_audio)