from letmedoit import config

"""
LetMeDoIt AI Plugin - contexts

add pre-defined contexts
"""

config.predefinedContexts["Let me Summarize"] = """Provide me with a summary of the following content:
[NO_FUNCTION_CALL]"""

config.predefinedContexts["Let me Explain"] = """Explain the following content to me:
[NO_FUNCTION_CALL]"""

config.predefinedContexts["Let me Translate"] = """Assist me by acting as a translator. Once I have provided you with the content, you should inquire about the language I need it translated into. After I inform you of the desired language, proceed with the translation without function call.
Please translate the content below:
[NO_FUNCTION_CALL]"""