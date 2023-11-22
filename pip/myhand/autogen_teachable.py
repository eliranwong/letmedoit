from myhand import config
import autogen, os, json
from pathlib import Path
from myhand.utils.terminal_mode_dialogs import TerminalModeDialogs
from prompt_toolkit import print_formatted_text, HTML
from autogen import UserProxyAgent, config_list_from_json
from autogen.agentchat.contrib.teachable_agent import TeachableAgent


class AutoGenTeachable:

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

    def getResponse(self, verbosity):
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

        # reference https://microsoft.github.io/autogen/docs/reference/agentchat/contrib/teachable_agent
        teachable_agent = TeachableAgent(
            name="teachableagent",
            llm_config={
                #"cache_seed": 42,  # seed for caching and reproducibility
                "config_list": config_list,  # a list of OpenAI API configurations
                "temperature": config.chatGPTApiTemperature,  # temperature for sampling
                "timeout": 300,
            },  # configuration for autogen's enhanced inference API which is compatible with OpenAI API
            teach_config={
                "reset_db": False,  # Use True to force-reset the memo DB, and False to use an existing DB.
                "path_to_db_dir": db,  # Can be any path.
                "verbosity": verbosity,
            }
        )

        user = UserProxyAgent("user", human_input_mode="ALWAYS")

        # This function will return once the user types 'exit'.
        teachable_agent.initiate_chat(user, message="Hi, I'm a teachable user assistant! What's on your mind?")

        teachable_agent.learn_from_user_feedback()
        teachable_agent.close_db()

    def print(self, message):
        #print(message)
        print_formatted_text(HTML(message))

    def run(self):
        options = {"(default) for basic info": 0, "to add memory operations": 1, "for analyzer messages": 2, "for memo lists": 3}
        verbosity = TerminalModeDialogs(self).getValidOptions(
            options=options.keys(),
            title="Launching AutoGen Teachable ...",
            default="(default) for basic info",
            text="Choose verbosity below:"
        )
        if not verbosity:
            verbosity = "(default) for basic info"
        self.getResponse(options[verbosity])
        
        self.print(f"\n\n<{config.terminalCommandEntryColor1}>AutoGen Teachable closed!</{config.terminalCommandEntryColor1}>")

if __name__ == '__main__':
    AutoGenTeachable().run()