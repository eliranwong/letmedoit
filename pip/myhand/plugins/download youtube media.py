# install binary ffmpeg and python package yt-dlp to work with this plugin

"""
My Hand Bot Plugin - download youtube media

download Youtube videos or audios

[FUNCTION_CALL]
"""

from myhand import config
import re, subprocess, os
from myhand.utils.shared_utils import SharedUtil
from pathlib import Path

if SharedUtil.isPackageInstalled("yt-dlp"):

    def download_youtube_media(function_args):
        def is_youtube_url(url_string):
            pattern = r'(?:https?:\/\/)?(?:www\.)?youtu(?:\.be|be\.com)\/(?:watch\?v=|embed\/|v\/)?([a-zA-Z0-9\-_]+)'
            match = re.match(pattern, url_string)
            return match is not None

        def isFfmpegInstalled():
            ffmpegVersion = subprocess.Popen("ffmpeg -version", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            *_, stderr = ffmpegVersion.communicate()
            return False if stderr else True

        def terminalDownloadYoutubeFile(downloadCommand, url_string, outputFolder):
            if isFfmpegInstalled():
                try:
                    config.print("--------------------")
                    # use os.system, as it displays download status ...
                    os.system("cd {2}; {0} {1}".format(downloadCommand, url_string, outputFolder))
                    if SharedUtil.isPackageInstalled("pkill"):
                        os.system("pkill yt-dlp")
                    config.print(f"Downloaded in directory '{outputFolder}'!")
                    try:
                        os.system(f'''{config.open} {outputFolder}''')
                    except:
                        pass
                except:
                    SharedUtil.showErrors() 
            else:
                config.print("Tool 'ffmpeg' is not found on your system!")
                config.print("Read https://github.com/eliranwong/myhand/wiki/Install-ffmpeg")


        url = function_args.get("url") # required
        if is_youtube_url(url):
            config.print("Loading youtube downloader ...")
            format = function_args.get("format") # required
            location = function_args.get("location", "") # optional
            if not (location and os.path.isdir(location)):
                location = os.path.join(config.getFiles(), "audio" if format == "audio" else "video")
                Path(location).mkdir(parents=True, exist_ok=True)
            downloadCommand = "yt-dlp -x --audio-format mp3" if format == "audio" else "yt-dlp -f bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4"
            terminalDownloadYoutubeFile(downloadCommand, url, location)
            return "Finished! Youtube downloader closed!"
        else:
            config.print("invalid link given")
            return "[INVALID]"

    functionSignature = {
        "name": "download_youtube_media",
        "description": "download Youtube video into mp4 file or audio into mp3 file",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Youtube url given by user",
                },
                "format": {
                    "type": "string",
                    "description": "Media format to be downloaded. Return 'video' if not given.",
                    "enum": ["video", "audio"],
                },
                "location": {
                    "type": "string",
                    "description": "Output folder where downloaded file is to be saved",
                },
            },
            "required": ["url", "format"],
        },
    }

    config.pluginsWithFunctionCall.append("download_youtube_media")
    config.chatGPTApiFunctionSignatures.append(functionSignature)
    config.chatGPTApiAvailableFunctions["download_youtube_media"] = download_youtube_media

else:
    config.print("You need to install package 'yt-dlp' to work with plugin 'download youtube media'! Run:\n> source venv/bin/activate\n> 'pip3 install yt-dlp'")