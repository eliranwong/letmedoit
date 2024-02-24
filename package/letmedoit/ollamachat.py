import ollama, os, traceback, argparse, threading, shutil
from letmedoit import config
from letmedoit.utils.ollama_models import ollama_models
from letmedoit.utils.streaming_word_wrapper import StreamingWordWrapper
from letmedoit.health_check import HealthCheck
if not hasattr(config, "currentMessages"):
    HealthCheck.setBasicConfig()
    HealthCheck.saveConfig()
    #print("Configurations updated!")
from prompt_toolkit.styles import Style
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import clear
from prompt_toolkit.completion import WordCompleter, FuzzyCompleter
from pathlib import Path

promptStyle = Style.from_dict({
    # User input (default text).
    "": config.terminalCommandEntryColor2,
    # Prompt.
    "indicator": config.terminalPromptIndicatorColor2,
})

class OllamaChat:

    def __init__(self):
        # authentication
        if shutil.which("ollama"):
            self.runnable = True
        else:
            print("Local LLM Server 'Ollama' not found! Install Ollama first!")
            print("Read https://ollama.com/.")
            self.runnable = False

    def run(self, prompt="", model="mistral"):
        if not self.runnable:
            return None

        # check model
        if not f"'model': '{model}'" in str(ollama.list()).replace(":latest", ""):
            # download model
            os.system(f"ollama pull {model}")

        historyFolder = os.path.join(HealthCheck.getFiles(), "history")
        Path(historyFolder).mkdir(parents=True, exist_ok=True)
        chat_history = os.path.join(historyFolder, f"ollama_{model}")
        chat_session = PromptSession(history=FileHistory(chat_history))

        HealthCheck.print2(f"\n{model.capitalize()} loaded!")

        # history
        messages = config.currentMessages[:-1] if hasattr(config, "currentMessages") else []
        
        # bottom toolbar
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
                messages = []
                print("New chat started!")
            elif prompt := prompt.strip():
                streamingWordWrapper = StreamingWordWrapper()
                config.pagerContent = ""
                messages.append({'role': 'user', 'content': prompt})
                try:
                    completion = ollama.chat(
                        model=model,
                        messages=messages,
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

                    # update messages
                    messages.append({"role": "assistant", "content": config.new_chat_response})
                except:
                    if hasattr(self, "streaming_thread"):
                        self.streaming_thread.join()
                    HealthCheck.print2(traceback.format_exc())

            prompt = ""

        HealthCheck.print2(f"\n{model.capitalize()} closed!")
        if hasattr(config, "currentMessages"):
            HealthCheck.print2(f"Return back to {config.letMeDoItName} prompt ...")

# available cli: 'ollamachat', 'mistral', 'llama2', 'llama213b', 'llama270b', 'gemma2b', 'gemma7b', 'llava', 'phi', 'vicuna'

def mistral():
    main("mistral")

def llama2():
    main("llama2")

def llama213b():
    main("llama2:13b")

def llama270b():
    main("llama2:70b")

def codellama():
    main("codellama")

def gemma2b():
    main("gemma:2b")

def gemma7b():
    main("gemma:7b")

def llava():
    main("llava")

def phi():
    main("phi")

def vicuna():
    main("vicuna")

def main(thisModel=""):
    # Create the parser
    parser = argparse.ArgumentParser(description="palm2 cli options")
    # Add arguments
    parser.add_argument("default", nargs="?", default=None, help="default entry")
    if not thisModel:
        parser.add_argument('-m', '--model', action='store', dest='model', help="specify language model with -m flag; default: mistral")
    # Parse arguments
    args = parser.parse_args()
    # Get options
    prompt = args.default.strip() if args.default and args.default.strip() else ""
    if thisModel:
        model = thisModel
    else:
        if args.model and args.model.strip():
            model = args.model.strip()
        else:
            historyFolder = os.path.join(HealthCheck.getFiles(), "history")
            Path(historyFolder).mkdir(parents=True, exist_ok=True)
            model_history = os.path.join(historyFolder, "ollama_default")
            model_session = PromptSession(history=FileHistory(model_history))
            completer = FuzzyCompleter(WordCompleter(ollama_models, ignore_case=True))
            bottom_toolbar = f""" {str(config.hotkey_exit).replace("'", "")} {config.exit_entry}"""

            HealthCheck.print2("Ollama chat launched!")
            print("Select a model below:")
            print("Note: You should have at least 8 GB of RAM available to run the 7B models, 16 GB to run the 13B models, and 32 GB to run the 33B models.")
            option = HealthCheck.simplePrompt(style=promptStyle, promptSession=model_session, bottom_toolbar=bottom_toolbar, default=config.ollamaDefaultModel, completer=completer)
            if option and option in ollama_models:
                model = config.ollamaDefaultModel = option
            else:
                model = config.ollamaDefaultModel

    # Run chat bot
    OllamaChat().run(
        prompt=prompt,
        model=model,
    )

if __name__ == '__main__':
    main()