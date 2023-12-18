import vertexai, os, traceback
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
from pathlib import Path
import asyncio, threading, shutil, textwrap


# Install google-cloud-aiplatform FIRST!
#!pip install --upgrade google-cloud-aiplatform

# Keep for reference; unnecessary for api key authentication with json file
# (developer): Update and un-comment below lines
#project_id = "letmedoitai"
#location = "us-central1"
#vertexai.init(project=project_id, location=location)


class GeminiPro:

    def __init__(self):
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

    def streamOutputs(self, streaming_event, completion):
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
                answer = event.text
                #answer = event.choices[0].delta.content
                #answer = SharedUtil.transformText(answer)
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
                    #self.readAnswer(answer)
            else:
                finishOutputs(wrapWords, chat_response)
                return None
        
        finishOutputs(wrapWords, chat_response)

    def run(self, prompt=""):
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

        if not self.runnable:
            print("Gemini Pro is not running due to missing configurations!")
            return None
        model = GenerativeModel("gemini-pro")
        chat = model.start_chat()
        HealthCheck.print2("\nGemini Pro loaded!")
        print("(To start a new chart, enter '.new')")
        print(f"(To quit, enter '{config.exit_entry}')\n")
        import re, time
        while True:
            #print("------------------------------\n")
            #print("Enter your prompt below:")
            if not prompt:
                #prompt = input(">>> ")
                prompt = HealthCheck.simplePrompt(style=promptStyle, promptSession=chat_session)
                if prompt and not prompt in (".new", config.exit_entry) and hasattr(config, "currentMessages"):
                    config.currentMessages.append({"content": prompt, "role": "user"})
            else:
                #print(f">>> {prompt}")
                prompt = HealthCheck.simplePrompt(style=promptStyle, promptSession=chat_session, default=prompt, accept_default=True)
            #print("")
            if prompt == config.exit_entry:
                break
            elif prompt == ".new":
                chat = model.start_chat()
                print("New chat started!")
            elif prompt := prompt.strip():
                config.pagerContent = ""
                self.addPagerContent = True

                try:
                    # https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini
                    completion = chat.send_message(
                        prompt,
                        # Optional:
                        generation_config=GenerationConfig(
                            temperature=0.9, # 0.0-1.0; default 0.9
                            max_output_tokens=8192, # default
                            candidate_count=1,
                        ),
                        safety_settings={
                            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                        },
                        stream=True,
                    )

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

                    # format response when streaming is not applied
                    #tokens = list(pygments.lex(fullContent, lexer=MarkdownLexer()))
                    #print_formatted_text(PygmentsTokens(tokens), style=HealthCheck.getPygmentsStyle())

                except:
                    self.streaming_finished = True
                    self.streaming_thread.join()
                    HealthCheck.print2(traceback.format_exc())

            prompt = ""
            #print("")
        #print("------------------------------")
        HealthCheck.print2("\nGemini Pro closed!\n")

def main():
    GeminiPro().run()

if __name__ == '__main__':
    main()