"""
My Hand Bot Plugin - convert simplified Chinese into traditional Chinese

Convert simplified Chinese into traditional Chinese in text output
"""

try:
    from opencc import OpenCC
except:
    from myhand.utils.install import *
    installmodule(f"--upgrade opencc")

from myhand import config
from opencc import OpenCC

def convertToTraditionalChinese(text):
    if text:
        return OpenCC('s2t').convert(text)
    else:
        return text

config.chatGPTTransformers.append(convertToTraditionalChinese)