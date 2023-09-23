import config, json, platform


# ChatGPT-GUI plugin: Instruct ChatGPT to excute python code directly in response to user input
# Written by: Eliran Wong
# Feature: Non-python users can use natural language to instruct ChatGPT to perform whatever tasks which python is capable to do.

# Usage:
# 1. Select "Execute Python Code" as predefined context
# 2. Use natural language to instruct ChatGPT to execute what python is capable to do
# 
# Examples, try:
# Tell me the current time.
# Tell me how many files in the current directory.
# What is my operating system and version?
# Is google chrome installed on this computer?
# Open web browser.
# Open https://github.com/eliranwong/ChatGPT-GUI in a web browser.
# Search ChatGPT in a web browser.
# Open the current directory using the default file manager.
# Open VLC player.
# Open Calendar.
# Ask Siri to open the current directory

def execute_python_code(function_args):
    # retrieve argument values from a dictionary
    #print(function_args)
    function_args = function_args.get("code") # required

    # show pyton code for developer
    if config.developer:
        print("--------------------")
        print("running python code ...\n")
        print("```")
        print(function_args)
        print("```\n")

    insert_string = "import config\nconfig.pythonFunctionResponse = "
    if "\n" in function_args:
        substrings = function_args.rsplit("\n", 1)
        lastLine = re.sub("print\((.*)\)", r"\1", substrings[-1])
        new_function_args = f"{substrings[0]}\n{insert_string}{lastLine}"
    else:
        new_function_args = f"{insert_string}{function_args}"
    try:
        exec(new_function_args, globals())
        function_response = str(config.pythonFunctionResponse)
    except:
        errorMessage = "Failed to run the python code!"
        if config.developer:
            print(errorMessage)
            print("--------------------")
        return errorMessage
    info = {"information": function_response}
    function_response = json.dumps(info)
    return json.dumps(info)

functionSignature = {
    "name": "execute_python_code",
    "description": "Execute python code",
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "python code, e.g. print('Hello world')",
            },
        },
        "required": ["code"],
    },
}

config.execute_python_code_signature = [functionSignature]
config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["execute_python_code"] = execute_python_code
current_platform = platform.system()
if current_platform == "Darwin":
    current_platform = "macOS"
config.predefinedContexts["Execute Python Code"] = f"""I am running {current_platform} on this device. Execute python code directly on my behalf to achieve the following tasks. Do not show me the codes unless I explicitly request it."""