from myhand import config
import autogen, os, json, traceback
from pathlib import Path
from myhand.utils.prompts import Prompts
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.styles import Style
from autogen import config_list_from_json
from autogen.agentchat.contrib.math_user_proxy_agent import MathUserProxyAgent


class AutoGenMath:

    def __init__(self):
        #config_list = autogen.get_config_list(
        #    [config.openaiApiKey], # assume openaiApiKey is in place in config.py
        #    api_type="openai",
        #    api_version=None,
        #)
        oai_config_list = []
        for model in ("gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"):
            oai_config_list.append({"model": model, "api_key": config.openaiApiKey})
        os.environ["OAI_CONFIG_LIST"] = json.dumps(oai_config_list)

    def getResponse(self, math_problem):
        this_file = os.path.realpath(__file__)
        currentFolder = os.path.dirname(this_file)
        folder = config.startupdirectory if config.startupdirectory else os.path.join(currentFolder, "files")
        db = os.path.join(folder, "autogen", "teachable")
        Path(db).mkdir(parents=True, exist_ok=True)

        config_list = autogen.config_list_from_json(
            env_or_file="OAI_CONFIG_LIST",  # or OAI_CONFIG_LIST.json if file extension is added
            filter_dict={
                "model": {
                    config.chatGPTApiModel,
                }
            }
        )

        # reference https://microsoft.github.io/autogen/docs/reference/agentchat/contrib/math_user_proxy_agent
        # 1. create an AssistantAgent instance named "assistant"
        assistant = autogen.AssistantAgent(
            name="assistant", 
            system_message="You are a helpful assistant.",
            llm_config={
                #"cache_seed": 42,  # seed for caching and reproducibility
                "config_list": config_list,  # a list of OpenAI API configurations
                "temperature": config.chatGPTApiTemperature,  # temperature for sampling
                "timeout": 600,
            },  # configuration for autogen's enhanced inference API which is compatible with OpenAI API
        )

        # 2. create the MathUserProxyAgent instance named "mathproxyagent"
        # By default, the human_input_mode is "NEVER", which means the agent will not ask for human input.
        mathproxyagent = MathUserProxyAgent(
            name="mathproxyagent",
            human_input_mode="NEVER",
            code_execution_config={"use_docker": False},
        )

        mathproxyagent.initiate_chat(assistant, problem=math_problem)

    def print(self, message):
        #print(message)
        print_formatted_text(HTML(message))

    def run(self):
        promptStyle = Style.from_dict({
            # User input (default text).
            "": config.terminalCommandEntryColor2,
            # Prompt.
            "indicator": config.terminalPromptIndicatorColor2,
        })
        prompts = Prompts()
        self.print(f"<{config.terminalCommandEntryColor1}>AutoGen Math launched!</{config.terminalCommandEntryColor1}>")
        self.print("[press 'ctrl+q' to exit]")
        while True:
            self.print(f"<{config.terminalCommandEntryColor1}>New session started!</{config.terminalCommandEntryColor1}>")
            self.print(f"<{config.terminalCommandEntryColor1}>Enter a math problem below:</{config.terminalCommandEntryColor1}>")
            math_problem = prompts.simplePrompt(style=promptStyle)
            if math_problem == config.exit_entry:
                break
            try:
                self.getResponse(math_problem)
            except:
                self.print(traceback.format_exc())
                break
        self.print(f"<{config.terminalCommandEntryColor1}>\n\nAutoGen Math closed!</{config.terminalCommandEntryColor1}>")


if __name__ == '__main__':
    AutoGenMath().run()