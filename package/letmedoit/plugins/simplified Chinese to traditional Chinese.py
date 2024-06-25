"""
LetMeDoIt AI Plugin - convert simplified Chinese into traditional Chinese

Convert simplified Chinese into traditional Chinese in text output
"""

try:
    from opencc import OpenCC
except:
    from letmedoit.utils.install import installmodule
    installmodule(f"--upgrade opencc")

from letmedoit import config
from opencc import OpenCC

def convertToTraditionalChinese(text):
    if text:
        return OpenCC('s2t').convert(text)
    else:
        return text

config.outputTransformers.append(convertToTraditionalChinese)