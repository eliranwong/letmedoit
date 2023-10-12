import config, os, sys, re, platform, subprocess
from utils.shared_utils import SharedUtil

class VlcUtil:

    @staticmethod
    def isVlcPlayerInstalled():
        # on macOS
        if not hasattr(config, "macVlc"):
            macVlc = "/Applications/VLC.app/Contents/MacOS/VLC"
            config.macVlc = macVlc if platform.system() == "Darwin" and os.path.isfile(macVlc) else ""
        # on Windows
        if not hasattr(config, "windowsVlc"):
            windowsVlc = r'C:\Program Files\VideoLAN\VLC\vlc.exe'
            config.windowsVlc = windowsVlc if platform.system() == "Windows" and os.path.isfile(windowsVlc) else ""
        if (config.macVlc or config.windowsVlc or SharedUtil.isPackageInstalled("vlc")):
            return True
        else:
            return False

    @staticmethod
    def openVlcPlayer():
        def run(command):
            os.system("{0}{1} > /dev/null 2>&1 &".format("nohup " if SharedUtil.isPackageInstalled("nohup") else "", command))
        VlcUtil.closeVlcPlayer()
        try:
            if config.windowsVlc:
                os.system(config.windowsVlc)
            elif config.macVlc:
                run(config.macVlc)
            elif SharedUtil.isPackageInstalled("vlc"):
                run("vlc")
        except:
            print("No VLC player is found!")

    @staticmethod
    def closeVlcPlayer():
        try:
            if platform.system() == "Windows":
                os.system("taskkill /IM vlc.exe /F")
            else:
                os.system("pkill VLC")
                os.system("pkill vlc")
        except:
            pass

    @staticmethod
    def playMediaFile(filePath, vlcSpeed=None, audioGui=False):
        if vlcSpeed is None:
            vlcSpeed = config.vlcSpeed
        # get full path and escape double quote
        if isinstance(filePath, str):
            filePath = os.path.abspath(filePath).replace('"', '\\"')
        else:
            # when filePath is a list
            filePath = [os.path.abspath(i).replace('"', '\\"') for i in filePath]
            filePath = '" "'.join(filePath)
        VlcUtil.playMediaFileVlcGui(filePath, vlcSpeed) if re.search("(.mp4|.avi)$", filePath.lower()[-4:]) or audioGui else VlcUtil.playMediaFileVlcNoGui(filePath, vlcSpeed)

    # play audio file with vlc without gui
    @staticmethod
    def playMediaFileVlcNoGui(filePath, vlcSpeed=None):
        if vlcSpeed is None:
            vlcSpeed = config.vlcSpeed
        # vlc on macOS
        if config.macVlc:
            command = f'''{config.macVlc} --intf rc --play-and-exit --rate {vlcSpeed} "{filePath}" &> /dev/null'''
        # vlc on windows
        elif config.windowsVlc:
            command = f'''"{config.windowsVlc}" --play-and-exit --rate {vlcSpeed} "{filePath}"'''
        # vlc on other platforms
        elif SharedUtil.isPackageInstalled("cvlc"):
            command = f'''cvlc --play-and-exit --rate {vlcSpeed} "{filePath}" &> /dev/null'''
        # use .communicate() to wait for the playback to be completed as .wait() or checking pid existence does not work
        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()


    # play video file with vlc with gui
    @staticmethod
    def playMediaFileVlcGui(filePath, vlcSpeed):
        # vlc on macOS
        if config.macVlc:
            command = f'''{config.macVlc} --play-and-exit --rate {vlcSpeed} "{filePath}" &> /dev/null'''
        # vlc on windows
        elif config.windowsVlc:
            command = f'''"{config.windowsVlc}" --play-and-exit --rate {vlcSpeed} "{filePath}"'''
        # vlc on other platforms
        elif SharedUtil.isPackageInstalled("vlc"):
            command = f'''vlc --play-and-exit --rate {vlcSpeed} "{filePath}" &> /dev/null'''
        # use .communicate() to wait for the playback to be completed as .wait() or checking pid existence does not work
        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

if __name__ == '__main__':
    speed = float(sys.argv[1])
    audioFile = " ".join(sys.argv[2:])
    VlcUtil.playMediaFile(audioFile, speed)
    isVlcPlaying = os.path.join("temp", "isVlcPlaying")
    if os.path.isfile(isVlcPlaying):
        os.remove(isVlcPlaying)

