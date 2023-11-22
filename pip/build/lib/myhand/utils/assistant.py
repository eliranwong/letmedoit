from myhand import config
import openai, threading, os, time, traceback, re, subprocess, json, pydoc, textwrap, string, shutil
from openai import OpenAI
try:
    import tiktoken
    tiktokenImported = True
except:
    tiktokenImported = False
from pathlib import Path
import pygments
from pygments.lexers.python import PythonLexer
from pygments.lexers.shell import BashLexer
#from pygments.lexers.markup import MarkdownLexer
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import clear
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit import print_formatted_text, HTML
from myhand.utils.terminal_mode_dialogs import TerminalModeDialogs
from myhand.utils.prompts import Prompts
from myhand.utils.promptValidator import FloatValidator, TokenValidator
from myhand.utils.get_path_prompt import GetPath
from myhand.utils.prompt_shared_key_bindings import swapTerminalColors
from myhand.utils.file_utils import FileUtil
from myhand.utils.terminal_system_command_prompt import SystemCommandPrompt
from myhand.utils.shared_utils import SharedUtil
from myhand.utils.tts_utils import TTSUtil
from myhand.plugins.bibleTools.utils.TextUtil import TextUtil


class MyHandAI:

    def __init__(self):
        #config.myHandAI = self
        self.prompts = Prompts()
        self.dialogs = TerminalModeDialogs(self)
        self.setup()
        self.runPlugins()

    def setup(self):
        self.models = list(SharedUtil.tokenLimits.keys())
        config.divider = self.divider = "--------------------"
        self.runPython = True
        if not hasattr(config, "accept_default"):
            config.accept_default = False
        if not hasattr(config, "defaultEntry"):
            config.defaultEntry = ""
        config.tempContent = ""
        config.tempChunk = ""
        config.chatGPTApiPredefinedContextTemp = ""
        config.systemCommandPromptEntry = ""
        config.pagerContent = ""
        self.addPagerContent = False
        # share the following methods in config so that they are accessible via plugins
        config.getFiles = self.getFiles
        config.stopSpinning = self.stopSpinning
        config.toggleMultiline = self.toggleMultiline
        config.print = self.print
        config.getWrappedHTMLText = self.getWrappedHTMLText
        config.fineTuneUserInput = self.fineTuneUserInput
        config.launchPager = self.launchPager
        config.addPagerText = self.addPagerText
        config.getFunctionMessageAndResponse = self.getFunctionMessageAndResponse
        config.runSpecificFuntion = ""

        # get path
        config.addPathAt = None
        self.getPath = GetPath(
            cancel_entry="",
            promptIndicatorColor=config.terminalPromptIndicatorColor2,
            promptEntryColor=config.terminalCommandEntryColor2,
            subHeadingColor=config.terminalHeadingTextColor,
            itemColor=config.terminalResourceLinkColor,
        )

        self.preferredDir = self.getPreferredDir()
        if (not config.historyParentFolder or not os.path.isdir(config.historyParentFolder)) and self.preferredDir:
            try:
                historyParentFolder = os.path.join(self.preferredDir, "history")
                Path(historyParentFolder).mkdir(parents=True, exist_ok=True)
                for i in ("chats", "paths", "commands"):
                    historyFile = os.path.join(historyParentFolder, i)
                    if not os.path.isfile(historyFile):
                        open(historyFile, "a", encoding="utf-8").close()
                config.historyParentFolder = self.preferredDir
            except:
                config.historyParentFolder = ""
            config.saveConfig()
        
        if not config.openaiApiKey:
            self.changeAPIkey()

        if not config.openaiApiKey:
            self.print("ChatGPT API key not found!")
            self.print("Read https://github.com/eliranwong/myhand/wiki/ChatGPT-API-Key")
            exit(0)

        # required
        self.checkCompletion()
        # optional
        #if config.openaiApiOrganization:
        #    raise Exception("The 'openai.organization' option isn't read in the client API. You will need to pass it when you instantiate the client, e.g. 'OpenAI(organization=config.openaiApiOrganization)'")
        # chat records
        chat_history = os.path.join(config.historyParentFolder if config.historyParentFolder else config.myHandAIFolder, "history", "chats")
        self.terminal_chat_session = PromptSession(history=FileHistory(chat_history))

        # check if tts is ready
        if not config.isVlcPlayerInstalled and not config.isPygameInstalled and not config.ttsCommand:
            config.tts = False
        else:
            config.tts = True
        self.isTtsAvailable()

    def getPreferredDir(self):
        preferredDir = os.path.join(os.path.expanduser('~'), 'myhand')
        try:
            Path(preferredDir).mkdir(parents=True, exist_ok=True)
        except:
            pass
        return preferredDir if os.path.isdir(preferredDir) else ""

    def getFiles(self):
        if config.startupdirectory and not os.path.isdir(config.startupdirectory):
            config.startupdirectory = ""
        preferredDir = self.preferredDir if self.preferredDir else os.path.join(config.myHandAIFolder, "files")
        return config.startupdirectory if config.startupdirectory else preferredDir

    def getFolderPath(self):
        return self.getPath.getFolderPath(
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

    def execPythonFile(self, script="", content=""):
        if script or content:
            def runCode(text):
                code = compile(text, script, 'exec')
                exec(code, globals())
            try:
                if content:
                    runCode(content)
                else:
                    with open(script, 'r', encoding='utf8') as f:
                        runCode(f.read())
            except:
                self.print("Failed to run '{0}'!".format(os.path.basename(script)))
                SharedUtil.showErrors()

    def runPlugins(self):
        # The following config values can be modified with plugins, to extend functionalities
        config.pluginsWithFunctionCall = []
        config.aliases = {}
        config.predefinedContexts = {
            "[none]": "",
            "[custom]": "",
        }
        config.predefinedInstructions = {}
        config.inputSuggestions = []
        config.chatGPTTransformers = []
        config.chatGPTApiFunctionSignatures = []
        config.chatGPTApiAvailableFunctions = {}

        pluginFolder = os.path.join(config.myHandAIFolder, "plugins")
        # always run 'integrate google searches'
        internetSeraches = "integrate google searches"
        script = os.path.join(pluginFolder, "{0}.py".format(internetSeraches))
        self.execPythonFile(script)
        # always include the following plugins
        requiredPlugins = ("auto heal python code",)
        for i in requiredPlugins:
            if i in config.chatGPTPluginExcludeList:
                config.chatGPTPluginExcludeList.remove(i)
        # execute enabled plugins
        for plugin in FileUtil.fileNamesWithoutExtension(pluginFolder, "py"):
            if not plugin in config.chatGPTPluginExcludeList:
                script = os.path.join(pluginFolder, "{0}.py".format(plugin))
                self.execPythonFile(script)
        if internetSeraches in config.chatGPTPluginExcludeList:
            del config.chatGPTApiFunctionSignatures[0]
        self.setupPythonExecution()
        if config.terminalEnableTermuxAPI:
            self.setupTermuxExecution()
        for i in config.pluginsWithFunctionCall:
            config.inputSuggestions.append(f"[CALL {i}]")

    def selectPlugins(self):
        plugins = []
        enabledPlugins = []
        pluginFolder = os.path.join(config.myHandAIFolder, "plugins")
        for plugin in FileUtil.fileNamesWithoutExtension(pluginFolder, "py"):
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
            apikey = self.prompts.simplePrompt(default=config.openaiApiKey, is_password=True)
            if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
                config.openaiApiKey = apikey
            #self.print("Enter your Organization ID [optional]:")
            #oid = self.prompts.simplePrompt(default=config.openaiApiOrganization, is_password=True)
            #if oid and not oid.strip().lower() in (config.cancel_entry, config.exit_entry):
            #    config.openaiApiOrganization = oid
            self.checkCompletion()
            config.saveConfig()
            self.print("Updated!")

    def exitAction(self):
        message = "closing ..."
        self.print(message)
        self.print(self.divider)
        return ""

    def wrapText(self, content, terminal_width):
        return "\n".join([textwrap.fill(line, width=terminal_width) for line in content.split("\n")])

    def print(self, content):
        content = SharedUtil.transformText(content)
        if config.wrapWords:
            # wrap words to fit terminal width
            terminal_width = shutil.get_terminal_size().columns
            print(self.wrapText(content, terminal_width))
            # remarks: 'fold' or 'fmt' does not work on Windows
            # pydoc.pipepager(f"{content}\n", cmd=f"fold -s -w {terminal_width}")
            # pydoc.pipepager(f"{content}\n", cmd=f"fmt -w {terminal_width}")
        else:
            print(content)

    def spinning_animation(self, stop_event):
        while not stop_event.is_set():
            for symbol in '|/-\\':
                print(symbol, end='\r')
                time.sleep(0.1)

#    def getChatResponse(self, completion):
#        chat_response = completion["choices"][0]["message"]["content"]
#        # transform response with plugins
#        if chat_response:
#            for t in config.chatGPTTransformers:
#                chat_response = t(chat_response)
#        return chat_response

    def confirmExecution(self, risk):
        if config.confirmExecution == "always" or (risk == "high" and config.confirmExecution == "high_risk_only") or (not risk == "low" and config.confirmExecution == "medium_risk_or_above"):
            return True
        else:
            return False

    def showRisk(self, risk):
        if not config.confirmExecution in ("always", "medium_risk_or_above", "high_risk_only", "none"):
            config.confirmExecution = "always"
        self.print(f"[risk level: {risk}]")

    def setupTermuxExecution(self):
        def execute_termux_command(function_args):
            # retrieve argument values from a dictionary
            risk = function_args.get("risk") # required
            title = function_args.get("title") # required
            #sharedText = function_args.get("message", "") # optional
            function_args = textwrap.dedent(function_args.get("code")).strip() # required
            sharedText = re.sub("^termux-share .*?'([^']+?)'$", r"\1", function_args)
            sharedText = re.sub('^termux-share .*?"([^"]+?)"$', r"\1", sharedText)
            sharedText = re.sub("""^[\d\D]*?subprocess.run\(\['termux-share'[^\[\]]*?'([^']+?)'\]\)[\d\D]*?$""", r"\1", sharedText)
            sharedText = re.sub('''^[\d\D]*?subprocess.run\(\["termux-share"[^\[\]]*?"([^']+?)"\]\)[\d\D]*?$''', r"\1", sharedText)
            function_args = function_args if sharedText == function_args else f'''termux-share -a send "{sharedText}"'''

            # show Termux command for developer
            self.print(self.divider)
            self.print(f"Termux: {title}")
            self.showRisk(risk)
            if config.developer or config.codeDisplay:
                self.print("```")
                #print(function_args)
                tokens = list(pygments.lex(function_args, lexer=BashLexer()))
                print_formatted_text(PygmentsTokens(tokens), style=SharedUtil.getPygmentsStyle())
                self.print("```")
            self.print(self.divider)

            self.stopSpinning()
            if self.confirmExecution(risk):
                self.print("Do you want to execute it? [y]es / [N]o")
                confirmation = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default="y")
                if not confirmation.lower() in ("y", "yes"):
                    return "[INVALID]"

            try:
                if not sharedText == function_args:
                    pydoc.pipepager(sharedText, cmd="termux-share -a send")
                    function_response = "Done!"
                else:
                    # display both output and error
                    function_response = SharedUtil.runSystemCommand(function_args)
                self.print(function_response)
            except:
                SharedUtil.showErrors()
                self.print(self.divider)
                return "[INVALID]"
            info = {"information": function_response}
            function_response = json.dumps(info)
            return json.dumps(info)

        functionSignature = {
            "name": "execute_termux_command",
            "description": "Execute Termux command on Android",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Termux command, e.g. am start -n com.android.chrome/com.google.android.apps.chrome.Main",
                    },
                    "title": {
                        "type": "string",
                        "description": "title for the termux command",
                    },
                    "risk": {
                        "type": "string",
                        "description": "Assess the risk level of damaging my device upon executing the task. e.g. file deletions or similar significant impacts are regarded as 'high' level.",
                        "enum": ["high", "medium", "low"],
                    },
                },
                "required": ["code", "title", "risk"],
            },
        }

        config.execute_termux_command_signature = [functionSignature]
        # useful when enhanced mode is disabled
        config.chatGPTApiFunctionSignatures.append(functionSignature)
        config.chatGPTApiAvailableFunctions["execute_termux_command"] = execute_termux_command

    def setupPythonExecution(self):
        def execute_python_code(function_args):
            # retrieve argument values from a dictionary
            risk = function_args.get("risk") # required
            title = function_args.get("title") # required
            python_code = function_args.get("code") # required
            refinedCode = SharedUtil.fineTunePythonCode(python_code)

            # show pyton code for developer
            self.print(self.divider)
            self.print(f"Python: {title}")
            self.showRisk(risk)
            if config.developer or config.codeDisplay:
                self.print("```")
                #print(python_code)
                # pygments python style
                tokens = list(pygments.lex(python_code, lexer=PythonLexer()))
                print_formatted_text(PygmentsTokens(tokens), style=SharedUtil.getPygmentsStyle())
                self.print("```")
            self.print(self.divider)

            self.stopSpinning()
            if not self.runPython:
                return "[INVALID]"
            elif self.confirmExecution(risk):
                self.print("Do you want to execute it? [y]es / [N]o")
                confirmation = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default="y")
                if not confirmation.lower() in ("y", "yes"):
                    self.runPython = False
                    return "[INVALID]"
            return SharedUtil.executePythonCode(refinedCode)

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
                    "risk": {
                        "type": "string",
                        "description": "Assess the risk level of damaging my device upon executing the task. e.g. file deletions or similar significant impacts are regarded as 'high' level.",
                        "enum": ["high", "medium", "low"],
                    },
                },
                "required": ["code", "title", "risk"],
            },
        }

        config.execute_python_code_signature = [functionSignature]
        # useful when enhanced mode is disabled
        config.chatGPTApiFunctionSignatures.append(functionSignature)
        config.chatGPTApiAvailableFunctions["execute_python_code"] = execute_python_code

    def screening(self, messages, userInput):
        self.print("enhanced screening ...")

        messagesCopy = messages[:]

        if config.terminalEnableTermuxAPI:
            context = """In response to the following request, answer me either "termux" or "python" or "chat" without extra comments.
Answer "python" only if you can write python code to get the requested information or carry out the requested task, e.g. open a web browser.
Answer "termux" only if you can write a Termux commands to get the requested information or carry out the requested task on Android, e.g. open Google Chrome.
Answer "chat" if I explicitly ask you "do not execute" or if I start my request with "how".
Otherwise, answer "chat". Here is the request:"""
        else:
            context = """In response to the following request, answer me either "python" or "chat" without extra comments.
Answer "python" only if you can write python code to get the requested information or carry out the requested task, e.g. open a web browser.
Answer "chat" if I explicitly ask you "do not execute" or if I start my request with "how".
Otherwise, answer "chat". Here is the request:"""

        messagesCopy.append({"role": "user", "content": f"{context} {userInput}"})
        completion = self.client.chat.completions.create(
            model=config.chatGPTApiModel,
            messages=messagesCopy,
            n=1,
            temperature=0.0,
            max_tokens=SharedUtil.getDynamicTokens(messagesCopy),
        )
        answer = completion.choices[0].message.content
        self.screenAction = answer = re.sub("[^A-Za-z]", "", answer).lower()

        self.print("screening done!")

        if answer == "termux":
            context = """I am running Turmux terminal on this Android device.\nFind my device information below:\n```\n{SharedUtil.getDeviceInfo()}\n```\nExecute Termux command or python code to achieve the following tasks."""
            userInputWithcontext = f"{context}\n{userInput}"
            messages.append({"role": "user", "content" : userInputWithcontext})
            messages = self.runFunction(messages, config.execute_termux_command_signature, "execute_termux_command")
            if messages[-1]["content"] == "[INVALID]":
                # remove messages for command execution
                messages = messages[:-3]
            else:
                return messages
        elif answer == "python":
            context = f"""Find my device information below:\n```\n{SharedUtil.getDeviceInfo()}\n```\nExecute python code to achieve the following tasks."""
            userInputWithcontext = f"{context}\n{userInput}"
            messages.append({"role": "user", "content" : userInputWithcontext})
            messages = self.runFunction(messages, config.execute_python_code_signature, "execute_python_code")
            if messages[-1]["content"] == "[INVALID]":
                # remove messages for command execution
                messages = messages[:-3]
            else:
                return messages
        #elif answer == "web":
        #    messages.append({"role": "user", "content" : userInput})
        #    return self.runFunction(messages, config.integrate_google_searches_signature, "integrate_google_searches")
        messages.append({"role": "user", "content" : userInput})
        return messages

    # call a specific function and return messages
    def runFunction(self, messages, functionSignatures, function_name):
        messagesCopy = messages[:]
        try:
            function_call_message, function_call_response = self.getFunctionMessageAndResponse(messages, functionSignatures, function_name)
            messages.append(function_call_message)
            messages.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_call_response if function_call_response else config.tempContent,
                }
            )
            config.tempContent = ""
        except:
            SharedUtil.showErrors()
            return messagesCopy
        return messages

    def getFunctionMessageAndResponse(self, messages, functionSignatures, function_name, temperature=None):
        completion = self.client.chat.completions.create(
            model=config.chatGPTApiModel,
            messages=messages,
            max_tokens=SharedUtil.getDynamicTokens(messages, functionSignatures),
            temperature=temperature if temperature is not None else config.chatGPTApiTemperature,
            n=1,
            tools=SharedUtil.convertFunctionSignaturesIntoTools(functionSignatures),
            tool_choice={"type": "function", "function": {"name": function_name}},
        )
        function_call_message = completion.choices[0].message
        tool_call = function_call_message.tool_calls[0]
        func_arguments = tool_call.function.arguments
        function_call_message_mini = {
            "role": "assistant",
            "content": "",
            "function_call": {
                "name": tool_call.function.name,
                "arguments": func_arguments,
            }
        }
        function_call_response = self.getFunctionResponse(func_arguments, function_name)
        return function_call_message_mini, function_call_response

    def getFunctionResponse(self, func_arguments, function_name):
        # ChatGPT's built-in function named "python"
        if function_name == "python":
            python_code = textwrap.dedent(func_arguments)
            refinedCode = SharedUtil.fineTunePythonCode(python_code)

            self.print(self.divider)
            self.print(f"running python code ...")
            risk = SharedUtil.riskAssessment(python_code)
            self.showRisk(risk)
            if config.developer or config.codeDisplay:
                print("```")
                #print(python_code)
                # pygments python style
                tokens = list(pygments.lex(python_code, lexer=PythonLexer()))
                print_formatted_text(PygmentsTokens(tokens), style=SharedUtil.getPygmentsStyle())
                print("```")
            self.print(self.divider)

            self.stopSpinning()
            if not self.runPython:
                info = {"information": python_code}
                return json.dumps(info)
            elif self.confirmExecution(risk):
                self.print("Do you want to continue? [y]es / [N]o")
                confirmation = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default="y")
                if not confirmation.lower() in ("y", "yes"):
                    info = {"information": python_code}
                    return json.dumps(info)
            try:
                exec(refinedCode, globals())
                function_response = SharedUtil.getPythonFunctionResponse(refinedCode)
            except:
                trace = SharedUtil.showErrors()
                self.print(self.divider)
                if config.max_consecutive_auto_heal > 0:
                    return SharedUtil.autoHealPythonCode(refinedCode, trace)
                else:
                    return "[INVALID]"
            if function_response:
                info = {"information": function_response}
                function_response = json.dumps(info)
        elif not function_name in config.chatGPTApiAvailableFunctions:
            # handle unexpected function
            self.print(f"Unexpected function: {function_name}")
            self.print(self.divider)
            print(func_arguments)
            self.print(self.divider)
            function_response = ""
        else:
            fuction_to_call = config.chatGPTApiAvailableFunctions[function_name]
            # convert the arguments from json into a dict
            function_args = json.loads(func_arguments)
            function_response = fuction_to_call(function_args)
        return function_response

    def runCompletion(self, thisMessage, noFunctionCall=False):
        self.functionJustCalled = False
        def runThisCompletion(thisThisMessage):
            if config.chatGPTApiFunctionSignatures and not self.functionJustCalled and not noFunctionCall:
                return self.client.chat.completions.create(
                    model=config.chatGPTApiModel,
                    messages=thisThisMessage,
                    n=1,
                    temperature=config.chatGPTApiTemperature,
                    max_tokens=SharedUtil.getDynamicTokens(thisThisMessage, config.chatGPTApiFunctionSignatures),
                    tools=SharedUtil.convertFunctionSignaturesIntoTools(config.chatGPTApiFunctionSignatures),
                    tool_choice={"type": "function", "function": {"name": config.runSpecificFuntion}} if config.runSpecificFuntion else config.chatGPTApiFunctionCall,
                    stream=True,
                )
            return self.client.chat.completions.create(
                model=config.chatGPTApiModel,
                messages=thisThisMessage,
                n=1,
                temperature=config.chatGPTApiTemperature,
                max_tokens=SharedUtil.getDynamicTokens(thisThisMessage),
                stream=True,
            )

        while True:
            completion = runThisCompletion(thisMessage)
            config.runSpecificFuntion = ""
            try:
                # consume the first delta
                for event in completion:
                    first_delta = event.choices[0].delta
                    # check if a tool is called
                    if first_delta.tool_calls: # a tool is called
                        function_calls = [i for i in first_delta.tool_calls if i.type == "function"]
                        # non_function_calls = [i for i in first_delta.tool_calls if not i.type == "function"]
                    else: # no tool is called; same treatment as tool calls are finished
                        self.functionJustCalled = True
                    # consume the first delta only at this point
                    break
                # Continue only when a function is called
                if self.functionJustCalled:
                    break

                # get all tool arguments, both of functions and non-functions
                toolArguments = SharedUtil.getToolArgumentsFromStreams(completion)

                func_responses = ""
                # handle function calls
                for func in function_calls:
                    func_index = func.index
                    func_id = func.id
                    func_name = func.function.name
                    func_arguments = toolArguments[func_index]

                    # get function response
                    func_response = self.getFunctionResponse(func_arguments, func_name)

                    if not func_response == "[INVALID]":
                        # send the function call info and response to GPT
                        function_call_message = {
                            "role": "assistant",
                            "content": "",
                            "function_call": {
                                "name": func_name,
                                "arguments": func_arguments,
                            }
                        }
                        thisMessage.append(function_call_message) # extend conversation with assistant's reply
                        thisMessage.append(
                            {
                                "tool_call_id": func_id,
                                "role": "function",
                                "name": func_name,
                                "content": func_response if func_response else "",
                            }
                        )  # extend conversation with function response
                        if func_response:
                            func_responses += f"\n{func_response}\n{config.divider}"

                self.functionJustCalled = True

                if not config.chatAfterFunctionCalled or not func_responses:
                    if func_responses:
                        self.print(f"{config.divider}\n{func_responses}")
                    break
            except:
                SharedUtil.showErrors()
                break

        return completion

    # reset message when a new chart is started or context is changed
    def resetMessages(self):
        systemMessage = f"You’re MyHand Bot, an advanced AI assistant, capable of both engaging in conversations and executing codes on my device.\nFind my device information below:\n```\n{SharedUtil.getDeviceInfo()}\n```\nYou have all permissions to execute {'Termux commands, ' if config.terminalEnableTermuxAPI else ''}system commands and python codes on my behalf."
        if config.chatGPTApiFunctionCall == "auto" and config.chatGPTApiFunctionSignatures:
            systemMessage += " Your functionality expands as I add more plugins to you. Only use the functions you have been provided with."
        messages = [
            {"role": "system", "content": systemMessage}
        ]
        return messages

    # in a long conversation, ChatGPT often forgets its system message
    # enhance system message by moving it forward
    def moveForwardSystemMessage(self, messages):
        for index, message in enumerate(messages):
            try:
                if message.get("role", "") == "system":
                    # update system mess
                    dayOfWeek = SharedUtil.getDayOfWeek()
                    item = messages.pop(index)
                    item["content"] = re.sub(
                        """^Current directory: .*?\nCurrent time: .*?\nCurrent day of the week: .*?$""",
                        f"""Current directory: {os.getcwd()}\nCurrent time: {str(datetime.datetime.now())}\nCurrent day of the week: {dayOfWeek}""",
                        item["content"],
                        flags=re.M,
                    )
                    messages.append(item)
                    break
            except:
                pass
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
        return context

    def fineTuneUserInput(self, userInput):
        # customise chat context
        context = self.getCurrentContext()
        if context and (not config.conversationStarted or (config.conversationStarted and config.chatGPTApiContextInAllInputs)):
            # context may start with "You will be provided with my input delimited with a pair of XML tags, <input> and </input>. ...
            userInput = re.sub("<content>|<content [^<>]*?>|</content>", "", userInput)
            userInput = f"{context}\n<content>{userInput}</content>" if userInput.strip() else context
        #userInput = SharedUtil.addTimeStamp(userInput)
        if config.chatGPTApiPredefinedContextTemp:
            config.chatGPTApiPredefinedContext = config.chatGPTApiPredefinedContextTemp
            config.chatGPTApiPredefinedContextTemp = ""
        return userInput

    def runOptions(self, features, userInput):
        descriptions = (
            "start a new chat [ctrl+n]",
            "share content [ctrl+s]" if config.terminalEnableTermuxAPI else "save content [ctrl+s]",
            "swap text brightness [esc+s]",
            "run an instruction",
            "change chat context [ctrl+o]",
            "change chat context inclusion",
            "change API key",
            "change ChatGPT model",
            "change ChatGPT temperature",
            "change maximum response tokens",
            "change minimum response tokens",
            "change maximum consecutive auto-heal",
            "change plugins",
            "change function call",
            "change function response",
            "change online searches",
            "change execution mode [ctrl+e]",
            "change user confirmation",
            "change command display",
            "change pager view",
            "change startup directory",
            "change Termux API integration",
            "change automatic upgrade",
            "change developer mode [ctrl+d]",
            "toggle multi-line input [ctrl+l]",
            "toogle mouse support [esc+m]",
            "toggle word wrap [ctrl+w]",
            "toggle improved writing [esc+i]",
            "toggle input audio [ctrl+b]",
            "toggle response audio [ctrl+p]",
            "configure text-to-speech command",
            "open system command prompt",
            "open myHand wiki",
            "display key bindings",
        )
        feature = self.dialogs.getValidOptions(
            options=features,
            descriptions=descriptions,
            title="MyHand Bot",
            default=config.defaultBlankEntryAction,
            text="Select an action or make changes:",
        )
        if feature:
            if feature == ".chatgptmodel":
                self.setModel()
            elif feature == ".latestSearches":
                self.setLatestSearches()
            elif feature == ".startupDirectory":
                self.setStartupDirectory()
            elif feature == ".contextinclusion":
                self.setContextInclusion()
            elif feature == ".codedisplay":
                self.setCodeDisplay()
            elif feature == ".confirmexecution":
                self.setUserConfirmation()
            elif feature == ".plugins":
                self.selectPlugins()
            elif feature == ".keys":
                config.showKeyBindings()
            elif feature == ".help":
                SharedUtil.openURL('https://github.com/eliranwong/myhand/wiki')
            elif feature == ".pagerview":
                self.setPagerView()
            elif feature == ".developer":
                self.setDeveloperMode()
            elif feature == ".autoupgrade":
                self.setAutoUpgrade()
            elif feature == ".termuxapi":
                self.setTermuxApi()
            elif feature == ".enhanceexecution":
                self.setCommandExecutionMode()
            elif feature == ".functioncall":
                self.setFunctionCall()
            elif feature == ".functionresponse":
                self.setFunctionResponse()
            elif feature == ".mintokens":
                self.setMinTokens()
            elif feature == ".maxtokens":
                self.setMaxTokens()
            elif feature == ".maxautoheal":
                self.setMaxAutoHeal()
            elif feature == ".temperature":
                self.setTemperature()
            elif feature == ".changeapikey":
                self.changeAPIkey()
            else:
                userInput = feature
        return userInput

    def setAutoUpgrade(self):
        options = ("enable", "disable")
        option = self.dialogs.getValidOptions(
            options=options,
            title="Automatic Upgrade on Startup",
            default="enable" if config.autoUpgrade else "disable",
            text="Select an option below:"
        )
        if option:
            config.autoUpgrade = (option == "enable")
            config.saveConfig()
            self.print(f"Automatic Upgrade: {option}d!")

    def setCodeDisplay(self):
        options = ("enable", "disable")
        option = self.dialogs.getValidOptions(
            options=options,
            title="Command / Code Display",
            default="enable" if config.codeDisplay else "disable",
            text="Options to display commands / codes before execution:"
        )
        if option:
            config.codeDisplay = (option == "enable")
            config.saveConfig()
            self.print(f"Command / Code display: {option}d!")

    def setContextInclusion(self):
        options = ("the first input only", "all inputs")
        option = self.dialogs.getValidOptions(
            options=options,
            title="Predefined Context Inclusion",
            default="all inputs" if config.chatGPTApiContextInAllInputs else "the first input only",
            text="Define below how you want to include predefined context\nwith your inputs.\nApply predefined context in ...",
        )
        if option:
            config.chatGPTApiContextInAllInputs = True if option == "all inputs" else False
            config.saveConfig()
            self.print(f"Predefined Context Inclusion: {option}!")

    def setStartupDirectory(self):
        try:
            folder = self.getFolderPath()
        except:
            self.print(f"Given path not accessible!")
            folder = ""
        if folder and os.path.isdir(folder):
            config.startupdirectory = folder
            config.saveConfig()
            self.print(f"Startup directory changed to:\n{folder}")

    def setLatestSearches(self):
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
            # reset plugins
            self.runPlugins()
            # notify
            config.saveConfig()
            self.print(f"Latest Online Searches: {option}")

    def setUserConfirmation(self):
        options = ("always", "medium_risk_or_above", "high_risk_only", "none")
        if not config.confirmExecution in options:
            config.confirmExecution = "always"
        descriptions = (
            "always",
            "medium risk or above",
            "high risk only, e.g. file deletion",
            "none",
        )
        option = self.dialogs.getValidOptions(
            options=options,
            descriptions=descriptions,
            title="Command Execution Confirmation",
            text="MyHand Bot can execute commands on your behalf.\nWhen do you want confirmation\nbefore commands are executed:\n(caution: execute commands at your own risk)",
            default=config.confirmExecution,
        )
        if option:
            config.confirmExecution = option
            config.saveConfig()
            self.print(f"Command execution confirmation: {option}")

    def setPagerView(self):
        options = ("auto", "manual [ctrl+g]")
        option = self.dialogs.getValidOptions(
            options=options,
            title="Pager View",
            default="auto" if config.pagerView else "manual [ctrl+g]",
        )
        if option:
            config.pagerView = (option == "auto")
            config.saveConfig()
            self.print(f"Pager View: {option}!")

    def setDeveloperMode(self):
        options = ("enable", "disable")
        option = self.dialogs.getValidOptions(
            options=options,
            title="Developer Mode",
            default="enable" if config.developer else "disable",
            text="Read myHand wiki for more information.\nSelect an option below:"
        )
        if option:
            config.developer = (option == "enable")
            config.saveConfig()
            self.print(f"Developer Mode: {option}d!")

    def setTermuxApi(self):
        options = ("enable", "disable")
        option = self.dialogs.getValidOptions(
            options=options,
            title="Termux API Integration",
            default="enable" if config.terminalEnableTermuxAPI else "disable",
            text="To learn about Termux API, read:\nhttps://wiki.termux.com/wiki/Termux:API\nSelect an option below:"
        )
        if option:
            config.terminalEnableTermuxAPI = (option == "enable")
            if config.terminalEnableTermuxAPI and not os.path.isdir("/data/data/com.termux/files/home/"):
                config.terminalEnableTermuxAPI = False
                self.print("Termux is not installed!")
            if config.terminalEnableTermuxAPI:
                # Check if Termux API package is installed
                result = subprocess.run(['pkg', 'list-installed', 'termux-api'], capture_output=True, text=True)
                # Check if the package is installed
                if not "termux-api" in result.stdout:
                    self.print("Termux:API is not installed!")
            # reset plugins
            self.runPlugins()
            config.saveConfig()
            self.print(f"""Termux API Integration: {"enable" if config.terminalEnableTermuxAPI else "disable"}d!""")

    def setCommandExecutionMode(self):
        options = ("enhanced", "auto")
        option = self.dialogs.getValidOptions(
            options=options,
            title="Command Execution Mode",
            default="enhanced" if config.enhanceCommandExecution else "auto",
            text="myHand can execute commands\nto retrieve the requested information\nor perform tasks for users.\n(read https://github.com/eliranwong/myhand/wiki/Command-Execution)\nSelect a mode below:",
        )
        if option:
            config.enhanceCommandExecution = (option == "enhanced")
            config.saveConfig()
            self.print(f"Command Execution Mode: {option}")

    def setFunctionCall(self):
        calls = ("auto", "none")
        call = self.dialogs.getValidOptions(
            options=calls,
            title="ChatGPT Function Call",
            default=config.chatGPTApiFunctionCall,
            text="Enabling function call\nallows online searches\nor other third-party features\nto extend ChatGPT capabilities.\nEnable / Disable this feature below:",
        )
        if call:
            config.chatGPTApiFunctionCall = call
            config.saveConfig()
            self.print(f"ChaptGPT function call: {'enabled' if config.chatGPTApiFunctionCall == 'auto' else 'disabled'}!")

    def setFunctionResponse(self):
        calls = ("enable", "disable")
        call = self.dialogs.getValidOptions(
            options=calls,
            title="Automatic Chat Generation with Function Response",
            default="enable" if config.chatAfterFunctionCalled else "disable",
            text="Enable this feature\nto generate further responses\naccording to function call results.\nDisable this feature allows\nperforming function calls\nwihtout generating further responses."
        )
        if call:
            config.chatAfterFunctionCalled = (call == "enable")
            config.saveConfig()
            self.print(f"Automatic Chat Generation with Function Response: {'enabled' if config.chatAfterFunctionCalled else 'disabled'}!")

    def setTemperature(self):
        self.print("Enter a value between 0.0 and 2.0:")
        self.print("(Lower values for temperature result in more consistent outputs, while higher values generate more diverse and creative results. Select a temperature value based on the desired trade-off between coherence and creativity for your specific application.)")
        temperature = self.prompts.simplePrompt(validator=FloatValidator(), default=str(config.chatGPTApiTemperature))
        if temperature and not temperature.strip().lower() == config.exit_entry:
            temperature = float(temperature)
            if temperature < 0:
                temperature = 0
            elif temperature > 2:
                temperature = 2
            config.chatGPTApiTemperature = round(temperature, 1)
            config.saveConfig()
            self.print(f"ChatGPT Temperature entered: {temperature}")

    def setModel(self):
        model = self.dialogs.getValidOptions(
            options=self.models,
            title="ChatGPT model",
            default=config.chatGPTApiModel,
            text="Select a ChatGPT model:",
        )
        if model:
            config.chatGPTApiModel = model
            self.print(f"ChatGPT model selected: {model}")
            # handle max tokens
            if tiktokenImported:
                functionTokens = SharedUtil.count_tokens_from_functions(config.chatGPTApiFunctionSignatures)
                tokenLimit = SharedUtil.tokenLimits[config.chatGPTApiModel] - functionTokens
            else:
                tokenLimit = SharedUtil.tokenLimits[config.chatGPTApiModel]
            suggestedMaxToken = int(tokenLimit / 2)
            #if config.chatGPTApiMaxTokens > suggestedMaxToken:
            config.chatGPTApiMaxTokens = suggestedMaxToken
            config.saveConfig()
            self.print(f"Maximum response tokens set to {config.chatGPTApiMaxTokens}.")

    def setMaxAutoHeal(self):
        self.print("The auto-heal feature enables MyHand Bot to automatically fix broken Python code if it was not executed properly.")
        self.print("Please specify maximum number of auto-heal attempts below:")
        self.print("(Remarks: Enter '0' if you want to disable auto-heal feature)")
        maxAutoHeal = self.prompts.simplePrompt(numberOnly=True, default=str(config.max_consecutive_auto_heal))
        if maxAutoHeal and not maxAutoHeal.strip().lower() == config.exit_entry and int(maxAutoHeal) >= 0:
            config.max_consecutive_auto_heal = int(maxAutoHeal)
            config.saveConfig()
            self.print(f"Maximum consecutive auto-heal entered: {config.max_consecutive_auto_heal}")

    def setMinTokens(self):
        self.print("Please specify minimum response tokens below:")
        mintokens = self.prompts.simplePrompt(numberOnly=True, default=str(config.chatGPTApiMinTokens))
        if mintokens and not mintokens.strip().lower() == config.exit_entry and int(mintokens) > 0:
            config.chatGPTApiMinTokens = int(mintokens)
            if config.chatGPTApiMinTokens > config.chatGPTApiMaxTokens:
                config.chatGPTApiMinTokens = config.chatGPTApiMaxTokens
            config.saveConfig()
            self.print(f"Minimum tokens entered: {config.chatGPTApiMinTokens}")

    def setMaxTokens(self):
        if tiktokenImported:
            functionTokens = SharedUtil.count_tokens_from_functions(config.chatGPTApiFunctionSignatures)
            tokenLimit = SharedUtil.tokenLimits[config.chatGPTApiModel] - functionTokens - config.chatGPTApiMinTokens
        else:
            tokenLimit = SharedUtil.tokenLimits[config.chatGPTApiModel]
        if tiktokenImported and tokenLimit < config.chatGPTApiMinTokens:
            self.print(f"Availble functions have already taken up too many tokens [{functionTokens}] to work with selected model '{config.chatGPTApiModel}'. You may either changing to a model that supports more tokens or deactivating some of the plugins that you don't need to reduce the number of tokens in total.")
        else:
            self.print(self.divider)
            if config.chatGPTApiModel == "gpt-4-1106-preview":
                self.print(f"You are using ChatGPT model '{config.chatGPTApiModel}'. This model supports at most 4096 completion tokens. You can set at most {tokenLimit} maximum response token below.")
            else:
                self.print(f"You are using ChatGPT model '{config.chatGPTApiModel}', which allows no more than {tokenLimit} tokens, including both prompt and response")
            self.print("(GPT and embeddings models process text in chunks called tokens. As a rough rule of thumb, 1 token is approximately 4 characters or 0.75 words for English text. One limitation to keep in mind is that for a GPT model the prompt and the generated output combined must be no more than the model's maximum context length.)")
            if tiktokenImported:
                self.print(f"Remarks: The current available functions have already taken up {functionTokens} tokens.")
            self.print(self.divider)
            self.print("Please specify maximum response tokens below:")
            maxtokens = self.prompts.simplePrompt(numberOnly=True, default=str(config.chatGPTApiMaxTokens))
            if maxtokens and not maxtokens.strip().lower() == config.exit_entry and int(maxtokens) > 0:
                config.chatGPTApiMaxTokens = int(maxtokens)
                if config.chatGPTApiMaxTokens > tokenLimit:
                    config.chatGPTApiMaxTokens = tokenLimit
                config.saveConfig()
                self.print(f"Maximum tokens entered: {config.chatGPTApiMaxTokens}")

    def runPythonScript(self, script):
        script = script.strip()[3:-3]
        try:
            exec(script, globals())
        except:
            trace = traceback.format_exc()
            print(trace if config.developer else "Error encountered!")
            self.print(self.divider)
            if config.max_consecutive_auto_heal > 0:
                SharedUtil.autoHealPythonCode(script, trace)

    def runSystemCommand(self, command):
        command = command.strip()[1:]
        if config.multilineInput:
            command = ";".join(command.split("\n"))
        os.system(command)

    def toggleMultiline(self):
        config.multilineInput = not config.multilineInput
        run_in_terminal(lambda: self.print(f"Multi-line input {'enabled' if config.multilineInput else 'disabled'}!"))
        if config.multilineInput:
            run_in_terminal(lambda: self.print("Use 'escape + enter' to complete your entry."))

    def isTtsAvailable(self):
        if config.tts:
            return True
        self.print("Text-to-speech feature not ready!\nTo, set up, either:\n* install 'VLC player'\n* install 'pygame'\n* define 'ttsCommand' in config.py")
        self.print("Read more at:\nhttps://github.com/eliranwong/myhand/wiki/myHand-Speaks")
        return False

    def toggleinputaudio(self):
        if self.isTtsAvailable:
            config.ttsInput = not config.ttsInput
            config.saveConfig()
            self.print(f"Input Audio '{'enabled' if config.ttsInput else 'disabled'}'!")

    def toggleresponseaudio(self):
        if self.isTtsAvailable:
            config.ttsOutput = not config.ttsOutput
            config.saveConfig()
            self.print(f"Response Audio '{'enabled' if config.ttsOutput else 'disabled'}'!")

    def defineTtsCommand(self):
        self.print("Define text-to-speech command below:")
        self.print("""* on macOS ['say -v "?"' to check voices], e.g.:\n'say' or 'say -r 200 -v Daniel'""")
        self.print("* on Ubuntu ['espeak --voices' to check voices], e.g.:\n'espeak' or 'espeak -s 175 -v en-gb'")
        self.print("* on Windows, simply enter 'windows' here to use Windows built-in speech engine") # myHand.bot will handle the command for Windows users
        self.print("remarks: always place the voice option, if any, at the end")
        ttsCommand = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.ttsCommand)
        if ttsCommand:
            self.print("Specify command suffix below, if any [leave it blank if N/A]:")
            ttsCommandSuffix = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.ttsCommandSuffix)
            if ttsCommand.lower() == "windows":
                command = f'''PowerShell -Command "Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('testing');"'''
                ttsCommandSuffix = ""
            else:
                command = f'''{ttsCommand} "testing"{ttsCommandSuffix}'''
            _, stdErr = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            if stdErr:
                SharedUtil.showErrors() if config.developer else self.print("Entered command invalid!")
            else:
                config.ttsCommand, config.ttsCommandSuffix = ttsCommand, ttsCommandSuffix
                config.saveConfig()
        else:
            config.ttsCommand, config.ttsCommandSuffix = "", ""

    def toggleWordWrap(self):
        config.wrapWords = not config.wrapWords
        config.saveConfig()
        self.print(f"Word Wrap '{'enabled' if config.wrapWords else 'disabled'}'!")

    def toggleMouseSupport(self):
        config.mouseSupport = not config.mouseSupport
        config.saveConfig()
        self.print(f"Entry Mouse Support '{'enabled' if config.mouseSupport else 'disabled'}'!")

    def toggleImprovedWriting(self):
        config.displayImprovedWriting = not config.displayImprovedWriting
        if config.displayImprovedWriting:
            self.print("Please specify the writing style below:")
            style = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.improvedWritingSytle)
            if style and not style in (config.exit_entry, config.cancel_entry):
                config.improvedWritingSytle = style
                config.saveConfig()
        self.print(f"Improved Writing Display '{'enabled' if config.displayImprovedWriting else 'disabled'}'!")

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
                filename = SharedUtil.getCurrentDateTime()
                foldername = os.path.join(self.getFiles(), "chats", re.sub("^([0-9]+?\-[0-9]+?)\-.*?$", r"\1", filename))
                Path(foldername).mkdir(parents=True, exist_ok=True)
                if filename:
                    chatFile = os.path.join(foldername, f"{filename}.txt")
                    with open(chatFile, "w", encoding="utf-8") as fileObj:
                        fileObj.write(plainText)
                    if openFile and os.path.isfile(chatFile):
                        os.system(f'''{config.open} "{chatFile}"''')
            except:
                self.print("Failed to save chat!\n")
                SharedUtil.showErrors()

    def runInstruction(self):
        instructions = list(config.predefinedInstructions.keys())
        instruction = self.dialogs.getValidOptions(
            options=instructions,
            title="Predefined Instructions",
            text="Select an instruction:",
        )
        if instruction:
            config.defaultEntry = config.predefinedInstructions[instruction]
            config.accept_default = True

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
                if customContext and not customContext.strip().lower() == config.exit_entry:
                    config.chatGPTApiCustomContext = customContext.strip()
            self.showCurrentContext()

    def showCurrentContext(self):
        if not config.chatGPTApiPredefinedContext in config.predefinedContexts:
            config.chatGPTApiPredefinedContext = "[none]"
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

    def readAnswer(self, answer):
        # read the chunk
        if answer in string.punctuation and config.tempChunk:
            # read words when there a punctuation
            chunk = config.tempChunk + answer
            # reset config.tempChunk
            config.tempChunk = ""
            # play with tts
            if config.ttsOutput:
                TTSUtil.play(chunk)
        else:
            # append to a chunk for reading
            config.tempChunk += answer

    def stopSpinning(self):
        try:
            config.stop_event.set()
            config.spinner_thread.join()
        except:
            pass

    def showLogo(self):
        terminal_width = shutil.get_terminal_size().columns
        try:
            from art import text2art
            #if terminal_width >= 50:
            #    logo = text2art("MyHand Bot", font="small")
            if terminal_width >= 37:
                logo = text2art("myHand", font="small")
            elif terminal_width >= 24:
                logo = text2art("HAND", font="small")
            elif terminal_width >= 14:
                logo = text2art("mH", font="small")
            else:
                logo = f"MyHand Bot"
            logo = logo[:-1] # remove the linebreak at the end
        except:
            logo = f"MyHand Bot"
        print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>{logo}</{config.terminalPromptIndicatorColor2}>"))

    def startChats(self):
        tokenValidator = TokenValidator()
        def getDynamicToolBar():
            return config.dynamicToolBarText
        def startChat():
            clear()
            self.print(self.divider)
            self.showLogo()
            self.showCurrentContext()
            # go to startup directory
            startupdirectory = self.getFiles()
            os.chdir(startupdirectory)
            config.currentMessages = messages = self.resetMessages()
            self.print(f"startup directory:\n{startupdirectory}")
            self.print(self.divider)

            config.conversationStarted = False
            return (startupdirectory, messages)
        startupdirectory, messages = startChat()
        config.multilineInput = False
        features = (
            ".new",
            ".share" if config.terminalEnableTermuxAPI else ".save",
            ".swaptextbrightness",
            ".instruction",
            ".context",
            ".contextinclusion",
            ".changeapikey",
            ".chatgptmodel",
            ".temperature",
            ".maxtokens",
            ".mintokens",
            ".maxautoheal",
            ".plugins",
            ".functioncall",
            ".functionresponse",
            ".latestSearches",
            ".enhanceexecution",
            ".confirmexecution",
            ".codedisplay",
            ".pagerview",
            ".startupDirectory",
            ".termuxapi",
            ".autoupgrade",
            ".developer",
            ".togglemultiline",
            ".togglemousesupport",
            ".togglewordwrap",
            ".toggleimprovedwriting",
            ".toggleinputaudio",
            ".toggleresponseaudio",
            ".ttscommand",
            ".system",
            ".help",
            ".keys",
        )
        featuresLower = [i.lower() for i in features] + ["...", ".save", ".share"]
        while True:
            # default toolbar text
            config.dynamicToolBarText = " [ctrl+q] exit [ctrl+k] shortcut keys "
            # display current directory if changed
            currentDirectory = os.getcwd()
            if not currentDirectory == startupdirectory:
                self.print(self.divider)
                self.print(f"current directory:\n{currentDirectory}")
                self.print(self.divider)
                startupdirectory = currentDirectory
            # default input entry
            accept_default = config.accept_default
            config.accept_default = False
            defaultEntry = config.defaultEntry
            config.defaultEntry = ""
            # input suggestions
            inputSuggestions = config.inputSuggestions[:] + self.getDirectoryList() if config.developer else config.inputSuggestions
            completer = WordCompleter(inputSuggestions, ignore_case=True) if inputSuggestions else None
            userInput = self.prompts.simplePrompt(promptSession=self.terminal_chat_session, completer=completer, default=defaultEntry, accept_default=accept_default, validator=tokenValidator, bottom_toolbar=getDynamicToolBar)
            # display options when empty string is entered
            userInputLower = userInput.lower()
            if config.addPathAt is not None:
                prefix = userInput[:config.addPathAt]
                prefixSplit = prefix.rsplit(" ", 1)
                if len(prefixSplit) > 1:
                    default = prefixSplit[-1]
                    prefix = f"{prefixSplit[0]} "
                else:
                    default = prefix
                    prefix = ""
                suffix = userInput[config.addPathAt:]
                config.addPathAt = None
                userPath = self.getPath.getPath(message=f"{prefix}<{config.terminalCommandEntryColor2}>[add a path here]</{config.terminalCommandEntryColor2}>{suffix}", promptIndicator=">>> ", empty_to_cancel=True, default=default)
                config.defaultEntry = f"{prefix}{userPath}{suffix}"
                userInput = ""
            elif not userInputLower:
                userInput = config.blankEntryAction
            if userInput == "...":
                userInputLower = self.runOptions(features, userInput)

            # try to run as a python script first
            try:
                exec(userInput, globals())
                userInput = ""
            except:
                pass

            if userInput in config.aliases:
                userInput = config.aliases[userInput]

            if userInput.startswith("!"):
                self.runSystemCommand(userInput)
            elif userInput.startswith("```") and userInput.endswith("```") and not userInput == "``````":
                userInput = re.sub("```python", "```", userInput)
                self.runPythonScript(userInput)
            elif userInputLower == config.exit_entry:
                self.saveChat(messages)
                return self.exitAction()
            elif userInputLower == config.cancel_entry:
                pass
            elif userInputLower == ".system":
                SystemCommandPrompt().run(allowPathChanges=True)
            elif userInputLower == ".togglemultiline":
                self.toggleMultiline()
            elif userInputLower == ".swaptextbrightness":
                swapTerminalColors()
            elif userInputLower == ".togglemousesupport":
                self.toggleMouseSupport()
            elif userInputLower == ".togglewordwrap":
                self.toggleWordWrap()
            elif userInputLower == ".toggleimprovedwriting":
                self.toggleImprovedWriting()
            elif userInputLower == ".toggleinputaudio":
                self.toggleinputaudio()
            elif userInputLower == ".toggleresponseaudio":
                self.toggleresponseaudio()
            elif userInputLower == ".ttscommand":
                self.defineTtsCommand()
            elif userInputLower == ".instruction":
                self.runInstruction()
            elif userInputLower == ".context":
                self.changeContext()
                if not config.chatGPTApiContextInAllInputs and config.conversationStarted:
                    self.saveChat(messages)
                    startupdirectory, messages = startChat()
            elif userInputLower == ".new" and config.conversationStarted:
                self.saveChat(messages)
                startupdirectory, messages = startChat()
            elif userInputLower in (".share", ".save") and config.conversationStarted:
                self.saveChat(messages, openFile=True)
            elif userInput and not userInputLower in featuresLower:
                try:
                    if userInput and config.ttsInput:
                        TTSUtil.play(userInput)
                    # Feature: improve writing:
                    if userInput and config.displayImprovedWriting:
                        userInput = re.sub("\n\[Current time: [^\n]*?$", "", userInput)
                        improvedVersion = SharedUtil.getSingleChatResponse(f"""Improve the following writing, according to {config.improvedWritingSytle}
In addition, I would like you to help me with converting relative dates and times, if any, into exact dates and times based on the reference that today is {SharedUtil.getDayOfWeek()} and datetime is {str(datetime.datetime.now())}.
Remember, provide me with the improved writing only, enclosed in triple quotes ``` and without any additional information or comments.
My writing:
{userInput}""")
                        if improvedVersion and improvedVersion.startswith("```") and improvedVersion.endswith("```"):
                            self.print(improvedVersion)
                            userInput = improvedVersion[3:-3]
                            if config.ttsOutput:
                                TTSUtil.play(userInput)
                    # refine messages before running completion
                    fineTunedUserInput = self.fineTuneUserInput(userInput)
                    noFunctionCall = (("[NO_FUNCTION_CALL]" in fineTunedUserInput) or config.chatGPTApiPredefinedContext.startswith("Counselling - ") or config.chatGPTApiPredefinedContext.endswith("Counselling"))
                    noScreening = ("[NO_SCREENING]" in fineTunedUserInput)
                    checkCallSpecificFunction = re.search("\[CALL ([^\[\]]*?)\]", fineTunedUserInput)
                    config.runSpecificFuntion = checkCallSpecificFunction.group(1) if checkCallSpecificFunction and checkCallSpecificFunction.group(1) in config.pluginsWithFunctionCall else ""
                    fineTunedUserInput = re.sub("\[CALL [^\[\]]*?\]|\[NO_FUNCTION_CALL\]|\[NO_SCREENING\]", "", fineTunedUserInput)

                    # python execution
                    self.screenAction = ""
                    if config.enhanceCommandExecution and not noScreening and not noFunctionCall:
                        messages = self.screening(messages, fineTunedUserInput)
                    else:
                        messages.append({"role": "user", "content": fineTunedUserInput})

                    # start spinning
                    config.stop_event = threading.Event()
                    config.spinner_thread = threading.Thread(target=self.spinning_animation, args=(config.stop_event,))
                    config.spinner_thread.start()

                    # force loading internet searches
                    if config.loadingInternetSearches == "always" and not self.screenAction in ("termux", "python", "web", "system"):
                        try:
                            messages = self.runFunction(messages, config.integrate_google_searches_signature, "integrate_google_searches")
                        except:
                            self.print("Unable to load internet resources.")
                            SharedUtil.showErrors()

                    config.pagerContent = ""
                    self.addPagerContent = True

                    if config.conversationStarted:
                        messages = self.moveForwardSystemMessage(messages)
                    completion = self.runCompletion(messages, noFunctionCall)
                    # stop spinning
                    self.runPython = True
                    self.stopSpinning()

                    chat_response = ""
                    terminal_width = shutil.get_terminal_size().columns
                    self.lineWidth = 0
                    blockStart = False
                    wrapWords = config.wrapWords
                    for event in completion:
                        # RETRIEVE THE TEXT FROM THE RESPONSE
                        #event_text = dict(event.choices[0].delta) # EVENT DELTA RESPONSE
                        #answer = event_text.get("content", "") # RETRIEVE CONTENT
                        answer = event.choices[0].delta.content
                        answer = SharedUtil.transformText(answer)
                        # STREAM THE ANSWER
                        if answer is not None:
                            # display the chunk
                            chat_response += answer
                            # word wrap
                            if answer in ("```", "``"):
                                blockStart = not blockStart
                                if blockStart:
                                    config.wrapWords = False
                                else:
                                    config.wrapWords = wrapWords
                            if config.wrapWords:
                                if "\n" in answer:
                                    lines = answer.split("\n")
                                    for index, line in enumerate(lines):
                                        isLastLine = (len(lines) - index == 1)
                                        self.wrapStreamWords(line, terminal_width)
                                        if not isLastLine:
                                            print("\n", end='', flush=True)
                                            self.lineWidth = 0
                                else:
                                    self.wrapStreamWords(answer, terminal_width)
                            else:
                                print(answer, end='', flush=True) # Print the response
                            # speak streaming words
                            self.readAnswer(answer)
                    config.wrapWords = wrapWords
                    # reset config.tempChunk
                    config.tempChunk = ""
                    print("\n")

                    # optional
                    # remove predefined context to reduce token size and cost
                    #messages[-1] = {"role": "user", "content": userInput}

                    messages.append({"role": "assistant", "content": chat_response})
                    config.currentMessages = messages

                    # auto pager feature
                    config.pagerContent += self.wrapText(chat_response, terminal_width) if config.wrapWords else chat_response
                    self.addPagerContent = False
                    if config.pagerView:
                        self.launchPager(config.pagerContent)

                    config.conversationStarted = True

                # error codes: https://platform.openai.com/docs/guides/error-codes/python-library-error-types
                except openai.APIError as e:
                    self.stopSpinning()
                    #Handle API error here, e.g. retry or log
                    self.print(f"OpenAI API returned an API Error: {e}")
                except openai.APIConnectionError as e:
                    self.stopSpinning()
                    #Handle connection error here
                    self.print(f"Failed to connect to OpenAI API: {e}")
                except openai.RateLimitError as e:
                    self.stopSpinning()
                    #Handle rate limit error (we recommend using exponential backoff)
                    self.print(f"OpenAI API request exceeded rate limit: {e}")
                except:
                    self.stopSpinning()
                    trace = traceback.format_exc()
                    if "Please reduce the length of the messages or completion" in trace:
                        self.print("Maximum tokens reached!")
                    elif config.developer:
                        self.print(self.divider)
                        self.print(trace)
                        self.print(self.divider)
                    else:
                        self.print("Error encountered!")

                    config.defaultEntry = userInput
                    self.print("starting a new chat!")
                    self.saveChat(messages)
                    startupdirectory, messages = startChat()

    def addPagerText(self, text, wrapWords=False):
        if wrapWords:
            text = self.getWrappedHTMLText(text)
        config.pagerContent += f"{text}\n"

    def launchPager(self, pagerContent=None):
        if pagerContent is None:
            pagerContent = config.pagerContent
        if pagerContent:
            try:
                if SharedUtil.isPackageInstalled("less"):
                    # Windows users can install vlc command with scoop
                    # read: https://github.com/ScoopInstaller/Scoop
                    # > iwr -useb get.scoop.sh | iex
                    # > scoop install aria2 less
                    if re.search("<[^<>]+?>", pagerContent):
                        pagerContent = TextUtil.convertHtmlTagToColorama(pagerContent)
                    pydoc.pipepager(pagerContent, cmd='less -R')
                else:
                    pydoc.pager(pagerContent)
            except:
                config.pagerView = False
                SharedUtil.showErrors()

    def wrapStreamWords(self, answer, terminal_width):
        if " " in answer:
            if answer == " ":
                if self.lineWidth < terminal_width:
                    print(" ", end='', flush=True)
                    self.lineWidth += 1
            else:
                answers = answer.split(" ")
                for index, item in enumerate(answers):
                    isLastItem = (len(answers) - index == 1)
                    itemWidth = SharedUtil.getStringWidth(item)
                    newLineWidth = (self.lineWidth + itemWidth) if isLastItem else (self.lineWidth + itemWidth + 1)
                    if isLastItem:
                        if newLineWidth > terminal_width:
                            print(f"\n{item}", end='', flush=True)
                            self.lineWidth = itemWidth
                        else:
                            print(item, end='', flush=True)
                            self.lineWidth += itemWidth
                    else:
                        if (newLineWidth - terminal_width) == 1:
                            print(f"{item}\n", end='', flush=True)
                            self.lineWidth = 0
                        elif newLineWidth > terminal_width:
                            print(f"\n{item} ", end='', flush=True)
                            self.lineWidth = itemWidth + 1
                        else:
                            print(f"{item} ", end='', flush=True)
                            self.lineWidth += (itemWidth + 1)
        else:
            answerWidth = SharedUtil.getStringWidth(answer)
            newLineWidth = self.lineWidth + answerWidth
            if newLineWidth > terminal_width:
                print(f"\n{answer}", end='', flush=True)
                self.lineWidth = answerWidth
            else:
                print(answer, end='', flush=True)
                self.lineWidth += answerWidth

    # wrap html text at spaces
    def getWrappedHTMLText(self, text, terminal_width=None):
        if not " " in text:
            return text
        if terminal_width is None:
            terminal_width = shutil.get_terminal_size().columns
        self.wrappedText = ""
        self.lineWidth = 0

        def addWords(words):
            words = words.split(" ")
            for index, item in enumerate(words):
                isLastItem = (len(words) - index == 1)
                if SharedUtil.is_CJK(item):
                    for iIndex, i in enumerate(item):
                        isSpaceItem = (not isLastItem and (len(item) - iIndex == 1))
                        iWidth = SharedUtil.getStringWidth(i)
                        if isSpaceItem:
                            newLineWidth = self.lineWidth + iWidth + 1
                        else:
                            newLineWidth = self.lineWidth + iWidth
                        if newLineWidth > terminal_width:
                            self.wrappedText += f"\n{i} " if isSpaceItem else f"\n{i}"
                            self.lineWidth = iWidth + 1 if isSpaceItem else iWidth
                        else:
                            self.wrappedText += f"{i} " if isSpaceItem else i
                            self.lineWidth += iWidth + 1 if isSpaceItem else iWidth
                else:
                    itemWidth = SharedUtil.getStringWidth(item)
                    if isLastItem:
                        newLineWidth = self.lineWidth + itemWidth
                    else:
                        newLineWidth = self.lineWidth + itemWidth + 1
                    if newLineWidth > terminal_width:
                        self.wrappedText += f"\n{item}" if isLastItem else f"\n{item} "
                        self.lineWidth = itemWidth if isLastItem else itemWidth + 1
                    else:
                        self.wrappedText += item if isLastItem else f"{item} "
                        self.lineWidth += itemWidth if isLastItem else itemWidth + 1

        def processLine(lineText):
            if re.search("<[^<>]+?>", lineText):
                # handle html/xml tags
                chunks = lineText.split(">")
                totalChunks = len(chunks)
                for index, chunk in enumerate(chunks):
                    isLastChunk = (totalChunks - index == 1)
                    if isLastChunk:
                        addWords(chunk)
                    else:
                        tag = True if "<" in chunk else False
                        if tag:
                            nonTag, tagContent = chunk.rsplit("<", 1)
                            addWords(nonTag)
                            self.wrappedText += f"<{tagContent}>"
                        else:
                            addWords(f"{chunk}>")
            else:
                addWords(lineText)

        lines = text.split("\n")
        totalLines = len(lines)
        for index, line in enumerate(lines):
            isLastLine = (totalLines - index == 1)
            processLine(line)
            if not isLastLine:
                self.wrappedText += "\n"
                self.lineWidth = 0

        return self.wrappedText

    def checkCompletion(self):
        # instantiate a client that can shared with plugins
        os.environ["OPENAI_API_KEY"] = config.openaiApiKey
        self.client = OpenAI()
        try:
            self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content" : "hello"}],
                n=1,
                max_tokens=10,
            )
            # set variable 'OAI_CONFIG_LIST' to work with pyautogen
            oai_config_list = []
            for model in self.models:
                oai_config_list.append({"model": model, "api_key": config.openaiApiKey})
            os.environ["OAI_CONFIG_LIST"] = json.dumps(oai_config_list)
        except openai.APIError as e:
            self.print("Error: Issue on OpenAI side.")
            self.print("Solution: Retry your request after a brief wait and contact us if the issue persists.")
        #except openai.Timeout as e:
        #    self.print("Error: Request timed out.")
        #    self.print("Solution: Retry your request after a brief wait and contact us if the issue persists.")
        except openai.RateLimitError as e:
            self.print("Error: You have hit your assigned rate limit.")
            self.print("Solution: Pace your requests. Read more in OpenAI [Rate limit guide](https://platform.openai.com/docs/guides/rate-limits).")
        except openai.APIConnectionError as e:
            self.print("Error: Issue connecting to our services.")
            self.print("Solution: Check your network settings, proxy configuration, SSL certificates, or firewall rules.")
        #except openai.InvalidRequestError as e:
        #    self.print("Error: Your request was malformed or missing some required parameters, such as a token or an input.")
        #    self.print("Solution: The error message should advise you on the specific error made. Check the [documentation](https://platform.openai.com/docs/api-reference/) for the specific API method you are calling and make sure you are sending valid and complete parameters. You may also need to check the encoding, format, or size of your request data.")
        except openai.AuthenticationError as e:
            self.print("Error: Your API key or token was invalid, expired, or revoked.")
            self.print("Solution: Check your API key or token and make sure it is correct and active. You may need to generate a new one from your account dashboard.")
            self.changeAPIkey()
        #except openai.ServiceUnavailableError as e:
        #    self.print("Error: Issue on OpenAI servers. ")
        #    self.print("Solution: Retry your request after a brief wait and contact us if the issue persists. Check the [status page](https://status.openai.com).")
        except:
            SharedUtil.showErrors()