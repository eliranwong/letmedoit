import vertexai, os, traceback, argparse
from vertexai.preview.generative_models import GenerativeModel, Content, Part
from vertexai.generative_models._generative_models import (
    GenerationConfig,
    HarmCategory,
    HarmBlockThreshold,
)
from letmedoit import config
from letmedoit.utils.streaming_word_wrapper import StreamingWordWrapper
from letmedoit.health_check import HealthCheck
if not hasattr(config, "currentMessages"):
    HealthCheck.setBasicConfig()
    config.saveConfig()
    #print("Configurations updated!")
from prompt_toolkit.styles import Style
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import clear
from pathlib import Path
import threading


# Install google-cloud-aiplatform FIRST!
#!pip install --upgrade google-cloud-aiplatform


class GeminiPro:

    def __init__(self, name="Gemini Pro", temperature=0.9, max_output_tokens=8192):
        # authentication
        if os.environ["GOOGLE_APPLICATION_CREDENTIALS"] and "Vertex AI" in config.enabledGoogleAPIs:
            self.runnable = True
        else:
            print("Vertex AI is disabled!")
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
        # Note: BLOCK_NONE is not allowed
        self.safety_settings={
            HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }
        """
        Alternately,
        from google.cloud.aiplatform_v1beta1.types.content import SafetySetting
        self.safety_settings = [
            SafetySetting(category=HarmCategory.HARM_CATEGORY_UNSPECIFIED, threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH)
            SafetySetting(category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH)
            SafetySetting(category=HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH)
            SafetySetting(category=HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH)
            SafetySetting(category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH)
        ]
        """
        self.defaultPrompt = ""
        #self.enableVision = (os.path.realpath(__file__).endswith("vision.py"))

    def run(self, prompt=""):
        if self.defaultPrompt:
            prompt, self.defaultPrompt = self.defaultPrompt, ""
        historyFolder = os.path.join(HealthCheck.getLocalStorage(), "history")
        Path(historyFolder).mkdir(parents=True, exist_ok=True)
        chat_history = os.path.join(historyFolder, "geminipro")
        chat_session = PromptSession(history=FileHistory(chat_history))

        promptStyle = Style.from_dict({
            # User input (default text).
            "": config.terminalCommandEntryColor2,
            # Prompt.
            "indicator": config.terminalPromptIndicatorColor2,
        })

        if not self.runnable:
            print(f"{self.name} is not running due to missing configurations!")
            return None
        model = GenerativeModel("gemini-pro")
        # on-going history
        if hasattr(config, "currentMessages") and config.currentMessages:
            history = []
            user = True
            for i in config.currentMessages:
                if i["role"] == "user" if user else "assistant":
                    history.append(Content(role="user" if user else "model", parts=[Part.from_text(i["content"])]))
                    user = not user
            # e.g. history=[
            #    Content(role="user", parts=[Part.from_text("Hello!")]),
            #    Content(role="model", parts=[Part.from_text("Hello! How can I assist you today?")]),
            #]
            if history and history[-1].role == "user":
                history = history[:-1]
            elif not history:
                history = None
        else:
            history = None
        chat = model.start_chat(history=history)
        justStarted = True
        #HealthCheck.print2(f"\n{self.name} + Vision loaded!" if self.enableVision else f"\n{self.name} loaded!")
        HealthCheck.print2(f"\n{self.name} loaded!")
        if hasattr(config, "currentMessages"):
            bottom_toolbar = f""" {str(config.hotkey_exit).replace("'", "")} {config.exit_entry}"""
        else:
            bottom_toolbar = f""" {str(config.hotkey_exit).replace("'", "")} {config.exit_entry} {str(config.hotkey_new).replace("'", "")} .new"""
            print("(To start a new chart, enter '.new')")
        print(f"(To exit, enter '{config.exit_entry}')\n")
        while True:
            if not prompt:
                prompt = HealthCheck.simplePrompt(style=promptStyle, promptSession=chat_session, bottom_toolbar=bottom_toolbar)
                if prompt and not prompt in (".new", config.exit_entry) and hasattr(config, "currentMessages"):
                    config.currentMessages.append({"content": prompt, "role": "user"})
            else:
                prompt = HealthCheck.simplePrompt(style=promptStyle, promptSession=chat_session, bottom_toolbar=bottom_toolbar, default=prompt, accept_default=True)
            if prompt == config.exit_entry:
                break
            elif prompt == ".new" and not hasattr(config, "currentMessages"):
                clear()
                chat = model.start_chat()
                justStarted = True
                print("New chat started!")
            elif prompt := prompt.strip():
                streamingWordWrapper = StreamingWordWrapper()
                config.pagerContent = ""
                #self.addPagerContent = True

                # declare a function
