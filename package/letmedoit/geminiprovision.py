import vertexai, os, traceback, argparse, re
from vertexai.preview.generative_models import GenerativeModel
from vertexai.generative_models._generative_models import (
    GenerationConfig,
    HarmCategory,
    HarmBlockThreshold,
)
from letmedoit import config
from letmedoit.health_check import HealthCheck
if not hasattr(config, "exit_entry"):
    HealthCheck.setBasicConfig()
    HealthCheck.saveConfig()
    print("Updated!")
HealthCheck.setPrint()
#import pygments
#from pygments.lexers.markup import MarkdownLexer
#from prompt_toolkit.formatted_text import PygmentsTokens
#from prompt_toolkit import print_formatted_text
from prompt_toolkit.styles import Style
from prompt_toolkit.keys import Keys
from prompt_toolkit.input import create_input
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import clear
from pathlib import Path
import asyncio, threading, shutil, textwrap

# To work with gemini-pro-vision
from PIL import Image as im
import requests
import http.client
import typing
import urllib.request
from vertexai.preview.generative_models import Image
from vertexai.preview import generative_models

# Install google-cloud-aiplatform FIRST!
#!pip install --upgrade google-cloud-aiplatform

# Keep for reference; unnecessary for api key authentication with json file
# (developer): Update and un-comment below lines
#project_id = "letmedoitai"
#location = "us-central1"
#vertexai.init(project=project_id, location=location)


