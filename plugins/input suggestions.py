import config, sys, os

config.inputSuggestions += [
        "[NO_SCREENING] ",
        "[NO_FUNCTION_CALL] ",
        f"!{sys.executable}" ,
        f"!{sys.executable} {os.path.join(config.myHandAIFolder, 'autogen_mini.py')}",
        f"!{sys.executable} {os.path.join(config.myHandAIFolder, 'eTextEdit.py')}",
        "write a summary ", 
        "open ",
        "open the current directory",
        "search ",
        "read ",
        "tell me about ",
        "write a prompt so that I may instruct you to:\n",
        f"improve my writing according to {config.improvedWritingSytle}:\n",
    ]

config.inputSuggestions.append("""Translate Content. I want you to assist me as a translator.
I will provide content below for your translation.
After I provide you with the content, you will ask me what language I want it translated to.
I will respond, and you can proceed with the translation.
[NO_FUNCTION_CALL]
Please translate the content below:
""")