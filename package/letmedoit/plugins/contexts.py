from letmedoit import config

"""
LetMeDoIt AI Plugin - contexts

add pre-defined contexts
"""

config.predefinedContexts["Let me Summarize"] = """Provide me with a summary of the following content, which is delimited with XML tags "content":
[NO_FUNCTION_CALL]"""

config.predefinedContexts["Let me Explain"] = """Explain the following content, which is delimited with XML tags "content", to me:
[NO_FUNCTION_CALL]"""

config.predefinedContexts["Let me Translate"] = """Assist me by acting as a translator.
Please translate the content below, which is delimited with XML tags "content":
[NO_FUNCTION_CALL]"""