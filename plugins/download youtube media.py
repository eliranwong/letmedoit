# install binary ffmpeg and python package yt-dlp to work with this plugin

import config, re, subprocess, os, traceback
from utils.shared_utils import SharedUtil

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
                    print("--------------------")
                    # use os.system, as it displays download status ...
                    os.system("cd {2}; {0} {1}".format(downloadCommand, url_string, outputFolder))
                    if SharedUtil.isPackageInstalled("pkill"):
                        os.system("pkill yt-dlp")
                    print(f"Downloaded in directory '{outputFolder}'!")
                except:
                    if config.developer:
                        print(traceback.format_exc())
                    else:
                        print("Errors!")
                    
            else:
                print("Tool 'ffmpeg' is not found on your system!")
                print("Read https://github.com/eliranwong/myHand.ai/wiki/Install-ffmpeg")


        url = function_args.get("url") # required
        if is_youtube_url(url):
            print("Loading youtube downloader ...")
            format = function_args.get("format") # required
            location = function_args.get("location", "") # optional
            if not (location and os.path.isdir(location)):
                location = os.path.join(config.myHandAIFolder, "audio") if format == "audio" else os.path.join(config.myHandAIFolder, "video")
            downloadCommand = "yt-dlp -x --audio-format mp3" if format == "audio" else "yt-dlp -f bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4"
            terminalDownloadYoutubeFile(downloadCommand, url, location)
            return "Finished! Youtube downloader closed!"
        else:
            print("invalid link given")
            return "[INVALID]"

    functionSignature = {
        "name": "download_youtube_media",
        "description": "download Youtube video into mp4 file or audio into mp3 file",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Youtube url",
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

    config.chatGPTApiFunctionSignatures.append(functionSignature)
    config.chatGPTApiAvailableFunctions["download_youtube_media"] = download_youtube_media

else:
    print("You need to install package 'yt-dlp' to work with plugin 'download youtube media'! Run:\n> source venv/bin/activate\n> 'pip3 install yt-dlp'")