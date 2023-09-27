import config, openai, glob, threading, os, time, traceback, re, subprocess, json, datetime, webbrowser
from utils.prompts import Prompts
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
from utils.terminal_mode_dialogs import TerminalModeDialogs
from utils.promptValidator import FloatValidator
from utils.get_path_prompt import GetPath

class MyHandAI:

    def __init__(self):
        #config.myHandAI = self
        self.prompts = Prompts()
        self.dialogs = TerminalModeDialogs(self)
        self.setup()
        self.runPlugins()
        self.setupPythonExecution()

    def setup(self):
        self.divider = "--------------------"
        config.defaultEntry = ""

        # token limit
        self.tokenLimits = {
            "gpt-3.5-turbo-instruct": 4097,
            "gpt-3.5-turbo": 4097,
            "gpt-3.5-turbo-16k": 16385,
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
        }

        if not config.openaiApiKey:
            self.changeAPIkey()

        if not config.openaiApiKey:
            print("ChatGPT API key not found!")
            print("Read https://github.com/eliranwong/myHand.ai/wiki/ChatGPT-API-Key")
            exit(0)

        # required
        self.checkCompletion()
        # optional
        if config.openaiApiOrganization:
            openai.organization = config.openaiApiOrganization
        # chat records
        chat_history = os.path.join(os.getcwd(), "history", "chats")
        self.terminal_chat_session = PromptSession(history=FileHistory(chat_history))

    def getFolderPath(self):
        # get path
        getPath = GetPath(
            cancel_entry=".cancel",
            promptIndicatorColor=config.terminalPromptIndicatorColor2,
            promptEntryColor=config.terminalCommandEntryColor2,
            subHeadingColor=config.terminalHeadingTextColor,
            itemColor=config.terminalResourceLinkColor,
            workingDirectory=config.myHandAIFolder,
        )
        return getPath.getFolderPath(
            check_isdir=True, 
            display_dir_only=True, 
            create_dirs_if_not_exist=True, 
            empty_to_cancel=True, 
            list_content_on_directory_change=True, 
            keep_startup_directory=True, 
            message=f"{self.divider}\nSetting a startup directory ...\nEnter a folder name or path below:", 
            bottom_toolbar="", 
            promptIndicator = ""
        )

    def fileNamesWithoutExtension(self, dir, ext):
        files = glob.glob(os.path.join(dir, "*.{0}".format(ext)))
        return sorted([file[len(dir)+1:-(len(ext)+1)] for file in files if os.path.isfile(file)])

    def execPythonFile(self, script):
        if config.developer:
            with open(script, 'r', encoding='utf8') as f:
                code = compile(f.read(), script, 'exec')
                exec(code, globals())
        else:
            try:
                with open(script, 'r', encoding='utf8') as f:
                    code = compile(f.read(), script, 'exec')
                    exec(code, globals())
            except:
                print("Failed to run '{0}'!".format(os.path.basename(script)))

    def runPlugins(self):
        # The following config values can be modified with plugins, to extend functionalities
        config.predefinedContexts = {
            "[none]": "",
            "[custom]": "",
        }
        config.inputSuggestions = []
        config.chatGPTTransformers = []
        config.chatGPTApiFunctionSignatures = []
        config.chatGPTApiAvailableFunctions = {}

        pluginFolder = os.path.join(config.myHandAIFolder, "plugins")
        # always run 'integrate google searches'
        internetSeraches = "integrate google searches"
        script = os.path.join(pluginFolder, "{0}.py".format(internetSeraches))
        self.execPythonFile(script)
        for plugin in self.fileNamesWithoutExtension(pluginFolder, "py"):
            if not plugin in config.chatGPTPluginExcludeList:
                script = os.path.join(pluginFolder, "{0}.py".format(plugin))
                self.execPythonFile(script)
        if internetSeraches in config.chatGPTPluginExcludeList:
            del config.chatGPTApiFunctionSignatures[0]

    def selectPlugins(self):
        plugins = []
        enabledPlugins = []
        pluginFolder = os.path.join(config.myHandAIFolder, "plugins")
        for plugin in self.fileNamesWithoutExtension(pluginFolder, "py"):
            plugins.append(plugin)
            if not plugin in config.chatGPTPluginExcludeList:
                enabledPlugins.append(plugin)
        enabledPlugins = self.dialogs.getMultipleSelection(
            title="Enable / Disable Plugins", 
            text="Select to enable plugin(s):", 
            options=plugins, 
            default_values=enabledPlugins,
        )
        if enabledPlugins is not None:
            for p in plugins:
                if p in enabledPlugins and p in config.chatGPTPluginExcludeList:
                    config.chatGPTPluginExcludeList.remove(p)
                elif not p in enabledPlugins and not p in config.chatGPTPluginExcludeList:
                    config.chatGPTPluginExcludeList.append(p)
            self.runPlugins()
            self.print("Plugin selection updated!")

    def getCliOutput(self, cli):
        try:
            process = subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, *_ = process.communicate()
            return stdout.decode("utf-8")
        except:
            return ""

    def fingerprint(self):
        try:
            output = json.loads(self.getCliOutput("termux-fingerprint"))
            return True if output["auth_result"] == "AUTH_RESULT_SUCCESS" else False
        except:
            return False

    def changeAPIkey(self):
        if not config.terminalEnableTermuxAPI or (config.terminalEnableTermuxAPI and self.fingerprint()):
            self.print("Enter your OpenAI API Key [required]:")
            apikey = self.prompts.simplePrompt(default=config.openaiApiKey)
            if apikey and not apikey.strip().lower() == config.terminal_cancel_action:
                config.openaiApiKey = apikey
            self.print("Enter your Organization ID [optional]:")
            oid = self.prompts.simplePrompt(default=config.openaiApiOrganization)
            if oid and not oid.strip().lower() == config.terminal_cancel_action:
                config.openaiApiOrganization = oid
            self.checkCompletion()
            self.print("Updated!")

    def cancelAction(self):
        message = "closing ..."
        self.print(message)
        self.print(self.divider)
        return ""

    def print(self, content):
        print(content)
        # format content output later

    def spinning_animation(self, stop_event):
        while not stop_event.is_set():
            for symbol in '|/-\\':
                print(symbol, end='\r')
                time.sleep(0.1)

    def getChatResponse(self, completion):
        chat_response = completion["choices"][0]["message"]["content"]
        # transform response with plugins
        if chat_response:
            for t in config.chatGPTTransformers:
                chat_response = t(chat_response)
        return chat_response

    def getFunctionResponse(self, response_message, function_name):
        if function_name == "python":
            config.pythonFunctionResponse = ""
            function_args = response_message["function_call"]["arguments"]
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
                function_response = function_args
            info = {"information": function_response}
            function_response = json.dumps(info)
        else:
            fuction_to_call = config.chatGPTApiAvailableFunctions[function_name]
            function_args = json.loads(response_message["function_call"]["arguments"])
            function_response = fuction_to_call(function_args)
        return function_response

    def getStreamFunctionResponseMessage(self, completion, function_name):
        function_arguments = ""
        for index, event in enumerate(completion):
            delta = event["choices"][0]["delta"]
            if delta and delta.get("function_call"):
                function_arguments += delta["function_call"]["arguments"]
        return {
            "role": "assistant",
            "content": None,
            "function_call": {
                "name": function_name,
                "arguments": function_arguments,
            }
        }

    def setupPythonExecution(self):
        def execute_python_code(function_args):
            errorMessage = "Failed to run the python code!"

            # retrieve argument values from a dictionary
            #print(function_args)
            title = function_args.get("title") # required
            function_args = function_args.get("code") # required

            # show pyton code for developer
            print("--------------------")
            print(f"Python: {title}")
            if config.developer or config.pythonExecutionDisplay:
                print("```")
                print(function_args)
                print("```")
            print("--------------------")
            
            if config.pythonExecutionConfirmation:
                print("Do you want to execute it? [y]es / [N]o")
                confirmation = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default="y")
                if not confirmation.lower() in ("y", "yes"):
                    return errorMessage

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
                    "title": {
                        "type": "string",
                        "description": "title for the python code",
                    },
                },
                "required": ["code", "title"],
            },
        }

        config.execute_python_code_signature = [functionSignature]
        config.chatGPTApiAvailableFunctions["execute_python_code"] = execute_python_code

    def pythonExecution(self, messages, userInput):
        self.print("screening ...")

        messagesCopy = messages[:]

        context = """In response to the following request, answer me either "python" or "chat" without extra comments.
Answer "python" only if you can execute python code to get the requested information or carry out the requested task, e.g. open a web browser.
Answer "chat" if I explicitly ask you "do not execute" or if I start my request with "how".
Otherwise, answer "chat". Here is the request:"""

        messagesCopy.append({"role": "user", "content": f"{context} {userInput}"})
        completion = openai.ChatCompletion.create(
            model=config.chatGPTApiModel,
            messages=messagesCopy,
            n=1,
            temperature=0.0,
            max_tokens=config.chatGPTApiMaxTokens,
        )
        answer = completion.choices[0].message.content
        self.screenAction = answer = re.sub("[^A-Za-z]", "", answer).lower()

        self.print("screening done!")

        if answer == "python":
            context = f"""I am running {"Termux on Android" if config.terminalEnableTermuxAPI else config.thisPlatform} on this device. Execute python codes{" and Termux commands" if config.terminalEnableTermuxAPI else ""} directly on my behalf to achieve the following tasks. Do not show me the codes unless I explicitly request it."""
            userInputWithcontext = f"{context}\n{userInput}"
            messages.append({"role": "user", "content" : userInputWithcontext})
            messages = self.runFunction(messages, config.execute_python_code_signature, "execute_python_code")
            if messages[-1]["content"] == "Failed to run the python code!":
                messages = messages[:-3]
            else:
                return messages
        #elif answer == "web":
        #    messages.append({"role": "user", "content" : userInput})
        #    return self.runFunction(messages, config.integrate_google_searches_signature, "integrate_google_searches")
        messages.append({"role": "user", "content" : userInput})
        return messages

    def runFunction(self, messages, functionSignatures, function_name):
        messagesCopy = messages[:]
        try:
            completion = openai.ChatCompletion.create(
                model=config.chatGPTApiModel,
                messages=messages,
                max_tokens=config.chatGPTApiMaxTokens,
                temperature=config.chatGPTApiTemperature,
                n=1,
                functions=functionSignatures,
                function_call={"name": function_name},
            )
            response_message = completion["choices"][0]["message"]
            function_response = self.getFunctionResponse(response_message, function_name)
            messages.append(response_message)
            messages.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                }
            )
        except:
            self.showErrors()
            return messagesCopy
        return messages

    def showErrors(self):
        if config.developer:
            print(traceback.format_exc())

    def runCompletion(self, thisMessage):
        self.functionJustCalled = False
        def runThisCompletion(thisThisMessage):
            if config.chatGPTApiFunctionSignatures and not self.functionJustCalled:
                return openai.ChatCompletion.create(
                    model=config.chatGPTApiModel,
                    messages=thisThisMessage,
                    n=1,
                    temperature=0.0 if config.chatGPTApiPredefinedContext == "Execute Python Code" else config.chatGPTApiTemperature,
                    max_tokens=config.chatGPTApiMaxTokens,
                    functions=config.chatGPTApiFunctionSignatures,
                    function_call={"name": "execute_python_code"} if config.chatGPTApiPredefinedContext == "Execute Python Code" else config.chatGPTApiFunctionCall,
                    stream=True,
                )
            return openai.ChatCompletion.create(
                model=config.chatGPTApiModel,
                messages=thisThisMessage,
                n=1,
                temperature=config.chatGPTApiTemperature,
                max_tokens=config.chatGPTApiMaxTokens,
                stream=True,
            )

        while True:
            completion = runThisCompletion(thisMessage)
            function_name = ""
            try:
                # consume the first delta
                for event in completion:
                    delta = event["choices"][0]["delta"]
                    # Check if a function is called
                    if not delta.get("function_call"):
                        self.functionJustCalled = True
                    # When streaming is enabled, in some rare cases, ChatGPT does not return function name
                    # check here
                    elif "name" in delta["function_call"]:
                        function_name = delta["function_call"]["name"]
                    # check the first delta is enough
                    break
                # Continue only when a function is called
                if self.functionJustCalled:
                    break

                if function_name:
                    response_message = self.getStreamFunctionResponseMessage(completion, function_name)
                else:
                    # when function name is not available (very rare)
                    # try again without streaming
                    completion = openai.ChatCompletion.create(
                        model=config.chatGPTApiModel,
                        messages=thisMessage,
                        n=1,
                        temperature=0.0 if config.chatGPTApiPredefinedContext == "Execute Python Code" else config.chatGPTApiTemperature,
                        max_tokens=config.chatGPTApiMaxTokens,
                        functions=config.chatGPTApiFunctionSignatures,
                        function_call={"name": "run_python"} if config.chatGPTApiPredefinedContext == "Execute Python Code" else config.chatGPTApiFunctionCall,
                    )
                    response_message = completion["choices"][0]["message"]
                    if response_message.get("function_call"):
                        function_name = response_message["function_call"]["name"]
                    else:
                        break
                # get function response
                function_response = self.getFunctionResponse(response_message, function_name)

                # process function response
                # send the info on the function call and function response to GPT
                thisMessage.append(response_message) # extend conversation with assistant's reply
                thisMessage.append(
                    {
                        "role": "function",
                        "name": function_name,
                        "content": function_response,
                    }
                )  # extend conversation with function response

                self.functionJustCalled = True

                if not config.chatAfterFunctionCalled:
                    self.print(function_response)
                    break
            except:
                self.showErrors()
                break

        return completion

    # reset message when a new chart is started or context is changed
    def resetMessages(self):
        systemMessage = "You’re a kind helpful assistant."
        if config.chatGPTApiFunctionCall == "auto" and config.chatGPTApiFunctionSignatures:
            systemMessage += " Only use the functions you have been provided with."
        messages = [
            {"role": "system", "content" : systemMessage}
        ]
        return messages

    def getCurrentContext(self):
        if not config.chatGPTApiPredefinedContext in config.predefinedContexts:
            config.chatGPTApiPredefinedContext = "[none]"
        if config.chatGPTApiPredefinedContext == "[none]":
            # no context
            context = ""
        elif config.chatGPTApiPredefinedContext == "[custom]":
            # custom input in the settings dialog
            context = config.chatGPTApiCustomContext
        else:
            # users can modify config.predefinedContexts via plugins
            context = config.predefinedContexts[config.chatGPTApiPredefinedContext]
            # change configs for particular contexts
            if config.chatGPTApiPredefinedContext == "Execute Python Code":
                if config.chatGPTApiFunctionCall == "none":
                    config.chatGPTApiFunctionCall = "auto"
                if config.loadingInternetSearches == "always":
                    config.loadingInternetSearches = "auto"
        return context

    def fineTuneUserInput(self, userInput, conversationStarted):
        # customise chat context
        context = self.getCurrentContext()
        if context and (config.chatGPTApiPredefinedContext == "Execute Python Code" or conversationStarted or (not conversationStarted and config.chatGPTApiContextInAllInputs)):
            userInput = f"{context}\n{userInput}"
        return userInput

    def runOptions(self, features, userInput):
        descriptions = (
            "start a new chat [ctrl+n]",
            "share content [ctrl+s]" if config.terminalEnableTermuxAPI else "save content [ctrl+s]",
            "swap multi-line input [ctrl+l]",
            "change chat context [ctrl+o]",
            "change chat context inclusion",
            "change API key",
            "change ChatGPT model",
            "change ChatGPT temperature",
            "change maximum tokens",
            "change plugins",
            "change function call",
            "change function response",
            "change online searches",
            "change task execution",
            "change python code display",
            "change execution confirmation",
            "change startup directory",
            "change developer mode",
            "open myHand.ai wiki",
        )
        feature = self.dialogs.getValidOptions(
            options=features, 
            descriptions=descriptions, 
            title="myHand AI", 
            default=config.defaultBlankEntryAction,
            text="Select an action or make changes:",
        )
        if feature:
            if feature == ".chatgptmodel":
                models = ("gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k")
                model = self.dialogs.getValidOptions(
                    options=models, 
                    title="ChatGPT model", 
                    default=config.chatGPTApiModel,
                    text="Select a ChatGPT model:",
                )
                if model:
                    config.chatGPTApiModel = model
                    tokenLimit = self.tokenLimits[model]
                    if config.chatGPTApiMaxTokens > tokenLimit:
                        config.chatGPTApiMaxTokens = tokenLimit
                    self.print(f"ChatGPT model selected: {model}")
            elif feature == ".latestSearches":
                options = ("always", "auto", "none")
                descriptions = (
                    "always search for latest information",
                    "search only when ChatGPT lacks information",
                    "do not perform online searches",
                )
                option = self.dialogs.getValidOptions(
                    options=options, 
                    descriptions=descriptions, 
                    title="Latest Online Searches", 
                    default=config.loadingInternetSearches, 
                    text="myHand can perform online searches.\nHow do you want this feature?",
                )
                if option:
                    config.loadingInternetSearches = option
                    # fine tune
                    if config.loadingInternetSearches == "auto":
                        config.chatGPTApiFunctionCall = "auto"
                        if "integrate google searches" in config.chatGPTPluginExcludeList:
                            config.chatGPTPluginExcludeList.remove("integrate google searches")
                    elif config.loadingInternetSearches == "none":
                        if not "integrate google searches" in config.chatGPTPluginExcludeList:
                            config.chatGPTPluginExcludeList.append("integrate google searches")
                    # notify
                    self.print(f"Latest Online Searches: {option}")
            elif feature == ".startupDirectory":
                folder = self.getFolderPath()
                if folder and os.path.isdir(folder):
                    config.startupdirectory = folder
                    self.print(f"Startup directory changed to:\n{folder}")
            elif feature == ".contextintensity":
                options = ("the first input only", "all inputs")
                option = self.dialogs.getValidOptions(
                    options=options, 
                    title="Predefined Context Inclusion", 
                    default=config.chatGPTApiContextInAllInputs,
                    text="Define below how you want to include predefined context\nwith your inputs.\nApply predefined context in ...",
                )
                if option:
                    config.chatGPTApiContextInAllInputs = True if option == "all inputs" else False
                    self.print(f"Predefined Context Inclusion: {option}!")
            elif feature == ".pythoncodedisplay":
                options = ("enable", "disable")
                option = self.dialogs.getValidOptions(
                    options=options, 
                    title="Python Code Display", 
                    default="enable" if config.pythonExecutionDisplay else "disable",
                    text="Options to display Python codes before execution:"
                )
                if option:
                    config.pythonExecutionDisplay = (option == "enable")
                    self.print(f"Python code display: {option}d!")
            elif feature == ".confirmpythonexecution":
                options = ("enable", "disable")
                option = self.dialogs.getValidOptions(
                    options=options, 
                    title="Confirm Execution before running Python Codes", 
                    default="enable" if config.pythonExecutionConfirmation else "disable",
                )
                if option:
                    config.pythonExecutionConfirmation = (option == "enable")
                    self.print(f"Task execution confirmation: {option}d!")
            elif feature == ".plugins":
                self.selectPlugins()
            elif feature == ".help":
                webbrowser.open('https://github.com/eliranwong/myHand.ai/wiki')
            elif feature == ".developer":
                options = ("enable", "disable")
                option = self.dialogs.getValidOptions(
                    options=options, 
                    title="Developer Mode", 
                    default="enable" if config.developer else "disable",
                    text="Read myHand.ai wiki for more information.\nSelect an option below:"
                )
                if option:
                    config.developer = (option == "enable")
                    self.print(f"Developer Mode: {option}d!")
            elif feature == ".pythonexecution":
                options = ("enable", "disable")
                option = self.dialogs.getValidOptions(
                    options=options, 
                    title="Python Execution", 
                    default="enable" if config.pythonExecution else "disable",
                    text="myHand can execute python codes\nto get information for a response\nor perform a task for users.\nEnable / Disable this feature below:",
                )
                if option:
                    config.pythonExecution = (option == "enable")
                    self.print(f"Python Execution: {option}d!")
            elif feature == ".functioncall":
                calls = ("auto", "none")
                call = self.dialogs.getValidOptions(
                    options=calls, 
                    title="ChatGPT Function Call", 
                    default=config.chatGPTApiFunctionCall,
                    text="Enabling function call\nallows online searches\nor other third-party features\nto extend ChatGPT capabilities.\nEnable / Disable this feature below:",
                )
                if call:
                    config.chatGPTApiFunctionCall = call
                    self.print(f"ChaptGPT function call: {'enabled' if config.chatGPTApiFunctionCall == 'auto' else 'disabled'}!")
            elif feature == ".functionresponse":
                calls = ("enable", "disable")
                call = self.dialogs.getValidOptions(
                    options=calls, 
                    title="Automatic Chat Generation with Function Response", 
                    default="enable" if config.chatAfterFunctionCalled else "disable",
                    text="Enable this feature\nto generate further responses\naccording to function call results.\nDisable this feature allows\nperforming function calls\nwihtout generating further responses."
                )
                if call:
                    config.chatAfterFunctionCalled = (call == "enable")
                    self.print(f"Automatic Chat Generation with Function Response: {'enabled' if config.chatAfterFunctionCalled else 'disabled'}!")
            elif feature == ".maxtokens":
                tokenLimit = self.tokenLimits[config.chatGPTApiModel]
                self.print(f"You are using ChatGPT model '{config.chatGPTApiModel}', which allows no more than {tokenLimit} tokens.")
                self.print("(GPT and embeddings models process text in chunks called tokens. As a rough rule of thumb, 1 token is approximately 4 characters or 0.75 words for English text. One limitation to keep in mind is that for a GPT model the prompt and the generated output combined must be no more than the model's maximum context length.)")
                maxtokens = self.prompts.simplePrompt(numberOnly=True, default=str(config.chatGPTApiMaxTokens))
                if maxtokens and not maxtokens.strip().lower() == config.terminal_cancel_action and int(maxtokens) > 0:
                    config.chatGPTApiMaxTokens = int(maxtokens)
                    if config.chatGPTApiMaxTokens > tokenLimit:
                        config.chatGPTApiMaxTokens = tokenLimit
                    self.print(f"Maximum tokens entered: {config.chatGPTApiMaxTokens}")
            elif feature == ".temperature":
                self.print("Enter a value between 0.0 and 2.0:")
                self.print("(Lower values for temperature result in more consistent outputs, while higher values generate more diverse and creative results. Select a temperature value based on the desired trade-off between coherence and creativity for your specific application.)")
                temperature = self.prompts.simplePrompt(validator=FloatValidator(), default=str(config.chatGPTApiTemperature))
                if temperature and not temperature.strip().lower() == config.terminal_cancel_action:
                    temperature = float(temperature)
                    if temperature < 0:
                        temperature = 0
                    elif temperature > 2:
                        temperature = 2
                    config.chatGPTApiTemperature = round(temperature, 1)
                    self.print(f"ChatGPT Temperature entered: {temperature}")
            elif feature == ".changeapikey":
                self.changeAPIkey()
            else:
                userInput = feature
        return userInput

    def swapmultiline(self):
        self.multilineInput = not self.multilineInput
        self.print(f"Multi-line input {'enabled' if self.multilineInput else 'disabled'}!")

    def getCurrentDateTime(self):
        current_datetime = datetime.datetime.now()
        return current_datetime.strftime("%Y-%m-%d_%H_%M_%S")

    def saveChat(self, messages, openFile=False):
        plainText = ""
        for i in messages:
            if i["role"] == "user":
                content = i["content"]
                plainText += f">>> {content}"
            if i["role"] == "function":
                if plainText:
                    plainText += "\n\n"
                name = i["name"]
                plainText += f"```\n{name}\n```"
                content = i["content"]
                plainText += f"\n\n{content}\n\n"
            elif i["role"] == "assistant":
                content = i["content"]
                if content is not None:
                    if plainText:
                        plainText += "\n\n"
                    plainText += f"{content}\n\n"
        plainText = plainText.strip()
        if config.terminalEnableTermuxAPI:
            pydoc.pipepager(plainText, cmd="termux-share -a send")
        else:
            try:
                #filename = re.sub('[\\\/\:\*\?\"\<\>\|]', "", messages[2 if config.chatGPTApiCustomContext.strip() else 1]["content"])[:40].strip()
                filename = self.getCurrentDateTime()
                if filename:
                    chatFile = os.path.join(config.myHandAIFolder, "chats", f"{filename}.txt")
                    with open(chatFile, "w", encoding="utf-8") as fileObj:
                        fileObj.write(plainText)
                    if openFile and os.path.isfile(chatFile):
                        os.system(f'''{config.open} "{chatFile}"''')
            except:
                self.print("Failed to save chat!\n")
                self.showErrors()

    def changeContext(self):
        contexts = list(config.predefinedContexts.keys())
        predefinedContext = self.dialogs.getValidOptions(
            options=contexts, 
            title="Predefined Contexts", 
            default=config.chatGPTApiPredefinedContext,
            text="Select a context:",
        )
        if predefinedContext:
            config.chatGPTApiPredefinedContext = predefinedContext
            if config.chatGPTApiPredefinedContext == "[custom]":
                self.print("Edit custom context below:")
                customContext = self.prompts.simplePrompt(default=config.chatGPTApiCustomContext)
                if customContext and not customContext.strip().lower() == config.terminal_cancel_action:
                    config.chatGPTApiCustomContext = customContext.strip()
            #print(f"Context selected: {config.chatGPTApiPredefinedContext}")
            self.showCurrentContext()

    def showCurrentContext(self):
        if config.chatGPTApiPredefinedContext == "[none]":
            context = "[none]"
        elif config.chatGPTApiPredefinedContext == "[custom]":
            context = f"[custom] {config.chatGPTApiCustomContext}"
        else:
            contextDescription = config.predefinedContexts[config.chatGPTApiPredefinedContext]
            context = f"[{config.chatGPTApiPredefinedContext}] {contextDescription}"
        self.print(self.divider)
        self.print(f"context: {context}")
        self.print(self.divider)

    def getDirectoryList(self):
        directoryList = []
        for f in os.listdir('.'):
            if os.path.isdir(f):
                separator = "\\" if config.thisPlatform == "Windows" else "/"
                directoryList.append(f"{f}{separator}")
            elif os.path.isfile(f):
                directoryList.append(f)
        return directoryList

    def startChats(self):
        messages = self.resetMessages()

        started = False

        def startChat():
            self.print(self.divider)
            try:
                from art import text2art
                self.print(text2art("myHand"))
            except:
                self.print(f"myHand AI")
            self.showCurrentContext()
            # go to startup directory
            self.currentDirectory = startupdirectory = config.startupdirectory if config.startupdirectory and os.path.isdir(config.startupdirectory) else config.myHandAIFolder
            os.chdir(startupdirectory)
            self.print(f"startup directory:\n{startupdirectory}")
            self.print(self.divider)

            started = False
        startChat()
        self.multilineInput = False
        features = (
            ".new",
            ".share" if config.terminalEnableTermuxAPI else ".save",
            ".swapmultiline",
            ".context",
            ".contextintensity",
            ".changeapikey",
            ".chatgptmodel",
            ".temperature",
            ".maxtokens",
            ".plugins",
            ".functioncall",
            ".functionresponse",
            ".latestSearches",
            ".pythonexecution",
            ".pythoncodedisplay",
            ".confirmpythonexecution",
            ".startupDirectory",
            ".developer",
            ".help",
        )
        featuresLower = [i.lower() for i in features] + ["...", ".save", ".share"]
        while True:
            # display current directory if changed
            currentDirectory = os.getcwd()
            if not currentDirectory == self.currentDirectory:
                self.print(self.divider)
                self.print(f"current directory:\n{currentDirectory}")
                self.print(self.divider)
            # default input entry
            defaultEntry = config.defaultEntry
            config.defaultEntry = ""
            # input suggestions
            inputSuggestions = config.inputSuggestions[:] + self.getDirectoryList() if config.developer else config.inputSuggestions
            completer = WordCompleter(inputSuggestions, ignore_case=True) if inputSuggestions else None
            userInput = self.prompts.simplePrompt(promptSession=self.terminal_chat_session, multiline=self.multilineInput, completer=completer, default=defaultEntry)
            # display options when empty string is entered
            if not userInput.strip():
                userInput = config.blankEntryAction
            if userInput.lower().strip() == "...":
                userInput = self.runOptions(features, userInput)
            if userInput.strip().lower() == config.terminal_cancel_action:
                self.saveChat(messages)
                return self.cancelAction()
            elif userInput.strip().lower() == ".swapmultiline":
                self.swapmultiline()
            elif userInput.strip().lower() == ".context":
                self.changeContext()
            elif userInput.strip().lower() == ".new" and started:
                self.saveChat(messages)
                messages = self.resetMessages()
                startChat()
            elif userInput.strip().lower() in (".share", ".save") and started:
                self.saveChat(messages, openFile=True)
            elif userInput.strip() and not userInput.strip().lower() in featuresLower:
                try:

                    # refine messages before running completion
                    fineTunedUserInput = self.fineTuneUserInput(userInput, started)

                    # python execution
                    self.screenAction = ""
                    if config.pythonExecution:
                        messages = self.pythonExecution(messages, fineTunedUserInput)
                    else:
                        messages.append({"role": "user", "content": fineTunedUserInput})

                    # start spinning
                    stop_event = threading.Event()
                    spinner_thread = threading.Thread(target=self.spinning_animation, args=(stop_event,))
                    spinner_thread.start()

                    # force loading internet searches
                    if config.loadingInternetSearches == "always" and not self.screenAction in ("python", "web"):
                        try:
                            messages = self.runFunction(messages, config.integrate_google_searches_signature, "integrate_google_searches")
                        except:
                            self.showErrors()
                            print("Unable to load internet resources.")

                    completion = self.runCompletion(messages)
                    # stop spinning
                    stop_event.set()
                    spinner_thread.join()

                    chat_response = ""
                    for event in completion:                                 
                        # RETRIEVE THE TEXT FROM THE RESPONSE
                        event_text = event["choices"][0]["delta"] # EVENT DELTA RESPONSE
                        answer = event_text.get("content", "") # RETRIEVE CONTENT
                        # STREAM THE ANSWER
                        if answer is not None:
                            chat_response += answer
                            print(answer, end='', flush=True) # Print the response
                    print("\n")
                    
                    # optional
                    # remove predefined context to reduce cost
                    #messages[-1] = {"role": "user", "content": userInput}
                    
                    messages.append({"role": "assistant", "content": chat_response})

                    started = True

                # error codes: https://platform.openai.com/docs/guides/error-codes/python-library-error-types
                except openai.error.APIError as e:
                    try:
                        stop_event.set()
                        spinner_thread.join()
                    except:
                        pass
                    #Handle API error here, e.g. retry or log
                    print(f"OpenAI API returned an API Error: {e}")
                except openai.error.APIConnectionError as e:
                    try:
                        stop_event.set()
                        spinner_thread.join()
                    except:
                        pass
                    #Handle connection error here
                    print(f"Failed to connect to OpenAI API: {e}")
                except openai.error.RateLimitError as e:
                    try:
                        stop_event.set()
                        spinner_thread.join()
                    except:
                        pass
                    #Handle rate limit error (we recommend using exponential backoff)
                    print(f"OpenAI API request exceeded rate limit: {e}")
                except:
                    try:
                        stop_event.set()
                        spinner_thread.join()
                    except:
                        pass
                    trace = traceback.format_exc()
                    if "Please reduce the length of the messages or completion" in trace:
                        self.print("Maximum tokens reached!")
                    elif config.developer:
                        print(self.divider)
                        self.print(trace)
                        print(self.divider)
                    else:
                        self.print("Errors!")
                    
                    config.defaultEntry = userInput
                    self.print("starting a new chat!")
                    self.saveChat(messages)
                    messages = self.resetMessages()
                    startChat()

    def checkCompletion(self):
        openai.api_key = os.environ["OPENAI_API_KEY"] = config.openaiApiKey
        try:
            openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content" : "hello"}],
                n=1,
                temperature=0.0,
                max_tokens=10,
            )
        except openai.error.APIError as e:
            self.print("Error: Issue on OpenAI side.")
            self.print("Solution: Retry your request after a brief wait and contact us if the issue persists.")
        except openai.error.Timeout as e:
            self.print("Error: Request timed out.")
            self.print("Solution: Retry your request after a brief wait and contact us if the issue persists.")
        except openai.error.RateLimitError as e:
            self.print("Error: You have hit your assigned rate limit.")
            self.print("Solution: Pace your requests. Read more in OpenAI [Rate limit guide](https://platform.openai.com/docs/guides/rate-limits).")
        except openai.error.APIConnectionError as e:
            self.print("Error: Issue connecting to our services.")
            self.print("Solution: Check your network settings, proxy configuration, SSL certificates, or firewall rules.")
        except openai.error.InvalidRequestError as e:
            self.print("Error: Your request was malformed or missing some required parameters, such as a token or an input.")
            self.print("Solution: The error message should advise you on the specific error made. Check the [documentation](https://platform.openai.com/docs/api-reference/) for the specific API method you are calling and make sure you are sending valid and complete parameters. You may also need to check the encoding, format, or size of your request data.")
        except openai.error.AuthenticationError as e:
            self.print("Error: Your API key or token was invalid, expired, or revoked.")
            self.print("Solution: Check your API key or token and make sure it is correct and active. You may need to generate a new one from your account dashboard.")
            self.changeAPIkey()
        except openai.error.ServiceUnavailableError as e:
            self.print("Error: Issue on OpenAI servers. ")
            self.print("Solution: Retry your request after a brief wait and contact us if the issue persists. Check the [status page](https://status.openai.com).")
        except:
            self.print("Error!")
            self.showErrors()