class GeminiPro:

    def __init__(self, name="Gemini Pro", temperature=0.9, max_output_tokens=8192):
        # authentication
        authpath1 = os.path.join(HealthCheck.getFiles(), "credentials_googleaistudio.json")
        if os.path.isfile(authpath1):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = authpath1
            self.runnable = True
        else:
            print(f"API key json file '{authpath1}' not found!")
            print("Read https://github.com/eliranwong/letmedoit/wiki/Google-API-Setup for setting up Google API.")
            self.runnable = False
        # initiation
        vertexai.init()
        self.name, self.temperature = name, temperature
        self.generation_config=GenerationConfig(
            temperature=temperature, # 0.0-1.0; default 0.9
            max_output_tokens=max_output_tokens, # default
            candidate_count=1,
        )
        self.safety_settings={
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        }
        self.defaultPrompt = ""
        self.enableVision = (os.path.realpath(__file__).endswith("vision.py"))

    def wrapText(self, content, terminal_width):
        return "\n".join([textwrap.fill(line, width=terminal_width) for line in content.split("\n")])

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
                    itemWidth = HealthCheck.getStringWidth(item)
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
            answerWidth = HealthCheck.getStringWidth(answer)
            newLineWidth = self.lineWidth + answerWidth
            if newLineWidth > terminal_width:
                print(f"\n{answer}", end='', flush=True)
                self.lineWidth = answerWidth
            else:
                print(answer, end='', flush=True)
                self.lineWidth += answerWidth

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

    def streamOutputs(self, streaming_event, completion, prompt):
        terminal_width = shutil.get_terminal_size().columns

        def finishOutputs(wrapWords, chat_response, terminal_width=terminal_width):
            config.wrapWords = wrapWords
            # reset config.tempChunk
            config.tempChunk = ""
            print("\n")
            # add chat response to messages
            if hasattr(config, "currentMessages") and chat_response:
                config.currentMessages.append({"role": "assistant", "content": chat_response})
            # auto pager feature
            if hasattr(config, "pagerView"):
                config.pagerContent += self.wrapText(chat_response, terminal_width) if config.wrapWords else chat_response
                self.addPagerContent = False
                if config.pagerView:
                    self.launchPager(config.pagerContent)
            # finishing
            if hasattr(config, "conversationStarted"):
                config.conversationStarted = True
            self.streaming_finished = True

        chat_response = ""
        self.lineWidth = 0
        blockStart = False
        wrapWords = config.wrapWords
        for event in completion:
            if not streaming_event.is_set() and not self.streaming_finished:
                # RETRIEVE THE TEXT FROM THE RESPONSE
                # vertex
                #print(str(event.candidates[0].content))
                function_call = ("function_call" in str(event.candidates[0].content))
                if not function_call:
                    answer = event.text
                # openai
                #answer = event.choices[0].delta.content
                #answer = SharedUtil.transformText(answer)
                # STREAM THE ANSWER
                if function_call:
                    # assume only one tool is in place
                    try:
                        function_args = dict(event.candidates[0].content.parts[0].function_call.args)
                        files = function_args["files"]
                        if not files or (len(files) == 1 and not files[0]): # {'files': [''], 'query': 'my query'}
                            self.defaultPrompt = f"{prompt}\n[NO_FUNCTION_CALL]"
                        else:
                            HealthCheck.print2("Running Gemini Pro Vision ...")
                            self.analyze_images(function_args)
                    except:
                        self.defaultPrompt = f"{prompt}\n[NO_FUNCTION_CALL]"
                    self.streaming_finished = True
                elif answer is not None:
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
                    #self.readAnswer(answer)
            else:
                finishOutputs(wrapWords, chat_response)
                return None
        
        finishOutputs(wrapWords, chat_response)

    def run(self, prompt=""):
        if self.defaultPrompt:
            prompt, self.defaultPrompt = self.defaultPrompt, ""
        historyFolder = os.path.join(HealthCheck.getFiles(), "history")
        Path(historyFolder).mkdir(parents=True, exist_ok=True)
        chat_history = os.path.join(historyFolder, "geminipro")
        chat_session = PromptSession(history=FileHistory(chat_history))

        promptStyle = Style.from_dict({
            # User input (default text).
            "": config.terminalCommandEntryColor2,
            # Prompt.
            "indicator": config.terminalPromptIndicatorColor2,
        })

        completer = WordCompleter(["[", "[NO_FUNCTION_CALL]"], ignore_case=True) if self.enableVision else None

        if not self.runnable:
            print(f"{self.name} is not running due to missing configurations!")
            return None
        model = GenerativeModel("gemini-pro")
        chat = model.start_chat(
            #context=f"You're {self.name}, a helpful AI assistant.",
        )
        HealthCheck.print2(f"\n{self.name} + Vision loaded!" if self.enableVision else f"\n{self.name} loaded!")
        print("(To start a new chart, enter '.new')")
        print(f"(To quit, enter '{config.exit_entry}')\n")
        while True:
            if not prompt:
                prompt = HealthCheck.simplePrompt(style=promptStyle, promptSession=chat_session, completer=completer,)
                if prompt and not prompt in (".new", config.exit_entry) and hasattr(config, "currentMessages"):
                    config.currentMessages.append({"content": prompt, "role": "user"})
            else:
                prompt = HealthCheck.simplePrompt(style=promptStyle, promptSession=chat_session, default=prompt, accept_default=True)
            if prompt == config.exit_entry:
                break
            elif prompt == ".new":
                clear()
                chat = model.start_chat()
                print("New chat started!")
            elif prompt := prompt.strip():
                config.pagerContent = ""
                self.addPagerContent = True

                # declare a function
                get_vision_func = generative_models.FunctionDeclaration(
                    name="analyze_images",
                    description="Describe or analyze images. Remember, do not use this function for non-image related tasks. Even it is an image-related task, use this function ONLY if I provide at least one image file path or image url.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Questions or requests that users ask about the given images",
                            },
                            "files": {
                                "type": "string",
                                "description": """Return a list of image paths or urls, e.g. '["image1.png", "/tmp/image2.png", "https://letmedoit.ai/image.png"]'. Return '[]' if image path is not provided.""",
                            },
                        },
                        "required": ["query", "files"],
                    },
                )
                vision_tool = generative_models.Tool(
                    function_declarations=[get_vision_func],
                )

                try:
                    # https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini
                    if "[NO_FUNCTION_CALL]" in prompt or not self.enableVision:
                        allow_function_call = False
                        prompt = prompt.replace("[NO_FUNCTION_CALL]", "")
                    else:
                        allow_function_call = True
                    completion = chat.send_message(
                        prompt,
                        # Optional:
                        generation_config=self.generation_config,
                        safety_settings=self.safety_settings,
                        tools=[vision_tool] if allow_function_call else None,
                        stream=True,
                    )

                    # Create a new thread for the streaming task
                    self.streaming_finished = False
                    streaming_event = threading.Event()
                    self.streaming_thread = threading.Thread(target=self.streamOutputs, args=(streaming_event, completion, prompt,))
                    # Start the streaming thread
                    self.streaming_thread.start()

                    # wait while text output is steaming; capture key combo 'ctrl+q' or 'ctrl+z' to stop the streaming
                    self.keyToStopStreaming(streaming_event)

                    # when streaming is done or when user press "ctrl+q"
                    self.streaming_thread.join()

                    # format response when streaming is not applied
                    #tokens = list(pygments.lex(fullContent, lexer=MarkdownLexer()))
                    #print_formatted_text(PygmentsTokens(tokens), style=HealthCheck.getPygmentsStyle())

                except:
                    self.streaming_finished = True
                    self.streaming_thread.join()
                    HealthCheck.print2(traceback.format_exc())

            prompt = ""

        HealthCheck.print2(f"\n{self.name} closed!")

    def analyze_images(self, function_args):
        def is_valid_url(url: str) -> bool:
            # Regular expression pattern for URL validation
            pattern = re.compile(
                r'^(http|https)://'  # http:// or https://
                r'([a-zA-Z0-9.-]+)'  # domain name
                r'(\.[a-zA-Z]{2,63})'  # dot and top-level domain (e.g. .com, .org)
                r'(:[0-9]{1,5})?'  # optional port number
                r'(/.*)?$'  # optional path
            )
            return bool(re.match(pattern, url))
        def is_valid_image_url(url: str) -> bool:
            try: 
                response = requests.head(url, timeout=30)
                content_type = response.headers['content-type'] 
                if 'image' in content_type: 
                    return True 
                else: 
                    return False 
            except requests.exceptions.RequestException: 
                return False
        def load_image_from_url(image_url: str) -> Image:
            with urllib.request.urlopen(image_url) as response:
                response = typing.cast(http.client.HTTPResponse, response)
                image_bytes = response.read()
            return Image.from_bytes(image_bytes)
        def is_valid_image_file(file_path: str) -> bool:
            try:
                # Open the image file
                with im.open(file_path) as img:
                    # Check if the file format is supported by PIL
                    img.verify()
                    return True
            except (IOError, SyntaxError) as e:
                # The file path is not a valid image file path
                return False
        def load_image_from_file(file_path: str) -> Image:
            with open(file_path, "rb") as file:
                image_bytes = file.read()
            return Image.from_bytes(image_bytes)

        query = function_args.get("query") # required
        files = function_args.get("files") # required
        if not files:
            self.defaultPrompt = f"{query}\n[NO_FUNCTION_CALL]"
            return None
        if isinstance(files, str):
            if not files.startswith("["):
                files = f'["{files}"]'
            files = eval(files)
        else:
            files = list(files)

        # check if some items are directory that contain images
        filesCopy = files[:]
        for item in filesCopy:
            if os.path.isdir(item):
                for root, _, allfiles in os.walk(item):
                    for file in allfiles:
                        file_path = os.path.join(root, file)
                        files.append(file_path)
                files.remove(item)

        content = []
        imageFiles = []
        # validate image paths
        for i in files:
            if is_valid_url(i) and is_valid_image_url(i):
                content.append(load_image_from_url(i))
                imageFiles.append(i)
            elif os.path.isfile(i) and is_valid_image_file(i):
                content.append(load_image_from_file(i))
                imageFiles.append(i)
        content.append(f"{query} Please give your answer in as much detail as possible.")

        if imageFiles:
            HealthCheck.print3(f"Reading: '{', '.join(imageFiles)}'")
            model = GenerativeModel("gemini-pro-vision")
            response = model.generate_content(
                content,
                generation_config=GenerationConfig(
                    temperature=self.temperature, # 0.0-1.0; default 0.9
                    max_output_tokens=2048,
                    candidate_count=1,
                ),
                safety_settings=self.safety_settings,
            )
            if response:
                chat_response = response.text.strip()
                if chat_response:
                    print(chat_response)
                    if hasattr(config, "currentMessages"):
                        config.currentMessages.append({"role": "assistant", "content": chat_response})
        else:
            self.defaultPrompt = f"{query}\n[NO_FUNCTION_CALL]"

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description="geminipro cli options")
    # Add arguments
    parser.add_argument("default", nargs="?", default=None, help="default entry")
    parser.add_argument('-o', '--outputtokens', action='store', dest='outputtokens', help="specify maximum output tokens with -o flag; default: 8192")
    parser.add_argument('-t', '--temperature', action='store', dest='temperature', help="specify temperature with -t flag: default: 0.9")
    # Parse arguments
    args = parser.parse_args()
    # Get options
    prompt = args.default.strip() if args.default and args.default.strip() else ""
    if args.outputtokens and args.outputtokens.strip():
        try:
            max_output_tokens = int(args.outputtokens.strip())
        except:
            max_output_tokens = 8192
    else:
        max_output_tokens = 8192
    if args.temperature and args.temperature.strip():
        try:
            temperature = float(args.temperature.strip())
        except:
            temperature = 0.9
    else:
        temperature = 0.9
    GeminiPro(
        temperature=temperature,
        max_output_tokens = max_output_tokens,
    ).run(
        prompt=prompt,
    )

if __name__ == '__main__':
    main()