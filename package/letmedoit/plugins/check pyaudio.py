from letmedoit import config
from letmedoit.utils.install import installmodule
from letmedoit.utils.shared_utils import SharedUtil
import os

# For more information, read https://github.com/Uberi/speech_recognition#pyaudio-for-microphone-users

try:
    import speech_recognition as sr
    mic = sr.Microphone() 
    del mic
    config.pyaudioInstalled = True
except:
    if config.isTermux:
        config.pyaudioInstalled = False
    elif SharedUtil.isPackageInstalled("apt"):
        config.print2("Installing 'portaudio19-dev' and 'Pyaudio' ...")
        os.system("sudo apt install portaudio19-dev")
        config.pyaudioInstalled = True if installmodule("--upgrade PyAudio") else False
    elif SharedUtil.isPackageInstalled("brew"):
        config.print2("Installing 'portaudio' and 'Pyaudio' ...")
        os.system("brew install portaudio")
        config.pyaudioInstalled = True if installmodule("--upgrade PyAudio") else False
    else:
        config.pyaudioInstalled = False