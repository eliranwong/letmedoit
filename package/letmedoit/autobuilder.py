import os
thisFile = os.path.realpath(__file__)
packageFolder = os.path.dirname(thisFile)
package = os.path.basename(packageFolder)
if os.getcwd() != packageFolder:
    os.chdir(packageFolder)
configFile = os.path.join(packageFolder, "config.py")
if not os.path.isfile(configFile):
    open(configFile, "a", encoding="utf-8").close()
from letmedoit import config

from letmedoit.health_check import HealthCheck
if not hasattr(config, "openaiApiKey") or not config.openaiApiKey:
    HealthCheck.setBasicConfig()
    HealthCheck.changeAPIkey()
    HealthCheck.saveConfig()
    print("Updated!")
HealthCheck.checkCompletion()

#from autogen.agentchat.contrib.agent_builder import AgentBuilder
from letmedoit.utils.agent_builder import AgentBuilder
import autogen, os, json, traceback, re, datetime
from pathlib import Path
from urllib.parse import quote
from letmedoit.utils.prompts import Prompts
from letmedoit.utils.shared_utils import SharedUtil
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.styles import Style
#from prompt_toolkit import PromptSession
#from prompt_toolkit.history import FileHistory

# Reference: https://microsoft.github.io/autogen/docs/reference/agentchat/contrib/agent_builder
class AutoGenBuilder:

    def __init__(self):
        #config_list = autogen.get_config_list(
        #    [config.openaiApiKey], # assume openaiApiKey is in place in config.py
        #    api_type="openai",
        #    api_version=None,
        #)
        oai_config_list = []
        for model in ("gpt-4-1106-preview", "gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"):
            oai_config_list.append({"model": model, "api_key": config.openaiApiKey})
        os.environ["OAI_CONFIG_LIST"] = json.dumps(oai_config_list)
        self.chatGPTmodel = "gpt-4-1106-preview"

    def getSavePath(self, title=""):
        package = os.path.basename(packageFolder)
        preferredDir = os.path.join(os.path.expanduser('~'), package)
        if os.path.isdir(preferredDir):
            folder = preferredDir
        elif config.startupdirectory:
            folder = config.startupdirectory
        else:
            folder = os.path.join(packageFolder, "files")
        folder = os.path.join(folder, "autogen", "builder")
        Path(folder).mkdir(parents=True, exist_ok=True)
        if title:
            title = "_" + quote(title, safe="")
        currentTime = re.sub("[\. :]", "_", str(datetime.datetime.now()))
        return os.path.join(folder, f"{currentTime}{title}.json")

    def getResponse(self, task, title=""):

        config_list = autogen.config_list_from_json(
            env_or_file="OAI_CONFIG_LIST",  # or OAI_CONFIG_LIST.json if file extension is added
            filter_dict={
                "model": {
                    self.chatGPTmodel,
                }
            }
        )
        llm_config={
            #"cache_seed": 42,  # seed for caching and reproducibility
            "config_list": config_list,  # a list of OpenAI API configurations
            "temperature": config.chatGPTApiTemperature,  # temperature for sampling
            "timeout": 300,
        }  # configuration for autogen's enhanced inference API which is compatible with OpenAI API

        builder = AgentBuilder(
            #config_path=config_path,
            builder_model=self.chatGPTmodel,
            agent_model=self.chatGPTmodel,
        )

        #building_task = "Find a paper on arxiv by programming, and analysis its application in some domain. For example, find a latest paper about gpt-4 on arxiv and find its potential applications in software."
        #execution_task="Find a recent paper about gpt-4 on arxiv and find its potential applications in software."
        #agent_list, agent_configs = builder.build(building_task, llm_config, coding=True)
        
        building_task = execution_task = task
        agent_list, _ = builder.build(building_task, llm_config, coding=True)

        group_chat = autogen.GroupChat(agents=agent_list, messages=[], max_round=config.max_group_chat_round)
        manager = autogen.GroupChatManager(
            groupchat=group_chat,
            llm_config={"config_list": config_list, **llm_config},
        )
        agent_list[0].initiate_chat(manager, message=execution_task)

        # save building config
        builder.save(self.getSavePath(title))
        #clear all agents
        builder.clear_all_agents(recycle_endpoint=True)

    def run(self):
        promptStyle = Style.from_dict({
            # User input (default text).
            "": config.terminalCommandEntryColor2,
            # Prompt.
            "indicator": config.terminalPromptIndicatorColor2,
        })
        prompts = Prompts()

        self.print("Enter maximum consecutive auto-reply below:")
        max_group_chat_round = prompts.simplePrompt(numberOnly=True, style=promptStyle, default=str(config.max_group_chat_round),)
        if max_group_chat_round and int(max_group_chat_round) > 1:
            config.max_group_chat_round = int(max_group_chat_round)

        self.print(f"<{config.terminalCommandEntryColor1}>AutoGen Agent Builder launched!</{config.terminalCommandEntryColor1}>")
        self.print("[press 'ctrl+q' to exit]")
        while True:
            self.print(f"<{config.terminalCommandEntryColor1}>Hi! I am ready for a new task.</{config.terminalCommandEntryColor1}>")
            self.print(f"<{config.terminalCommandEntryColor1}>Please specify a task below:</{config.terminalCommandEntryColor1}>")
            task = prompts.simplePrompt(style=promptStyle)
            if task == config.exit_entry:
                break
            try:
                self.getResponse(task)
            except:
                self.print(traceback.format_exc())
                break
        self.print(f"<{config.terminalCommandEntryColor1}>\n\nAutoGen Agent Builder closed!</{config.terminalCommandEntryColor1}>")


    def print(self, message):
        #print(message)
        print_formatted_text(HTML(message))

def main():
    AutoGenBuilder().run()

if __name__ == '__main__':
    main()