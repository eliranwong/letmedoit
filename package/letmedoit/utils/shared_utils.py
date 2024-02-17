from letmedoit import config
from packaging import version
from bs4 import BeautifulSoup
import platform, shutil, subprocess, os, pydoc, webbrowser, re, socket, wcwidth, unicodedata, traceback, html2text
import datetime, requests, netifaces, textwrap, json, geocoder, base64, getpass, pendulum, pkg_resources
import pygments
from pygments.lexers.python import PythonLexer
from pygments.styles import get_style_by_name
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit import prompt
import tiktoken
import openai
from openai import OpenAI
from urllib.parse import quote
from pathlib import Path
from PIL import Image
if not config.isTermux:
    from autogen.retrieve_utils import TEXT_FORMATS


def check_openai_errors(func):
    def wrapper(*args, **kwargs):
        try: 
            return func(*args, **kwargs)
        except openai.APIError as e:
            print("Error: Issue on OpenAI side.")
            print("Solution: Retry your request after a brief wait and contact us if the issue persists.")
        except openai.APIConnectionError as e:
            print("Error: Issue connecting to our services.")
            print("Solution: Check your network settings, proxy configuration, SSL certificates, or firewall rules.")
        except openai.APITimeoutError as e:
            print("Error: Request timed out.")
            print("Solution: Retry your request after a brief wait and contact us if the issue persists.")
        except openai.AuthenticationError as e:
            print("Error: Your API key or token was invalid, expired, or revoked.")
            print("Solution: Check your API key or token and make sure it is correct and active. You may need to generate a new one from your account dashboard.")
            HealthCheck.changeAPIkey()
        except openai.BadRequestError as e:
            print("Error: Your request was malformed or missing some required parameters, such as a token or an input.")
            print("Solution: The error message should advise you on the specific error made. Check the [documentation](https://platform.openai.com/docs/api-reference/) for the specific API method you are calling and make sure you are sending valid and complete parameters. You may also need to check the encoding, format, or size of your request data.")
        except openai.ConflictError as e:
            print("Error: The resource was updated by another request.")
            print("Solution: Try to update the resource again and ensure no other requests are trying to update it.")
        except openai.InternalServerError as e:
            print("Error: Issue on OpenAI servers.")
            print("Solution: Retry your request after a brief wait and contact us if the issue persists. Check the [status page](https://status.openai.com).")
        except openai.NotFoundError as e:
            print("Error: Requested resource does not exist.")
            print("Solution: Ensure you are the correct resource identifier.")
        except openai.PermissionDeniedError as e:
            print("Error: You don't have access to the requested resource.")
            print("Solution: Ensure you are using the correct API key, organization ID, and resource ID.")
        except openai.RateLimitError as e:
            print("Error: You have hit your assigned rate limit.")
            print("Solution: Pace your requests. Read more in OpenAI [Rate limit guide](https://platform.openai.com/docs/guides/rate-limits).")
        except openai.UnprocessableEntityError as e:
            print("Error: Unable to process the request despite the format being correct.")
            print("Solution: Please try the request again.")
        except:
            print(traceback.format_exc())
    return wrapper

