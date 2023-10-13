import config, os, traceback, subprocess, re
from gtts import gTTS
from utils.vlc_utils import VlcUtil
try:
    from google.cloud import texttospeech
except:
    pass
try:
    import pygame
except:
    pass

class ttsUtil:

    @staticmethod
    def playAudioFile(audioFile):
        pygame.mixer.music.load(audioFile)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)  # Check every 10 milliseconds
        pygame.mixer.music.stop()

    @staticmethod
    def play(content):
        if config.tts:
            try:
                credentials_GoogleCloudTextToSpeech = os.path.join(config.myHandAIFolder, "credentials_GoogleCloudTextToSpeech.json")
                # official google-cloud-texttospeech
                if os.path.isfile(credentials_GoogleCloudTextToSpeech):
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_GoogleCloudTextToSpeech
                    audioFile = os.path.join(config.myHandAIFolder, "temp", "gctts.mp3")
                    ttsUtil.saveCloudTTSAudio(content, config.gcttsLang, filename=audioFile)
                    ttsUtil.playAudioFile(audioFile)
                elif config.ttsCommand:
                    # remove '"' from the content
                    content = re.sub('"', "", content)
                    #os.system(f'''{config.ttsCommand} "{content}"''')
                    command = f'''{config.ttsCommand} "{content}"{config.ttsCommandSuffix}'''
                    subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                else:
                    # use gTTS as default as config.ttsCommand is empty by default
                    audioFile = os.path.join(config.myHandAIFolder, "temp", "gtts.mp3")
                    tts = gTTS(content, lang=config.gttsLang, tld=config.gttsTld) if config.gttsTld else gTTS(content, lang=config.gttsLang)
                    tts.save(audioFile)
                    ttsUtil.playAudioFile(audioFile)
            except:
                if config.developer:
                    print(traceback.format_exc())
                else:
                    pass

    @staticmethod
    def playAudioFile(audioFile):
        try:
            if config.isVlcPlayerInstalled:
                # vlc is preferred as it allows speed control with config.vlcSpeed
                VlcUtil.playMediaFile(audioFile)
            else:
                ttsUtil.playAudioFile(audioFile)
        except:
            command = f"{config.open} {audioFile}"
            subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

    # Official Google Cloud Text-to-speech Service
    @staticmethod
    def saveCloudTTSAudio(inputText, languageCode="", filename=""):
        if not languageCode:
            languageCode = config.gcttsLang
        # Modified from source: https://cloud.google.com/text-to-speech/docs/create-audio-text-client-libraries#client-libraries-install-python
        """Synthesizes speech from the input string of text or ssml.
        Make sure to be working in a virtual environment.

        Note: ssml must be well-formed according to:
            https://www.w3.org/TR/speech-synthesis/
        """
        # Instantiates a client
        client = texttospeech.TextToSpeechClient()

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=inputText)

        # Build the voice request, select the language code (e.g. "yue-HK") and the ssml
        # voice gender ("neutral")
        # Supported language: https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages
        # Voice: https://cloud.google.com/text-to-speech/docs/voices
        # Gener: https://cloud.google.com/text-to-speech/docs/reference/rest/v1/SsmlVoiceGender
        voice = texttospeech.VoiceSelectionParams(
            language_code=languageCode, ssml_gender=texttospeech.SsmlVoiceGender.SSML_VOICE_GENDER_UNSPECIFIED
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            # For more config, read https://cloud.google.com/text-to-speech/docs/reference/rest/v1/text/synthesize#audioconfig
            speaking_rate=config.gcttsSpeed,
        )

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # The response's audio_content is binary.
        # Save into mp3
        if not filename:
            filename = os.path.abspath(self.getGttsFilename())
        if os.path.isfile(filename):
            os.remove(filename)
        with open(filename, "wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)
            #print('Audio content written to file "{0}"'.format(outputFile))
