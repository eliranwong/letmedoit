"""
LetMeDoIt AI Plugin - input suggestions

add input suggestions
"""

from letmedoit import config
import sys, os

config.inputSuggestions += [
        "[NO_SCREENING] ",
        "NO_SCREENING] ",
        "[NO_FUNCTION_CALL] ",
        "NO_FUNCTION_CALL] ",
        f"!{config.open} ",
        config.open,
        f"!{sys.executable} ",
        sys.executable,
        "open ",
        "read ",
        "search ",
        "analyze ",
        "tell me about ",
        "Craft a prompt for ChatGPT that outlines the necessary steps it should take to complete the following task at hand:\n[NO_FUNCTION_CALL]\n",
        f"Improve the following content according to {config.improvedWritingSytle}:\n[NO_FUNCTION_CALL]\n",
    ]

config.inputSuggestions.append("""Translate Content. Assist me by acting as a translator. Once I have provided you with the content, you should inquire about the language I need it translated into. After I inform you of the desired language, proceed with the translation.
[NO_FUNCTION_CALL]
Please translate the content below:
""")