import config

config.inputSuggestions += [
        "[NO_SCREENING] ",
        "[NO_FUNCTION_CALL] ",
        "Write a summary ", 
        "Open ",
        "Search ", 
        "Read ",
        "Tell me about ",
    ]

config.inputSuggestions.append("""Translate Content. I want you to assist me as a translator.
I will provide content below for your translation.
After I provide you with the content, you will ask me what language I want it translated to.
I will respond, and you can proceed with the translation.
[NO_FUNCTION_CALL]
Please translate the content below:
""")