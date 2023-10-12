import config, os, traceback, subprocess, re
from gtts import gTTS
from utils.vlc_utils import VlcUtil
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
                if config.ttsCommand:
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
                    try:
                        if config.isVlcPlayerInstalled:
                            # vlc is preferred as it allows speed control with config.vlcSpeed
                            VlcUtil.playMediaFile(audioFile)
                        else:
                            ttsUtil.playAudioFile(audioFile)
                    except:
                        command = f"{config.open} {audioFile}"
                        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            except:
                if config.developer:
                    print(traceback.format_exc())
                else:
                    pass