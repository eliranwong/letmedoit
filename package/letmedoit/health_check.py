from openai import OpenAI
from prompt_toolkit import prompt
import os, openai, traceback, json, pprint
from chromadb.utils import embedding_functions
from prompt_toolkit import print_formatted_text, HTML

thisFile = os.path.realpath(__file__)
packageFolder = os.path.dirname(thisFile)
package = os.path.basename(packageFolder)
if os.getcwd() != packageFolder:
    os.chdir(packageFolder)
configFile = os.path.join(packageFolder, "config.py")
if not os.path.isfile(configFile):
    open(configFile, "a", encoding="utf-8").close()
from letmedoit import config

class HealthCheck:

    models = ("gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4-1106-preview", "gpt-4", "gpt-4-32k")

    @staticmethod
    def setBasicConfig(): # minimum config to work with standalone scripts built with AutoGen
        config.openaiApiKey = ''
        config.chatGPTApiModel = 'gpt-3.5-turbo'
        config.chatGPTApiTemperature = 0.8
        config.max_consecutive_auto_reply = 10
        config.exit_entry = '.exit'
        config.cancel_entry = '.cancel'
        config.terminalPromptIndicatorColor1 = "ansimagenta"
        config.terminalPromptIndicatorColor2 = "ansicyan"
        config.terminalCommandEntryColor1 = "ansiyellow"
        config.terminalCommandEntryColor2 = "ansigreen"
        config.terminalResourceLinkColor = "ansiyellow"
        config.terminalHeadingTextColor = "ansigreen"
        config.mouseSupport = False
        config.embeddingModel = "text-embedding-ada-002"
        config.max_agents = 5
        config.max_group_chat_round = 12
        config.max_consecutive_auto_reply = 10
        config.includeIpInSystemMessage = False
        HealthCheck.setPrint()
    
    @staticmethod
    def setPrint():
        if not hasattr(config, "print2"):
            config.print2 = HealthCheck.print2
        if not hasattr(config, "print3"):
            config.print3 = HealthCheck.print3

    @staticmethod
    def print2(content):
        print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>{content}</{config.terminalPromptIndicatorColor2}>"))

    @staticmethod
    def print3(content):
        splittedContent = content.split(": ", 1)
        if len(splittedContent) == 2:
            key, value = splittedContent
            print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>{key}:</{config.terminalPromptIndicatorColor2}> {value}"))
        else:
            self.print2(splittedContent)

    @staticmethod
    def getEmbeddingFunction():
        if config.embeddingModel == "text-embedding-ada-002":
            return embedding_functions.OpenAIEmbeddingFunction(api_key=config.openaiApiKey, model_name="text-embedding-ada-002")
        return embedding_functions.SentenceTransformerEmbeddingFunction(model_name=config.embeddingModel) # support custom Sentence Transformer Embedding models by modifying config.embeddingModel

    @staticmethod
    def changeAPIkey():
        print("Enter your OpenAI API Key [required]:")
        apikey = prompt(default=config.openaiApiKey, is_password=True)
        if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
            config.openaiApiKey = apikey
        #HealthCheck.checkCompletion()

    @staticmethod
    def checkCompletion():
        # instantiate a client that can shared with plugins
        os.environ["OPENAI_API_KEY"] = config.openaiApiKey
        client = OpenAI()
        try:
            client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content" : "hello"}],
                n=1,
                max_tokens=10,
            )
            # set variable 'OAI_CONFIG_LIST' to work with pyautogen
            oai_config_list = []
            for model in HealthCheck.models:
                oai_config_list.append({"model": model, "api_key": config.openaiApiKey})
            os.environ["OAI_CONFIG_LIST"] = json.dumps(oai_config_list)
        except openai.APIError as e:
            print("Error: Issue on OpenAI side.")
            print("Solution: Retry your request after a brief wait and contact us if the issue persists.")
        #except openai.Timeout as e:
        #    print("Error: Request timed out.")
        #    print("Solution: Retry your request after a brief wait and contact us if the issue persists.")
        except openai.RateLimitError as e:
            print("Error: You have hit your assigned rate limit.")
            print("Solution: Pace your requests. Read more in OpenAI [Rate limit guide](https://platform.openai.com/docs/guides/rate-limits).")
        except openai.APIConnectionError as e:
            print("Error: Issue connecting to our services.")
            print("Solution: Check your network settings, proxy configuration, SSL certificates, or firewall rules.")
        #except openai.InvalidRequestError as e:
        #    print("Error: Your request was malformed or missing some required parameters, such as a token or an input.")
        #    print("Solution: The error message should advise you on the specific error made. Check the [documentation](https://platform.openai.com/docs/api-reference/) for the specific API method you are calling and make sure you are sending valid and complete parameters. You may also need to check the encoding, format, or size of your request data.")
        except openai.AuthenticationError as e:
            print("Error: Your API key or token was invalid, expired, or revoked.")
            print("Solution: Check your API key or token and make sure it is correct and active. You may need to generate a new one from your account dashboard.")
            HealthCheck.changeAPIkey()
        #except openai.ServiceUnavailableError as e:
        #    print("Error: Issue on OpenAI servers. ")
        #    print("Solution: Retry your request after a brief wait and contact us if the issue persists. Check the [status page](https://status.openai.com).")
        except:
            print(traceback.format_exc())

    @staticmethod
    def saveConfig():
        #print(configFile)
        with open(configFile, "w", encoding="utf-8") as fileObj:
            #print(dir(config))
            for name in dir(config):
                excludeConfigList = []
                if not name.startswith("__") and not name in excludeConfigList:
                    try:
                        value = eval(f"config.{name}")
                        fileObj.write("{0} = {1}\n".format(name, pprint.pformat(value)))
                    except:
                        pass