#                get_vision_func = generative_models.FunctionDeclaration(
#                    name="analyze_images",
#                    description="Describe or analyze images. Remember, do not use this function for non-image related tasks. Even it is an image-related task, use this function ONLY if I provide at least one image file path or image url.",
#                    parameters={
#                        "type": "object",
#                        "properties": {
#                            "query": {
#                                "type": "string",
#                                "description": "Questions or requests that users ask about the given images",
#                            },
#                            "files": {
#                                "type": "string",
#                                "description": """Return a list of image paths or urls, e.g. '["image1.png", "/tmp/image2.png", "https://letmedoit.ai/image.png"]'. Return '[]' if image path is not provided.""",
#                            },
#                        },
#                        "required": ["query", "files"],
#                    },
#                )
#                vision_tool = generative_models.Tool(
#                    function_declarations=[get_vision_func],
#                )

                try:
                    if not hasattr(config, "currentMessages") and config.systemMessage_geminipro and justStarted:
                        prompt = f"{config.systemMessage_geminipro}\n{prompt}"
                        justStarted = False
                    # https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini
                    # Note: At the time of writing, function call feature with Gemini Pro is very weak, compared with the function call feature offerred by ChatGPT:
                    # 1. Gemini Pro do not accept multiple tools in a single message
                    # 2. Gemini Pro is weak to determine if it is appropriate to use the given tool or not.  When a tool is given, it is called by mistake so often.  In contrast, ChatGPT has the "auto" setting which makes ChatGPT obviously smarter than Gemini Pro.
                    #if "[NO_FUNCTION_CALL]" in prompt or not self.enableVision:
                    #    allow_function_call = False
                    #    prompt = prompt.replace("[NO_FUNCTION_CALL]", "")
                    #else:
                    #    allow_function_call = True
                    completion = chat.send_message(
                        prompt,
                        # Optional:
                        generation_config=self.generation_config,
                        safety_settings=self.safety_settings,
                        #tools=[vision_tool] if allow_function_call else None,
                        stream=True,
                    )

                    # Create a new thread for the streaming task
                    streaming_event = threading.Event()
                    self.streaming_thread = threading.Thread(target=streamingWordWrapper.streamOutputs, args=(streaming_event, completion,))
                    # Start the streaming thread
                    self.streaming_thread.start()

                    # wait while text output is steaming; capture key combo 'ctrl+q' or 'ctrl+z' to stop the streaming
                    streamingWordWrapper.keyToStopStreaming(streaming_event)

                    # when streaming is done or when user press "ctrl+q"
                    self.streaming_thread.join()

                    # format response when streaming is not applied
                    #tokens = list(pygments.lex(fullContent, lexer=MarkdownLexer()))
                    #print_formatted_text(PygmentsTokens(tokens), style=HealthCheck.getPygmentsStyle())

                except:
                    self.streaming_thread.join()
                    HealthCheck.print2(traceback.format_exc())

            prompt = ""

        HealthCheck.print2(f"\n{self.name} closed!")
        if hasattr(config, "currentMessages"):
            HealthCheck.print2(f"Return back to {config.letMeDoItName} prompt ...")

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