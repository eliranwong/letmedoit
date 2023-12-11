from letmedoit import config
import openai, threading, os, time, traceback, re, subprocess, json, pydoc, textwrap, string, shutil, asyncio, datetime, pprint
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
from prompt_toolkit.input import create_input
from prompt_toolkit.keys import Keys
from letmedoit.utils.terminal_mode_dialogs import TerminalModeDialogs
from letmedoit.utils.prompts import Prompts
from letmedoit.utils.promptValidator import FloatValidator, TokenValidator
from letmedoit.utils.get_path_prompt import GetPath
from letmedoit.utils.prompt_shared_key_bindings import swapTerminalColors
from letmedoit.utils.file_utils import FileUtil
from letmedoit.utils.terminal_system_command_prompt import SystemCommandPrompt
from letmedoit.utils.shared_utils import SharedUtil
from letmedoit.utils.tts_utils import TTSUtil
from letmedoit.plugins.bibleTools.utils.TextUtil import TextUtil
from letmedoit.autobuilder import AutoGenBuilder


class LetMeDoItAI:

    def __init__(self):
        #config.letMeDoItAI = self
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
        if not hasattr(config, "predefinedContextTemp"):
            config.predefinedContextTemp = ""
        config.systemCommandPromptEntry = ""
        config.pagerContent = ""
        self.addPagerContent = False
        # share the following methods in config so that they are accessible via plugins
        config.getFiles = self.getFiles
        config.stopSpinning = self.stopSpinning
        config.toggleMultiline = self.toggleMultiline
        config.print = self.print
        config.print2 = self.print2
        config.print3 = self.print3
        config.getWrappedHTMLText = self.getWrappedHTMLText
        config.fineTuneUserInput = self.fineTuneUserInput
        config.launchPager = self.launchPager
        config.addPagerText = self.addPagerText
        config.getFunctionMessageAndResponse = self.getFunctionMessageAndResponse
        config.runSpecificFuntion = ""
        # env variables
        os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = config.env_QT_QPA_PLATFORM_PLUGIN_PATH

        # get path
        config.addPathAt = None
        self.getPath = GetPath(
            cancel_entry="",
            promptIndicatorColor=config.terminalPromptIndicatorColor2,
            promptEntryColor=config.terminalCommandEntryColor2,
            subHeadingColor=config.terminalColors[config.terminalPromptIndicatorColor2],
            itemColor=config.terminalColors[config.terminalCommandEntryColor2],
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
            self.print2("ChatGPT API key not found!")
            self.print3("Read: https://github.com/eliranwong/letmedoit/wiki/ChatGPT-API-Key")
            exit(0)

        # initial completion check at startup
        if config.initialCompletionCheck:
            self.checkCompletion()
        else:
            self.setAPIkey()

        chat_history = os.path.join(config.historyParentFolder if config.historyParentFolder else config.letMeDoItAIFolder, "history", "chats")
        self.terminal_chat_session = PromptSession(history=FileHistory(chat_history))

        # check if tts is ready
        if not config.isVlcPlayerInstalled and not config.isPygameInstalled and not config.ttsCommand:
            config.tts = False
        else:
            config.tts = True
        self.isTtsAvailable()

        # check if text output streaming is finished
        self.streaming_finished = False

        self.actions = {
            '.new': 'start a new chat [ctrl+n]',
            '.save': 'save content [ctrl+s]',
            '.swaptextbrightness': 'swap text brightness [esc+s]',
            '.instruction': 'run an instruction',
            '.context': 'change chat context [ctrl+o]',
            '.contextinclusion': 'change chat context inclusion',
            '.changeapikey': 'change API key',
            '.chatgptmodel': 'change ChatGPT model',
            '.temperature': 'change ChatGPT temperature',
            '.maxtokens': 'change maximum response tokens',
            '.mintokens': 'change minimum response tokens',
            '.dynamictokencount': 'change dynamic token count',
            '.maxautoheal': 'change maximum consecutive auto-heal',
            '.maxmemorymatches': 'change maximum memory matches',
            '.plugins': 'change plugins',
            '.functioncall': 'change function call',
            '.functionresponse': 'change function call response integration',
            '.latestSearches': 'change online searches',
            #'.enhanceexecution': 'change code execution mode [ctrl+e]',
            '.confirmexecution': 'change code confirmation protocol',
            '.codedisplay': 'change code display',
            '.pagerview': 'change pager view',
            '.embeddingmodel': 'change embedding model',
            '.assistantname': 'change assistant name',
            '.systemmessage': 'change custom system message',
            '.ipinfo': 'change ip information inclusion',
            '.startupDirectory': 'change startup directory',
            '.autobuilderconfig': 'change auto builder config',
            '.customtexteditor': 'change custom text editor',
            '.termuxapi': 'change Termux API integration',
            '.autoupgrade': 'change automatic upgrade',
            '.developer': 'change developer mode [ctrl+d]',
            '.togglemultiline': 'toggle multi-line input [ctrl+l]',
            '.togglemousesupport': 'toogle mouse support [esc+m]',
            '.togglewordwrap': 'toggle word wrap [ctrl+w]',
            '.toggleimprovedwriting': 'toggle improved writing [esc+i]',
            '.toggleinputaudio': 'toggle input audio [ctrl+b]',
            '.toggleresponseaudio': 'toggle response audio [ctrl+p]',
            '.ttscommand': 'configure text-to-speech command',
            '.system': 'open system command prompt',
            '.help': 'open LetMeDoIt wiki',
            '.keys': 'display key bindings',
        }

    def getPreferredDir(self):
        preferredDir = os.path.join(os.path.expanduser('~'), config.letMeDoItName.split()[0].lower())
        try:
            Path(preferredDir).mkdir(parents=True, exist_ok=True)
        except:
            pass
        return preferredDir if os.path.isdir(preferredDir) else ""

    def getFiles(self):
        if config.startupdirectory and not os.path.isdir(config.startupdirectory):
            config.startupdirectory = ""
        preferredDir = self.preferredDir if self.preferredDir else os.path.join(config.letMeDoItAIFolder, "files")
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
            try:
                def runCode(text):
                    code = compile(text, script, 'exec')
                    exec(code, globals())
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

        # built-in functions
        config.pluginsWithFunctionCall.append("execute_python_code")
        config.inputSuggestions.append("[CALL_execute_python_code]")
        if config.terminalEnableTermuxAPI:
            config.pluginsWithFunctionCall.append("execute_termux_command")
            config.inputSuggestions.append("[CALL_execute_termux_command]")

        pluginFolder = os.path.join(config.letMeDoItAIFolder, "plugins")
        if self.preferredDir:
            customPluginFoler = os.path.join(self.preferredDir, "plugins")
            Path(customPluginFoler).mkdir(parents=True, exist_ok=True)
            pluginFolders = (pluginFolder, customPluginFoler)
        else:
            pluginFolders = (pluginFolder,)
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
        for folder in pluginFolders:
            for plugin in FileUtil.fileNamesWithoutExtension(folder, "py"):
                if not plugin in config.chatGPTPluginExcludeList:
                    script = os.path.join(folder, "{0}.py".format(plugin))
                    self.execPythonFile(script)
        if internetSeraches in config.chatGPTPluginExcludeList:
            del config.chatGPTApiFunctionSignatures[0]
        self.setupPythonExecution()
        if config.terminalEnableTermuxAPI:
            self.setupTermuxExecution()
        for i in config.pluginsWithFunctionCall:
            config.inputSuggestions.append(f"[CALL_{i}]")
            config.inputSuggestions.append(f"CALL_{i}]")

    def selectPlugins(self):
        plugins = []
        enabledPlugins = []
        pluginFolder = os.path.join(config.letMeDoItAIFolder, "plugins")
        if self.preferredDir:
            customPluginFoler = os.path.join(self.preferredDir, "plugins")
            Path(customPluginFoler).mkdir(parents=True, exist_ok=True)
            pluginFolders = (pluginFolder, customPluginFoler)
        else:
            pluginFolders = (pluginFolder,)
        for folder in pluginFolders:
            for plugin in FileUtil.fileNamesWithoutExtension(folder, "py"):
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

    def setAPIkey(self):
        # instantiate a client that can shared with plugins
        os.environ["OPENAI_API_KEY"] = config.openaiApiKey
        self.client = OpenAI()
        # set variable 'OAI_CONFIG_LIST' to work with pyautogen
        oai_config_list = []
        for model in self.models:
            oai_config_list.append({"model": model, "api_key": config.openaiApiKey})
        os.environ["OAI_CONFIG_LIST"] = json.dumps(oai_config_list)

    def changeAPIkey(self):
        if not config.terminalEnableTermuxAPI or (config.terminalEnableTermuxAPI and self.fingerprint()):
            print("Enter your OpenAI API Key [required]:")
            apikey = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.openaiApiKey, is_password=True)
            if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
                config.openaiApiKey = apikey
            #self.print("Enter your Organization ID [optional]:")
            #oid = self.prompts.simplePrompt(default=config.openaiApiOrganization, is_password=True)
            #if oid and not oid.strip().lower() in (config.cancel_entry, config.exit_entry):
            #    config.openaiApiOrganization = oid
            self.checkCompletion()
            config.saveConfig()
            self.print2("Updated!")

    def exitAction(self):
        message = "closing ..."
        self.print2(message)
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

    def print2(self, content):
        print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>{content}</{config.terminalPromptIndicatorColor2}>"))

    def print3(self, content):
        splittedContent = content.split(": ", 1)
        if len(splittedContent) == 2:
            key, value = splittedContent
            print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>{key}:</{config.terminalPromptIndicatorColor2}> {value}"))
        else:
            self.print2(splittedContent)

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
            "description": "Execute python code to resolve a computing task",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code that integrates any relevant packages to resolve my request",
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
        def notifyDeveloper(func_name):
            if config.developer:
                #self.print(f"running function '{func_name}' ...")
                print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>Running function</{config.terminalPromptIndicatorColor2}> <{config.terminalCommandEntryColor2}>'{func_name}'</{config.terminalCommandEntryColor2}> <{config.terminalPromptIndicatorColor2}>...</{config.terminalPromptIndicatorColor2}>"))
        # ChatGPT's built-in function named "python"
        if function_name == "python":
            notifyDeveloper(function_name)
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
        # known unwanted functions are handled here
        elif function_name in ("translate_text",):
            # "translate_text" has two arguments, "text", "target_language"
            # handle known and unwanted function
            function_response = "[INVALID]" 
        # handle unexpected function
        elif not function_name in config.chatGPTApiAvailableFunctions:
            if config.developer:
                self.print(f"Unexpected function: {function_name}")
                self.print(self.divider)
                print(func_arguments)
                self.print(self.divider)
            function_response = "[INVALID]"
        else:
            notifyDeveloper(function_name)
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
                    else: # no tool is called; same handling as tools finished calling; which break the loop later
                        self.functionJustCalled = True
                    # consume the first delta only at this point
                    break
                # Continue only when a function is called
                if self.functionJustCalled:
                    break

                # get all tool arguments, both of functions and non-functions
                toolArguments = SharedUtil.getToolArgumentsFromStreams(completion)

                func_responses = ""
                bypassFunctionCall = False
                # handle function calls
                for func in function_calls:
                    func_index = func.index
                    func_id = func.id
                    func_name = func.function.name
                    func_arguments = toolArguments[func_index]

                    # get function response
                    func_response = self.getFunctionResponse(func_arguments, func_name)

                    # "[INVALID]" practically mean that it ignores previously called function and continues chat without function calling
                    if func_response == "[INVALID]":
                        bypassFunctionCall = True
                    elif func_response or config.tempContent:
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
                                "content": func_response if func_response else config.tempContent,
                            }
                        )  # extend conversation with function response
                        config.tempContent = ""
                        if func_response:
                            func_responses += f"\n{func_response}\n{config.divider}"

                self.functionJustCalled = True

                # bypassFunctionCall is set to True, usually when a function is called by mistake
                if bypassFunctionCall:
                    pass
                # two cases that breaks the loop at this point
                # 1. func_responses == ""
                # 2. config.passFunctionCallReturnToChatGPT = False
                elif not config.passFunctionCallReturnToChatGPT or not func_responses:
                    if func_responses:
                        self.print(f"{config.divider}\n{func_responses}")
                    # A break here means that no information from the called function is passed back to ChatGPT
                    # 1. config.passFunctionCallReturnToChatGPT is set to True
                    # 2. func_responses = "" or None; can be specified in plugins
                    break
            except:
                SharedUtil.showErrors()
                break

        return completion

    # reset message when a new chart is started or context is changed
    def resetMessages(self):
        systemMessage = config.customSystemMessage if config.customSystemMessage else f'''You’re {config.letMeDoItName}, an advanced AI assistant, capable of both engaging in conversations and executing codes on my device.
I am providing the basic information of my device below in case you need it:
```
{SharedUtil.getDeviceInfo()}
```
Please use the current time and date that I have provided above as a reference point for any relative dates and times mentioned in my prompt.
You have all the necessary permissions to execute system commands and Python code on my behalf. Your functionality expands as I add more plugins to you. You respond to my prompts and perform tasks based on your own knowledge, the context I provide, as well as the additional knowledge and capabilities provided by plugins.

When replying to my requests, please follow these steps:
Step 1: Estimate my intent based on the request and context. The intent can be a code generation task, an executable computing task, a translation task, or a question answering task.
Step 2: Reply based on the estimated intent.

Always remember that you are much more than a text-based AI. You possess both vision and speech capabilities and have direct access to my device's system, enabling you to execute tasks at my command. Please do not state otherwise.
'''
        messages = [
            {"role": "system", "content": systemMessage}
        ]
        return messages

    # update system message
    def updateSystemMessage(self, messages):
        for index, message in enumerate(messages):
            try:
                if message.get("role", "") == "system":
                    # update system mess
                    dayOfWeek = SharedUtil.getDayOfWeek()
                    message["content"] = re.sub(
                        """^Current directory: .*?\nCurrent time: .*?\nCurrent day of the week: .*?$""",
                        f"""Current directory: {os.getcwd()}\nCurrent time: {str(datetime.datetime.now())}\nCurrent day of the week: {dayOfWeek}""",
                        message["content"],
                        flags=re.M,
                    )
                    messages[index] = message
                    # in a long conversation, ChatGPT often forgets its system message
                    # move forward if conversation have started, to enhance system message
                    if config.conversationStarted and not index == len(messages) - 1:
                        item = messages.pop(index)
                        messages.append(item)
                    break
            except:
                pass
        return messages

    def getCurrentContext(self):
        if not config.predefinedContext in config.predefinedContexts:
            self.print2(f"'{config.predefinedContext}' not defined!")
            config.predefinedContext = config.predefinedContextTemp if config.predefinedContextTemp and config.predefinedContextTemp in config.predefinedContexts else "[none]"
            self.print3(f"Predefined context changed to: {config.predefinedContext}")
        if config.predefinedContext == "[none]":
            # no context
            context = ""
        elif config.predefinedContext == "[custom]":
            # custom input in the settings dialog
            context = config.customPredefinedContext
        else:
            # users can modify config.predefinedContexts via plugins
            context = config.predefinedContexts[config.predefinedContext]
        return context

    def showCurrentContext(self):
        description = self.getCurrentContext()
        if description:
            description = f"\n{description}"
        self.print(self.divider)
        self.print3(f"Context: {config.predefinedContext}{description}")
        self.print(self.divider)

    def fineTuneUserInput(self, userInput):
        # customise chat context
        context = self.getCurrentContext()
        if SharedUtil.is_valid_url(userInput) and config.predefinedContext in ("Let me Summarize", "Let me Explain"):
            context = context.replace("the following content:\n[NO_FUNCTION_CALL]", "the content in the this web url:\n")
        elif SharedUtil.is_valid_url(userInput) and config.predefinedContext == "Let me Translate":
            userInput = SharedUtil.getWebText(userInput)
        if context and (not config.conversationStarted or (config.conversationStarted and config.applyPredefinedContextAlways)):
            # context may start with "You will be provided with my input delimited with a pair of XML tags, <input> and </input>. ...
            userInput = re.sub("<content>|<content [^<>]*?>|</content>", "", userInput)
            userInput = f"{context}\n<content>{userInput}</content>" if userInput.strip() else context
        #userInput = SharedUtil.addTimeStamp(userInput)
        return userInput

    def runOptions(self, userInput):
        features = tuple(self.actions.keys())
        descriptions = tuple(self.actions.values())
        feature = self.dialogs.getValidOptions(
            options=features,
            descriptions=descriptions,
            title=config.letMeDoItName,
            default=config.defaultBlankEntryAction,
            text="Select an action or make changes:",
        )
        if feature:
            if feature == ".chatgptmodel":
                self.setLlmModel()
            elif feature == ".embeddingmodel":
                self.setEmbeddingModel()
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
            elif feature == ".autobuilderconfig":
                AutoGenBuilder().promptConfig()
            elif feature == ".systemmessage":
                self.setCustomSystemMessage()
            elif feature == ".ipinfo":
                self.setIncludeIpInSystemMessage()
            elif feature == ".dynamictokencount":
                self.setDynamicTokenCount()
            elif feature == ".keys":
                config.showKeyBindings()
            elif feature == ".help":
                SharedUtil.openURL('https://github.com/eliranwong/letmedoit/wiki')
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
            elif feature == ".maxmemorymatches":
                self.setMemoryClosestMatchesNumber()
            elif feature == ".assistantname":
                self.setAssistantName()
            elif feature == ".customtexteditor":
                self.setCustomTextEditor()
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
            self.print3(f"Automatic Upgrade: {option}d!")

    def setDynamicTokenCount(self):
        options = ("enable", "disable")
        option = self.dialogs.getValidOptions(
            options=options,
            title="Dynamic Token Count",
            default="enable" if config.dynamicTokenCount else "disable",
            text="Perform token count as users type.\nSelect an option below:"
        )
        if option:
            config.dynamicTokenCount = (option == "enable")
            config.saveConfig()
            self.print3(f"Dynamic token count: {option}d!")

    def setIncludeIpInSystemMessage(self):
        options = ("enable", "disable")
        option = self.dialogs.getValidOptions(
            options=options,
            title="Include IP information",
            default="enable" if config.includeIpInSystemMessage else "disable",
            text="Include IP information in system message\ncan enhance response about locations.\nSelect an option below:"
        )
        if option:
            config.includeIpInSystemMessage = (option == "enable")
            config.saveConfig()
            self.print3(f"Include IP information: {option}d!")

    def setCodeDisplay(self):
        options = ("enable", "disable")
        option = self.dialogs.getValidOptions(
            options=options,
            title="Code Display",
            default="enable" if config.codeDisplay else "disable",
            text="Options to display programming code before execution:"
        )
        if option:
            config.codeDisplay = (option == "enable")
            config.saveConfig()
            self.print3(f"Code display: {option}d!")

    def setContextInclusion(self):
        options = ("the first input only", "all inputs")
        option = self.dialogs.getValidOptions(
            options=options,
            title="Predefined Context Inclusion",
            default="all inputs" if config.applyPredefinedContextAlways else "the first input only",
            text="Define below how you want to include predefined context\nwith your inputs.\nApply predefined context in ...",
        )
        if option:
            config.applyPredefinedContextAlways = True if option == "all inputs" else False
            config.saveConfig()
            self.print3(f"Predefined Context Inclusion: {option}!")

    def setStartupDirectory(self):
        try:
            folder = self.getFolderPath()
        except:
            self.print2(f"Given path not accessible!")
            folder = ""
        if folder and os.path.isdir(folder):
            config.startupdirectory = folder
            config.saveConfig()
            self.print3(f"Startup directory:\n{folder}")

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
            text=f"{config.letMeDoItName} can perform online searches.\nHow do you want this feature?",
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
            self.print3(f"Latest Online Searches: {option}")

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
            title="Command Confirmation Protocol",
            text=f"{config.letMeDoItName} is designed to execute commands on your behalf.\nPlease specify when you would prefer\nto receive a confirmation\nbefore commands are executed:\n(Note: Execute commands at your own risk.)",
            default=config.confirmExecution,
        )
        if option:
            config.confirmExecution = option
            config.saveConfig()
            self.print3(f"Command Confirmation Protocol: {option}")

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
            self.print3(f"Pager View: {option}!")

    def setDeveloperMode(self):
        options = ("enable", "disable")
        option = self.dialogs.getValidOptions(
            options=options,
            title="Developer Mode",
            default="enable" if config.developer else "disable",
            text="Read LetMeDoIt wiki for more information.\nSelect an option below:"
        )
        if option:
            config.developer = (option == "enable")
            config.saveConfig()
            self.print3(f"Developer Mode: {option}d!")

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
            self.print3(f"""Termux API Integration: {"enable" if config.terminalEnableTermuxAPI else "disable"}d!""")

    def setCommandExecutionMode(self):
        options = ("enhanced", "auto")
        option = self.dialogs.getValidOptions(
            options=options,
            title="Code Execution Mode",
            default="enhanced" if config.enhanceCommandExecution else "auto",
            text=f"{config.letMeDoItName} can execute commands\nto retrieve the requested information\nor perform tasks for users.\n(read https://github.com/eliranwong/letmedoit/wiki/Command-Execution)\nSelect a mode below:",
        )
        if option:
            config.enhanceCommandExecution = (option == "enhanced")
            config.saveConfig()
            self.print3(f"Code Execution Mode: {option}")

    def setFunctionCall(self):
        calls = ("auto", "none")
        call = self.dialogs.getValidOptions(
            options=calls,
            title="ChatGPT Function Call",
            default=config.chatGPTApiFunctionCall,
            text="Enabling function call\nto extend ChatGPT capabilities.\nEnable / Disable this feature below:",
        )
        if call:
            config.chatGPTApiFunctionCall = call
            config.saveConfig()
            self.print3(f"ChaptGPT function call: {'enabled' if config.chatGPTApiFunctionCall == 'auto' else 'disabled'}!")

    def setFunctionResponse(self):
        calls = ("enable", "disable")
        call = self.dialogs.getValidOptions(
            options=calls,
            title="Pass Function Call Response to ChatGPT",
            default="enable" if config.passFunctionCallReturnToChatGPT else "disable",
            text="Enabling this feature allows\npassing function call responses, if any,\nto extend conversation with ChatGPT.\nDisabling this feature allows\nrunning function calls\nwithout generating further responses."
        )
        if call:
            config.passFunctionCallReturnToChatGPT = (call == "enable")
            config.saveConfig()
            self.print3(f"Pass Function Call Response to ChatGPT: {'enabled' if config.passFunctionCallReturnToChatGPT else 'disabled'}!")

    def setTemperature(self):
        self.print("Enter a value between 0.0 and 2.0:")
        self.print("(Lower values for temperature result in more consistent outputs, while higher values generate more diverse and creative results. Select a temperature value based on the desired trade-off between coherence and creativity for your specific application.)")
        temperature = self.prompts.simplePrompt(style=self.prompts.promptStyle2, validator=FloatValidator(), default=str(config.chatGPTApiTemperature))
        if temperature and not temperature.strip().lower() == config.exit_entry:
            temperature = float(temperature)
            if temperature < 0:
                temperature = 0
            elif temperature > 2:
                temperature = 2
            config.chatGPTApiTemperature = round(temperature, 1)
            config.saveConfig()
            self.print3(f"ChatGPT Temperature: {temperature}")

    def setLlmModel(self):
        model = self.dialogs.getValidOptions(
            options=self.models,
            title="ChatGPT model",
            default=config.chatGPTApiModel,
            text="Select a ChatGPT model:",
        )
        if model:
            config.chatGPTApiModel = model
            self.print3(f"ChatGPT model: {model}")
            # handle max tokens
            if tiktokenImported:
                functionTokens = SharedUtil.count_tokens_from_functions(config.chatGPTApiFunctionSignatures)
                tokenLimit = SharedUtil.tokenLimits[config.chatGPTApiModel] - functionTokens
            else:
                tokenLimit = SharedUtil.tokenLimits[config.chatGPTApiModel]
            suggestedMaxToken = int(tokenLimit / 2)
            config.chatGPTApiMaxTokens = 4096 if config.chatGPTApiModel == "gpt-4-1106-preview" else suggestedMaxToken # 'gpt-4-1106-preview' supports at most 4096 completion tokens
            config.saveConfig()
            self.print3(f"Maximum response tokens: {config.chatGPTApiMaxTokens}.")

    def setEmbeddingModel(self):
        oldEmbeddingModel = config.embeddingModel
        model = self.dialogs.getValidOptions(
            options=("text-embedding-ada-002", "all-mpnet-base-v2", "all-MiniLM-L6-v2", "custom"),
            title="Embedding model",
            default=config.embeddingModel,
            text="Select an embedding model:",
        )
        if model:
            if model == "custom":
                self.print("Enter OpenAI or Sentence Transformer Embedding model:")
                customModel = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.embeddingModel)
                if customModel and not customModel.strip().lower() == config.exit_entry:
                    config.embeddingModel = customModel 
            else:
                config.embeddingModel = model
            self.print3(f"Embedding model: {model}")
        if not oldEmbeddingModel == config.embeddingModel:
            self.print(f"You've change the embedding model from '{oldEmbeddingModel}' to '{config.embeddingModel}'.")
            self.print("To work with the newly selected model, previous memory store and retrieved collections need to be deleted.")
            self.print("Do you want to delete them now? [y]es / [N]o")
            confirmation = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default="yes")
            if confirmation.lower() in ("y", "yes"):
                memory_store = os.path.join(config.getFiles(), "memory")
                retrieved_collections = os.path.join(config.getFiles(), "autogen", "retriever")
                for folder in (memory_store, retrieved_collections):
                    shutil.rmtree(folder, ignore_errors=True)
            else:
                self.print(f"Do you want to change back the embedding model from '{config.embeddingModel}' to '{oldEmbeddingModel}'? [y]es / [N]o")
                confirmation = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default="yes")
                if not confirmation.lower() in ("y", "yes"):
                    config.embeddingModel = oldEmbeddingModel
                    self.print3(f"Embedding model: {oldEmbeddingModel}")

    def setAssistantName(self):
        self.print("You may modify my name below:")
        letMeDoItName = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.letMeDoItName)
        if letMeDoItName and not letMeDoItName.strip().lower() == config.exit_entry:
            config.letMeDoItName = letMeDoItName
            self.preferredDir = self.getPreferredDir()
            config.saveConfig()
            self.print3(f"You have changed my name to: {config.letMeDoItName}")

    def setCustomSystemMessage(self):
        self.print("You can modify the system message to furnish me with details about my capabilities, constraints, or any pertinent context that may inform our interactions. This will guide me in managing and responding to your requests appropriately.")
        self.print("Please note that altering my system message directly affects my functionality. Handle with care.")
        self.print("Enter custom system message below:")
        self.print(f"(Keep it blank to use {config.letMeDoItName} default system message.)")
        message = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.customSystemMessage)
        if message and not message.strip().lower() == config.exit_entry:
            config.customSystemMessage = message
            config.saveConfig()
            self.print3(f"Custom system message: {config.letMeDoItName}")

    def setCustomTextEditor(self):
        self.print("Please specify custom text editor command below:")
        self.print("e.g. 'micro -softwrap true -wordwrap true'")
        self.print("Leave it blank to use our built-in text editor 'eTextEdit' by default.")
        customTextEditor = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.customTextEditor)
        if customTextEditor and not customTextEditor.strip().lower() == config.exit_entry:
            textEditor = re.sub(" .*?$", "", customTextEditor)
            if not textEditor or not SharedUtil.isPackageInstalled(textEditor):
                self.print2("Command not found on your device!")
            else:
                config.customTextEditor = customTextEditor
                config.saveConfig()
                self.print3(f"Custom text editor: {config.customTextEditor}")

    def setMemoryClosestMatchesNumber(self):
        self.print("Please specify the number of closest matches in each memory retrieval:")
        memoryClosestMatchesNumber = self.prompts.simplePrompt(style=self.prompts.promptStyle2, numberOnly=True, default=str(config.memoryClosestMatchesNumber))
        if memoryClosestMatchesNumber and not memoryClosestMatchesNumber.strip().lower() == config.exit_entry and int(memoryClosestMatchesNumber) >= 0:
            config.memoryClosestMatchesNumber = int(memoryClosestMatchesNumber)
            config.saveConfig()
            self.print3(f"Number of memory closest matches: {config.memoryClosestMatchesNumber}")

    def setMaxAutoHeal(self):
        self.print(f"The auto-heal feature enables {config.letMeDoItName} to automatically fix broken Python code if it was not executed properly.")
        self.print("Please specify maximum number of auto-heal attempts below:")
        self.print("(Remarks: Enter '0' if you want to disable auto-heal feature)")
        maxAutoHeal = self.prompts.simplePrompt(style=self.prompts.promptStyle2, numberOnly=True, default=str(config.max_consecutive_auto_heal))
        if maxAutoHeal and not maxAutoHeal.strip().lower() == config.exit_entry and int(maxAutoHeal) >= 0:
            config.max_consecutive_auto_heal = int(maxAutoHeal)
            config.saveConfig()
            self.print3(f"Maximum consecutive auto-heal: {config.max_consecutive_auto_heal}")

    def setMinTokens(self):
        self.print("Please specify minimum response tokens below:")
        mintokens = self.prompts.simplePrompt(style=self.prompts.promptStyle2, numberOnly=True, default=str(config.chatGPTApiMinTokens))
        if mintokens and not mintokens.strip().lower() == config.exit_entry and int(mintokens) > 0:
            config.chatGPTApiMinTokens = int(mintokens)
            if config.chatGPTApiMinTokens > config.chatGPTApiMaxTokens:
                config.chatGPTApiMinTokens = config.chatGPTApiMaxTokens
            config.saveConfig()
            self.print3(f"Minimum tokens: {config.chatGPTApiMinTokens}")

    def setMaxTokens(self):
        contextWindowLimit = SharedUtil.tokenLimits[config.chatGPTApiModel]
        if tiktokenImported:
            functionTokens = SharedUtil.count_tokens_from_functions(config.chatGPTApiFunctionSignatures)
            tokenLimit = contextWindowLimit - functionTokens - config.chatGPTApiMinTokens
        else:
            tokenLimit = contextWindowLimit
        if tiktokenImported and tokenLimit < config.chatGPTApiMinTokens:
            self.print(f"Availble functions have already taken up too many tokens [{functionTokens}] to work with selected model '{config.chatGPTApiModel}'. You may either changing to a model that supports more tokens or deactivating some of the plugins that you don't need to reduce the number of tokens in total.")
        else:
            self.print(self.divider)
            self.print(f"You are now using ChatGPT model '{config.chatGPTApiModel}'. Its context window limit is {contextWindowLimit} tokens.")
            if tiktokenImported:
                self.print(f"Current enabled functions have taken up {functionTokens} tokens.")
            self.print(f"You can have no more than {tokenLimit} tokens, for both prompts and responses, in a single chain of messages.")
            self.print("(GPT and embeddings models process text in chunks called tokens. As a rough rule of thumb, 1 token is approximately 4 characters or 0.75 words for English text. One limitation to keep in mind is that for a GPT model the prompt and the generated output combined must be no more than the model's maximum context length.)")
            self.print(self.divider)
            self.print("Please specify maximum response tokens below:")
            self.print("(Remarks: If the entered value exceeds the maximum number of completion tokens allowed in your selected model, it will be modified.)")
            maxtokens = self.prompts.simplePrompt(style=self.prompts.promptStyle2, numberOnly=True, default=str(config.chatGPTApiMaxTokens))
            if maxtokens and not maxtokens.strip().lower() == config.exit_entry and int(maxtokens) > 0:
                config.chatGPTApiMaxTokens = int(maxtokens)
                if config.chatGPTApiMaxTokens > 4096 if config.chatGPTApiModel == "gpt-4-1106-preview" else tokenLimit: # 'gpt-4-1106-preview' supports at most 4096 completion tokens
                    config.chatGPTApiMaxTokens = 4096 if config.chatGPTApiModel == "gpt-4-1106-preview" else tokenLimit
                config.saveConfig()
                self.print3(f"Maximum tokens: {config.chatGPTApiMaxTokens}")

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
        if config.thisPlatform == "Windows":
            os.system(command)
        else:
            os.system(f"env QT_QPA_PLATFORM_PLUGIN_PATH='{config.env_QT_QPA_PLATFORM_PLUGIN_PATH}' {command}")

    def toggleMultiline(self):
        config.multilineInput = not config.multilineInput
        run_in_terminal(lambda: self.print(f"Multi-line input {'enabled' if config.multilineInput else 'disabled'}!"))
        if config.multilineInput:
            run_in_terminal(lambda: self.print("Use 'escape + enter' to complete your entry."))

    def isTtsAvailable(self):
        if config.tts:
            return True
        self.print("Text-to-speech feature not ready!\nTo, set up, either:\n* install 'VLC player'\n* install 'pygame'\n* define 'ttsCommand' in config.py")
        self.print("Read more at:\nhttps://github.com/eliranwong/letmedoit/wiki/letMeDoIt-Speaks")
        return False

    def toggleinputaudio(self):
        if self.isTtsAvailable:
            config.ttsInput = not config.ttsInput
            config.saveConfig()
            self.print3(f"Input Audio: '{'enabled' if config.ttsInput else 'disabled'}'!")

    def toggleresponseaudio(self):
        if self.isTtsAvailable:
            config.ttsOutput = not config.ttsOutput
            config.saveConfig()
            self.print3(f"Response Audio: '{'enabled' if config.ttsOutput else 'disabled'}'!")

    def defineTtsCommand(self):
        self.print("Define text-to-speech command below:")
        self.print("""* on macOS ['say -v "?"' to check voices], e.g.:\n'say' or 'say -r 200 -v Daniel'""")
        self.print("* on Ubuntu ['espeak --voices' to check voices], e.g.:\n'espeak' or 'espeak -s 175 -v en-gb'")
        self.print("* on Windows, simply enter 'windows' here to use Windows built-in speech engine") # letmedoit.ai will handle the command for Windows users
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
        self.print3(f"Word Wrap: '{'enabled' if config.wrapWords else 'disabled'}'!")

    def toggleMouseSupport(self):
        config.mouseSupport = not config.mouseSupport
        config.saveConfig()
        self.print3(f"Entry Mouse Support: '{'enabled' if config.mouseSupport else 'disabled'}'!")

    def toggleImprovedWriting(self):
        config.displayImprovedWriting = not config.displayImprovedWriting
        if config.displayImprovedWriting:
            self.print("Please specify the writing style below:")
            style = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.improvedWritingSytle)
            if style and not style in (config.exit_entry, config.cancel_entry):
                config.improvedWritingSytle = style
                config.saveConfig()
        self.print3(f"Improved Writing Display: '{'enabled' if config.displayImprovedWriting else 'disabled'}'!")

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
                #filename = re.sub('[\\\/\:\*\?\"\<\>\|]', "", messages[2 if config.customPredefinedContext.strip() else 1]["content"])[:40].strip()
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
                self.print2("Failed to save chat!\n")
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
            default=config.predefinedContext,
            text="Select a context:",
        )
        if predefinedContext:
            config.predefinedContext = predefinedContext
            if config.predefinedContext == "[custom]":
                self.print("Edit custom context below:")
                customContext = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.customPredefinedContext)
                if customContext and not customContext.strip().lower() == config.exit_entry:
                    config.customPredefinedContext = customContext.strip()
            self.showCurrentContext()
        else:
            # a way to quickly clean up context
            config.predefinedContext = "[none]"

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
        appName = config.letMeDoItName.split()[0].upper()
        terminal_width = shutil.get_terminal_size().columns
        try:
            from art import text2art
            if terminal_width >= 32:
                logo = text2art(appName, font="cybermedum")
            elif terminal_width >= 20:
                logo = text2art(" ".join(appName) + " ", font="white_bubble")
            else:
                logo = config.letMeDoItName
            logo = logo[:-1] # remove the linebreak at the end
        except:
            logo = config.letMeDoItName
        print_formatted_text(HTML(f"<{config.terminalCommandEntryColor2}>{logo}</{config.terminalCommandEntryColor2}>"))

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
            messages = self.resetMessages()
            #self.print(f"startup directory:\n{startupdirectory}")
            print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>Directory:</{config.terminalPromptIndicatorColor2}> {startupdirectory}"))
            self.print(self.divider)

            config.conversationStarted = False
            return (startupdirectory, messages)
        startupdirectory, config.currentMessages = startChat()
        config.multilineInput = False
        featuresLower = [i.lower() for i in self.actions] + ["...", ".save", ".share"]
        while True:
            # default toolbar text
            config.dynamicToolBarText = " [ctrl+q] exit [ctrl+k] shortcut keys "
            # display current directory if changed
            currentDirectory = os.getcwd()
            if not currentDirectory == startupdirectory:
                #self.print(self.divider)
                self.print3(f"Current directory: {currentDirectory}")
                self.print(self.divider)
                startupdirectory = currentDirectory
            # default input entry
            accept_default = config.accept_default
            config.accept_default = False
            defaultEntry = config.defaultEntry
            if os.path.isfile(defaultEntry):
                defaultEntry = f'File: "{defaultEntry}"\n'
            elif os.path.isdir(defaultEntry):
                defaultEntry = f'Folder: "{defaultEntry}"\n'
            config.defaultEntry = ""
            # input suggestions
            inputSuggestions = config.inputSuggestions[:] + self.getDirectoryList() if config.developer else config.inputSuggestions
            completer = WordCompleter(inputSuggestions, ignore_case=True) if inputSuggestions else None
            userInput = self.prompts.simplePrompt(promptSession=self.terminal_chat_session, completer=completer, default=defaultEntry, accept_default=accept_default, validator=tokenValidator, bottom_toolbar=getDynamicToolBar)
            
            # update system message when user enter a new input
            config.currentMessages = self.updateSystemMessage(config.currentMessages)
            
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
                if not default:
                    default = os.getcwd()
                userPath = self.getPath.getPath(message=f"{prefix}<{config.terminalCommandEntryColor2}>[add a path here]</{config.terminalCommandEntryColor2}>{suffix}", promptIndicator=">>> ", empty_to_cancel=True, default=default)
                config.defaultEntry = f"{prefix}{userPath}{suffix}"
                userInput = ""
            elif not userInputLower:
                userInput = config.blankEntryAction
            if userInput == "...":
                userInputLower = self.runOptions(userInput)

            # replace alias, if any with full entry
            for alias, fullEntry in config.aliases.items():
                #userInput = re.sub(alias, fullEntry, userInput) # error on Windows coz of Windows path
                userInput = userInput.replace(alias, fullEntry)

            # open file / directory directly
            docs_path = SharedUtil.isExistingPath(userInput)
            if os.path.isfile(docs_path):
                os.system(f"{config.open} {docs_path}")
                continue
            elif os.path.isdir(docs_path):
                try:
                    os.chdir(docs_path)
                    self.print3(f"Directory changed to: {docs_path}")
                    self.getPath.displayDirectoryContent()
                    continue
                except:
                    pass

            # try eval
            if not userInput == "...":
                try:
                    value = eval(userInput) # it solve simple math, e.g. 1+1, or read variables, e.g. dir(config)
                    if value is not None:
                        #print(value)
                        pprint.pprint(value)
                        continue
                    elif re.search("^print\([^\)\)]+?\)$", userInput):
                        continue
                except:
                    pass
            # try to run as a python script first
            try:
                exec(userInput, globals())
                continue
            except:
                pass

            if userInput.startswith("!"):
                self.runSystemCommand(userInput)
            elif userInput.startswith("```") and userInput.endswith("```") and not userInput == "``````":
                userInput = re.sub("```python", "```", userInput)
                self.runPythonScript(userInput)
            elif userInputLower == config.exit_entry:
                self.saveChat(config.currentMessages)
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
                if not config.applyPredefinedContextAlways and config.conversationStarted:
                    self.saveChat(config.currentMessages)
                    startupdirectory, config.currentMessages = startChat()
            elif userInputLower == ".new" and config.conversationStarted:
                self.saveChat(config.currentMessages)
                startupdirectory, config.currentMessages = startChat()
            elif userInputLower in (".share", ".save") and config.conversationStarted:
                self.saveChat(config.currentMessages, openFile=True)
            elif userInput and not userInputLower in featuresLower:
                try:
                    if userInput and config.ttsInput:
                        TTSUtil.play(userInput)
                    # Feature: improve writing:
                    specialEntryPattern = "\[CALL_[^\[\]]*?\]|\[NO_FUNCTION_CALL\]|\[NO_SCREENING\]"
                    specialEntry = re.search(specialEntryPattern, userInput)
                    specialEntry = specialEntry.group(0) if specialEntry else ""
                    userInput = re.sub(specialEntryPattern, "", userInput) # remove special entry temporarily
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
                    if specialEntry:
                        userInput = f"{userInput}{specialEntry}"
                    # refine messages before running completion
                    fineTunedUserInput = self.fineTuneUserInput(userInput)
                    # in case of translation
                    if config.predefinedContext == "Let me Translate" and fineTunedUserInput.startswith("Assist me by acting as a translator.\nPlease translate"):
                        self.print("Please specify below the language you would like the content to be translated into:")
                        language = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.translateToLanguage)
                        if language and not language.strip().lower() in (config.cancel_entry, config.exit_entry):
                            fineTunedUserInput = f"{fineTunedUserInput}\n\nPlease translate the content into <language>{language}</language>."
                            config.translateToLanguage = language
                        else:
                            continue
                    # clear config.predefinedContextTemp if any
                    if config.predefinedContextTemp:
                        config.predefinedContext = config.predefinedContextTemp
                        config.predefinedContextTemp = ""
                    # check special entries
                    noFunctionCall = (("[NO_FUNCTION_CALL]" in fineTunedUserInput) or config.predefinedContext.startswith("Counselling - ") or config.predefinedContext.endswith("Counselling"))
                    noScreening = ("[NO_SCREENING]" in fineTunedUserInput)
                    checkCallSpecificFunction = re.search("\[CALL_([^\[\]]+?)\]", fineTunedUserInput)
                    config.runSpecificFuntion = checkCallSpecificFunction.group(1) if checkCallSpecificFunction and checkCallSpecificFunction.group(1) in config.pluginsWithFunctionCall else ""
                    if config.developer and config.runSpecificFuntion:
                        #self.print(f"calling function '{config.runSpecificFuntion}' ...")
                        print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>Calling function</{config.terminalPromptIndicatorColor2}> <{config.terminalCommandEntryColor2}>'{config.runSpecificFuntion}'</{config.terminalCommandEntryColor2}> <{config.terminalPromptIndicatorColor2}>...</{config.terminalPromptIndicatorColor2}>"))
                    fineTunedUserInput = re.sub(specialEntryPattern, "", fineTunedUserInput)

                    # remove enhanced screening option from v2.0.1 as handling of function calls improved
                    # python execution
                    #self.screenAction = ""
                    #if config.enhanceCommandExecution and not noScreening and not noFunctionCall:
                    #    config.currentMessages = self.screening(config.currentMessages, fineTunedUserInput)
                    #else:
                    #    config.currentMessages.append({"role": "user", "content": fineTunedUserInput})
                    config.currentMessages.append({"role": "user", "content": fineTunedUserInput})

                    # start spinning
                    config.stop_event = threading.Event()
                    config.spinner_thread = threading.Thread(target=self.spinning_animation, args=(config.stop_event,))
                    config.spinner_thread.start()

                    # force loading internet searches
                    #if config.loadingInternetSearches == "always" and not self.screenAction in ("termux", "python", "web", "system"):
                    if config.loadingInternetSearches == "always":
                        try:
                            config.currentMessages = self.runFunction(config.currentMessages, config.integrate_google_searches_signature, "integrate_google_searches")
                        except:
                            self.print("Unable to load internet resources.")
                            SharedUtil.showErrors()

                    config.pagerContent = ""
                    self.addPagerContent = True

                    #if config.conversationStarted:
                    #    config.currentMessages = self.moveForwardSystemMessage(config.currentMessages)
                    completion = self.runCompletion(config.currentMessages, noFunctionCall)
                    # stop spinning
                    self.runPython = True
                    self.stopSpinning()

                    # Create a new thread for the streaming task
                    self.streaming_finished = False
                    streaming_event = threading.Event()
                    self.streaming_thread = threading.Thread(target=self.streamOutputs, args=(streaming_event, completion,))
                    # Start the streaming thread
                    self.streaming_thread.start()

                    # wait while text output is steaming; capture key combo 'ctrl+q' or 'ctrl+z' to stop the streaming
                    self.keyToStopStreaming(streaming_event)

                    # when streaming is done or when user press "ctrl+q"
                    self.streaming_thread.join()

                    #print(config.currentMessages)

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
                    self.saveChat(config.currentMessages)
                    startupdirectory, config.currentMessages = startChat()

    def keyToStopStreaming(self, streaming_event):
        async def readKeys() -> None:
            done = False
            input = create_input()

            def keys_ready():
                nonlocal done
                for key_press in input.read_keys():
                    #print(key_press)
                    if key_press.key in (Keys.ControlQ, Keys.ControlZ):
                        print("\n")
                        done = True
                        streaming_event.set()

            with input.raw_mode():
                with input.attach(keys_ready):
                    while not done:
                        if self.streaming_finished:
                            break
                        await asyncio.sleep(0.1)

        asyncio.run(readKeys())

    def streamOutputs(self, streaming_event, completion):
        terminal_width = shutil.get_terminal_size().columns

        def finishOutputs(wrapWords, chat_response, terminal_width=terminal_width):
            config.wrapWords = wrapWords
            # reset config.tempChunk
            config.tempChunk = ""
            print("\n")
            # add chat response to messages
            if chat_response:
                config.currentMessages.append({"role": "assistant", "content": chat_response})
            # auto pager feature
            config.pagerContent += self.wrapText(chat_response, terminal_width) if config.wrapWords else chat_response
            self.addPagerContent = False
            if config.pagerView:
                self.launchPager(config.pagerContent)
            # finishing
            config.conversationStarted = True
            self.streaming_finished = True

        chat_response = ""
        self.lineWidth = 0
        blockStart = False
        wrapWords = config.wrapWords
        for event in completion:
            if not streaming_event.is_set():
                # RETRIEVE THE TEXT FROM THE RESPONSE
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
            else:
                finishOutputs(wrapWords, chat_response)
                return None
        
        finishOutputs(wrapWords, chat_response)

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
        self.setAPIkey()
        try:
            self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content" : "hello"}],
                n=1,
                max_tokens=10,
            )
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