class SharedUtil:

    # token limit
    # reference: https://platform.openai.com/docs/models/gpt-4
    tokenLimits = {
        "gpt-4-turbo-preview": 128000, # Returns a maximum of 4,096 output tokens.
        "gpt-4-0125-preview": 128000, # Returns a maximum of 4,096 output tokens.
        "gpt-4-1106-preview": 128000, # Returns a maximum of 4,096 output tokens.
        "gpt-3.5-turbo": 16385, # Returns a maximum of 4,096 output tokens.
        "gpt-3.5-turbo-16k": 16385,
        "gpt-4": 8192,
        "gpt-4-32k": 32768,
    }

    @staticmethod
    @check_openai_errors
    def checkCompletion():
        SharedUtil.setAPIkey()
        config.oai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content" : "hello"}],
            n=1,
            max_tokens=10,
        )

    @staticmethod
    def setAPIkey():
        # instantiate a client that can shared with plugins
        os.environ["OPENAI_API_KEY"] = config.openaiApiKey
        config.oai_client = OpenAI()
        # set variable 'OAI_CONFIG_LIST' to work with pyautogen
        oai_config_list = []
        for model in SharedUtil.tokenLimits.keys():
            oai_config_list.append({"model": model, "api_key": config.openaiApiKey})
        os.environ["OAI_CONFIG_LIST"] = json.dumps(oai_config_list)

    @staticmethod
    def getPackageInstalledVersion(package):
        try:
            installed_version = pkg_resources.get_distribution(package).version
            return version.parse(installed_version)
        except pkg_resources.DistributionNotFound:
            return None

    @staticmethod
    def getPackageLatestVersion(package):
        try:
            response = requests.get(f"https://pypi.org/pypi/{package}/json", timeout=10)
            latest_version = response.json()['info']['version']
            return version.parse(latest_version)
        except:
            return None

    @staticmethod
    def isPackageUpgradable(package):
        latest_version = SharedUtil.getPackageLatestVersion(package)
        installed_version = SharedUtil.getPackageInstalledVersion(package)
        return (latest_version > installed_version)

    # handle document path dragged to the terminal
    @staticmethod
    def isExistingPath(docs_path):
        docs_path = docs_path.strip()
        search_replace = (
            ("^'(.*?)'$", r"\1"),
            ('^(File|Folder): "(.*?)"$', r"\2"),
        )
        for search, replace in search_replace:
            docs_path = re.sub(search, replace, docs_path)
        if "\\ " in docs_path or "\(" in docs_path:
            search_replace = (
                ("\\ ", " "),
                ("\(", "("),
            )
            for search, replace in search_replace:
                docs_path = docs_path.replace(search, replace)
        return docs_path if os.path.exists(os.path.expanduser(docs_path)) else ""

    @staticmethod
    def getCurrentDateTime():
        current_datetime = datetime.datetime.now()
        return current_datetime.strftime("%Y-%m-%d_%H_%M_%S")

    @staticmethod
    def showErrors():
        trace = traceback.format_exc()
        print(trace if config.developer else "Error encountered!")
        return trace

    @staticmethod
    def addTimeStamp(content):
        time = re.sub("\.[^\.]+?$", "", str(datetime.datetime.now()))
        return f"{content}\n[Current time: {time}]"

    @staticmethod
    def downloadWebContent(url, timeout=60, folder="", ignoreKind=False):
        config.print2("Downloading web content ...")
        hasExt = re.search("\.([^\./]+?)$", url)
        supported_documents = TEXT_FORMATS[:]
        supported_documents.remove("org")

        response = requests.get(url, timeout=timeout)
        folder = folder if folder and os.path.isdir(folder) else os.path.join(config.letMeDoItAIFolder, "temp")
        filename = quote(url, safe="")
        def downloadBinary(filename=filename):
            filename = os.path.join(folder, filename)
            with open(filename, "wb") as fileObj:
                fileObj.write(response.content)
            return filename
        def downloadHTML(filename=filename):
            filename = os.path.join(folder, f"{filename}.html")
            with open(filename, "w", encoding="utf-8") as fileObj:
                fileObj.write(response.text)
            return filename

        try:
            if ignoreKind:
                filename = downloadBinary()
                config.print3(f"Downloaded at: {filename}")
                return ("any", filename)
            elif hasExt and hasExt.group(1) in supported_documents:
                return ("document", downloadBinary())
            elif SharedUtil.is_valid_image_url(url):
                return ("image", downloadBinary())
            else:
                # download content as text
                # Save the content to a html file
                return ("text", downloadHTML())
        except:
            SharedUtil.showErrors()
            return ("", "")

    @staticmethod
    def is_valid_url(url):
        # Regular expression pattern for URL validation
        pattern = re.compile(
            r'^(http|https)://'  # http:// or https://
            r'([a-zA-Z0-9.-]+)'  # domain name
            r'(\.[a-zA-Z]{2,63})'  # dot and top-level domain (e.g. .com, .org)
            r'(:[0-9]{1,5})?'  # optional port number
            r'(/.*)?$'  # optional path
        )
        return bool(re.match(pattern, url))

    @staticmethod
    def is_valid_image_url(url): 
        try: 
            response = requests.head(url, timeout=30)
            content_type = response.headers['content-type'] 
            if 'image' in content_type: 
                return True 
            else: 
                return False 
        except requests.exceptions.RequestException: 
            return False

    @staticmethod
    def is_valid_image_file(file_path):
        try:
            # Open the image file
            with Image.open(file_path) as img:
                # Check if the file format is supported by PIL
                img.verify()
                return True
        except (IOError, SyntaxError) as e:
            # The file path is not a valid image file path
            return False

    # Function to encode the image
    @staticmethod
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        os.path.splitext(os.path.basename(image_path))[1]
        return f"data:image/png;base64,{base64_image}"

    def getWebText(url):
        try:
            # Download webpage content
            response = requests.get(url, timeout=30)
            # Parse the HTML content to extract text
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.get_text()
        except:
            return ""

    @staticmethod
    def transformText(text):
        for transformer in config.chatGPTTransformers:
                text = transformer(text)
        return text

    @staticmethod
    def getPygmentsStyle():
        theme = config.pygments_style if config.pygments_style else "stata-dark" if not config.terminalResourceLinkColor.startswith("ansibright") else "stata-light"
        return style_from_pygments_cls(get_style_by_name(theme))

    @staticmethod
    def displayPythonCode(code):
        if config.developer or config.codeDisplay:
            config.print("```python")
            tokens = list(pygments.lex(code, lexer=PythonLexer()))
            print_formatted_text(PygmentsTokens(tokens), style=SharedUtil.getPygmentsStyle())
            config.print("```")

    @staticmethod
    def showAndExecutePythonCode(code):
        SharedUtil.displayPythonCode(code)
        config.stopSpinning()
        refinedCode = SharedUtil.fineTunePythonCode(code)
        information = SharedUtil.executePythonCode(refinedCode)
        return information

    @staticmethod
    def executePythonCode(code):
        try:
            exec(code, globals())
            pythonFunctionResponse = SharedUtil.getPythonFunctionResponse(code)
        except:
            trace = SharedUtil.showErrors()
            config.print(config.divider)
            if config.max_consecutive_auto_heal > 0:
                return SharedUtil.autoHealPythonCode(code, trace)
            else:
                return "[INVALID]"
        if not pythonFunctionResponse:
            return ""
        return json.dumps({"information": pythonFunctionResponse})

    @staticmethod
    def convertFunctionSignaturesIntoTools(functionSignatures):
        return [{"type": "function", "function": func} for func in functionSignatures]

    @staticmethod
    def getPythonFunctionResponse(code):
        return str(config.pythonFunctionResponse) if config.pythonFunctionResponse is not None and (type(config.pythonFunctionResponse) in (int, float, str, list, tuple, dict, set, bool) or str(type(config.pythonFunctionResponse)).startswith("<class 'numpy.")) and not ("os.system(" in code) else ""

    @staticmethod
    def autoHealPythonCode(code, trace):
        for i in range(config.max_consecutive_auto_heal):
            userInput = f"Original python code:\n```\n{code}\n```\n\nTraceback:\n```\n{trace}\n```"
            config.print3(f"Auto-correction attempt: {(i + 1)}")
            function_call_message, function_call_response = SharedUtil.getSingleFunctionResponse(userInput, [config.chatGPTApiFunctionSignatures["heal_python"]], "heal_python")
            # display response
            config.print(config.divider)
            if config.developer:
                print(function_call_response)
            else:
                config.print("Executed!" if function_call_response == "EXECUTED" else "Failed!")
            if function_call_response == "EXECUTED":
                break
            else:
                code = json.loads(function_call_message["function_call"]["arguments"]).get("fix")
                trace = function_call_response
            config.print(config.divider)
        # return information if any
        if function_call_response == "EXECUTED":
            pythonFunctionResponse = SharedUtil.getPythonFunctionResponse(code)
            if pythonFunctionResponse:
                return json.dumps({"information": pythonFunctionResponse})
            else:
                return ""
        # ask if user want to manually edit the code
        config.print(f"Failed to execute the code {(config.max_consecutive_auto_heal + 1)} times in a row!")
        config.print("Do you want to manually edit it? [y]es / [N]o")
        confirmation = prompt(style=config.promptStyle2, default="N")
        if confirmation.lower() in ("y", "yes"):
            config.defaultEntry = f"```python\n{code}\n```"
            return ""
        else:
            return "[INVALID]"

    @staticmethod
    def fineTunePythonCode(code):
        # dedent
        code = textwrap.dedent(code).rstrip()
        # capture print output
        config.pythonFunctionResponse = ""
        insert_string = "from letmedoit import config\nconfig.pythonFunctionResponse = "
        code = re.sub("^!(.*?)$", r'import os\nos.system(""" \1 """)', code, flags=re.M)
        if "\n" in code:
            substrings = code.rsplit("\n", 1)
            lastLine = re.sub("print\((.*)\)", r"\1", substrings[-1])
            if lastLine.startswith(" "):
                lastLine = re.sub("^([ ]+?)([^ ].*?)$", r"\1config.pythonFunctionResponse = \2", lastLine)
                code = f"from letmedoit import config\n{substrings[0]}\n{lastLine}"
            else:
                lastLine = f"{insert_string}{lastLine}"
                code = f"{substrings[0]}\n{lastLine}"
        else:
            code = f"{insert_string}{code}"
        return code

    @staticmethod
    def getDynamicTokens(messages, functionSignatures=None):
        if functionSignatures is None:
            functionTokens = 0
        else:
            functionTokens = SharedUtil.count_tokens_from_functions(functionSignatures)
        tokenLimit = SharedUtil.tokenLimits[config.chatGPTApiModel]
        currentMessagesTokens = SharedUtil.count_tokens_from_messages(messages) + functionTokens
        availableTokens = tokenLimit - currentMessagesTokens
        if availableTokens >= config.chatGPTApiMaxTokens:
            return config.chatGPTApiMaxTokens
        elif (config.chatGPTApiMaxTokens > availableTokens > config.chatGPTApiMinTokens):
            return availableTokens
        return config.chatGPTApiMinTokens

    @staticmethod
    def count_tokens_from_functions(functionSignatures, model=""):
        count = 0
        if not model:
            model = config.chatGPTApiModel
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        for i in functionSignatures:
            count += len(encoding.encode(str(i)))
        return count

    # The following method was modified from source:
    # https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
    @staticmethod
    def count_tokens_from_messages(messages, model=""):
        if not model:
            model = config.chatGPTApiModel

        """Return the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if model in {
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-0125",
                "gpt-3.5-turbo-1106",
                "gpt-3.5-turbo-0613",
                "gpt-3.5-turbo-16k",
                "gpt-3.5-turbo-16k-0613",
                "gpt-4-turbo-preview",
                "gpt-4-0125-preview",
                "gpt-4-1106-preview",
                "gpt-4-0314",
                "gpt-4-32k-0314",
                "gpt-4",
                "gpt-4-0613",
                "gpt-4-32k",
                "gpt-4-32k-0613",
            }:
            tokens_per_message = 3
            tokens_per_name = 1
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif "gpt-3.5-turbo" in model:
            #print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
            return SharedUtil.count_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
        elif "gpt-4" in model:
            #print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
            return SharedUtil.count_tokens_from_messages(messages, model="gpt-4-0613")
        else:
            raise NotImplementedError(
                f"""count_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
            )
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            if not "content" in message or not message.get("content", ""):
                num_tokens += len(encoding.encode(str(message)))
            else:
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":
                        num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

    @staticmethod
    def riskAssessment(code):
        content = f"""You are a senior python engineer.
Assess the risk level of damaging my device upon executing the python code that I will provide for you.
Answer me either 'high', 'medium' or 'low', without giving me any extra information.
e.g. file deletions or similar significant impacts are regarded as 'high' level.
Acess the risk level of this Python code:
```
{code}
```"""
        try:
            answer = SharedUtil.getSingleChatResponse(content, temperature=0.0)
            if not answer:
                answer = "high"
            answer = re.sub("[^A-Za-z]", "", answer).lower()
            if not answer in ("high", "medium", "low"):
                answer = "high"
            return answer
        except:
            return "high"

    @staticmethod
    def getSingleFunctionResponse(userInput, functionSignatures, function_name, temperature=None):
        messages=[{"role": "user", "content" : userInput}]
        return config.getFunctionMessageAndResponse(messages, functionSignatures, function_name, temperature=temperature)

    @staticmethod
    def getSingleChatResponse(userInput, temperature=None):
        try:
            completion = OpenAI().chat.completions.create(
                model=config.chatGPTApiModel,
                messages=[{"role": "user", "content" : userInput}],
                n=1,
                temperature=temperature if temperature is not None else config.llmTemperature,
                max_tokens=config.chatGPTApiMaxTokens,
            )
            return completion.choices[0].message.content
        except:
            return ""

    # streaming
    @staticmethod
    def getToolArgumentsFromStreams(completion):
        toolArguments = {}
        for event in completion:
            delta = event.choices[0].delta
            if delta and delta.tool_calls:
                for tool_call in delta.tool_calls:
                    # handle functions
                    if tool_call.function:
                        func_index = tool_call.index
                        if func_index in toolArguments:
                            toolArguments[func_index] += tool_call.function.arguments
                        else:
                            toolArguments[func_index] = tool_call.function.arguments
                    # may support non functions later
        return toolArguments

    @staticmethod
    def get_wan_ip():
        try:
            response = requests.get('https://api.ipify.org?format=json', timeout=5)
            data = response.json()
            return data['ip']
        except:
            return ""

    @staticmethod
    def get_local_ip():
        interfaces = netifaces.interfaces()
        for interface in interfaces:
            addresses = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addresses:
                for address in addresses[netifaces.AF_INET]:
                    ip = address['addr']
                    if ip != '127.0.0.1':
                        return ip

    @staticmethod
    def getDayOfWeek():
        if config.isTermux:
            return ""
        else:
            now = pendulum.now() 
            return now.format('dddd')

    @staticmethod
    def getWeather(latlng=""):
        # get current weather information
        # Reference: https://openweathermap.org/api/one-call-3

        if not config.openweathermapApi:
            return None

        # latitude, longitude
        if not latlng:
            latlng = geocoder.ip('me').latlng

        try:
            latitude, longitude = latlng
            # Build the URL for the weather API
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={config.openweathermapApi}&units=metric"
            # Make the request to the API
            response = requests.get(url)
            # Parse the JSON response
            data = json.loads(response.text)
            # Get the current weather condition
            weather_condition = data["weather"][0]["description"]
            # Get the current temperature in Celsius
            temperature_celsius = data["main"]["temp"]

            # Convert the temperature to Fahrenheit
            #temperature_fahrenheit = (temperature_celsius * 9/5) + 32

            # Print the weather condition and temperature
            #print(f"The current weather condition is {weather_condition}.")
            #print(f"The current temperature is {temperature_fahrenheit} degrees Fahrenheit.")
            return temperature_celsius, weather_condition
        except:
            SharedUtil.showErrors()
            return None

    @staticmethod
    def getDeviceInfo(includeIp=False):
        g = geocoder.ip('me')
        if hasattr(config, "thisPlatform"):
            thisPlatform = config.thisPlatform
        else:
            thisPlatform = platform.system()
            if thisPlatform == "Darwin":
                thisPlatform = "macOS"
        if config.includeIpInSystemMessageTemp or includeIp or (config.includeIpInSystemMessage and config.includeIpInSystemMessageTemp):
            wan_ip = SharedUtil.get_wan_ip()
            local_ip = SharedUtil.get_local_ip()
            ipInfo = f'''Wan ip: {wan_ip}
Local ip: {local_ip}
'''
        else:
            ipInfo = ""
        if config.isTermux:
            dayOfWeek = ""
        else:
            dayOfWeek = SharedUtil.getDayOfWeek()
            dayOfWeek = f"Current day of the week: {dayOfWeek}"
        return f"""Operating system: {thisPlatform}
Version: {platform.version()}
Machine: {platform.machine()}
Architecture: {platform.architecture()[0]}
Processor: {platform.processor()}
Hostname: {socket.gethostname()}
Username: {getpass.getuser()}
Python version: {platform.python_version()}
Python implementation: {platform.python_implementation()}
Current directory: {os.getcwd()}
Current time: {str(datetime.datetime.now())}
{dayOfWeek}
{ipInfo}Latitude & longitude: {g.latlng}
Country: {g.country}
State: {g.state}
City: {g.city}"""

    @staticmethod
    def getStringWidth(text):
        width = 0
        for character in text:
            width += wcwidth.wcwidth(character)
        return width

    @staticmethod
    def is_CJK(text):
        for char in text:
            if 'CJK' in unicodedata.name(char):
                return True
        return False

    @staticmethod
    def isPackageInstalled(package):
        return True if shutil.which(package.split(" ", 1)[0]) else False

    @staticmethod
    def getCliOutput(cli):
        try:
            process = subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, *_ = process.communicate()
            return stdout.decode("utf-8")
        except:
            return ""

    @staticmethod
    def textTool(tool="", content=""):
        command = re.sub(" .*?$", "", tool.strip())
        if command and SharedUtil.isPackageInstalled(command):
            pydoc.pipepager(content, cmd=tool)
            if SharedUtil.isPackageInstalled("pkill"):
                os.system(f"pkill {command}")
        return ""

    @staticmethod
    def runSystemCommand(command):
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout  # Captured standard output
        error = result.stderr  # Captured standard error
        response = ""
        response += f"# Output:\n{output}"
        if error.strip():
            response += f"\n# Error:\n{error}"
        return response

    # Function to convert HTML to Markdown
    @staticmethod
    def convert_html_to_markdown(html_string):
        # Create an instance of the HTML2Text converter
        converter = html2text.HTML2Text()
        # Convert the HTML string to Markdown
        markdown_string = converter.handle(html_string)
        # Return the Markdown string
        return markdown_string

    @staticmethod
    def openURL(url):
        config.stopSpinning()
        if config.terminalEnableTermuxAPI:
            command = f'''termux-open-url "{url}"'''
            SharedUtil.runSystemCommand(command)
        else:
            webbrowser.open(url)

    @staticmethod
    def getStorageDir():
        storageDir = os.path.join(os.path.expanduser('~'), config.letMeDoItName.split()[0].lower())
        try:
            Path(storageDir).mkdir(parents=True, exist_ok=True)
        except:
            pass
        return storageDir if os.path.isdir(storageDir) else ""

    @staticmethod
    def getFiles():
        storageDir = SharedUtil.getStorageDir()
        if config.storagedirectory and not os.path.isdir(config.storagedirectory):
            config.storagedirectory = ""
        storageDir = storageDir if storageDir else os.path.join(config.letMeDoItAIFolder, "files")
        return config.storagedirectory if config.storagedirectory else storageDir