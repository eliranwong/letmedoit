import config, autogen, readline

if not hasattr(config, "max_consecutive_auto_reply"):
    config.max_consecutive_auto_reply = 10

config_list = autogen.get_config_list(
    [config.openaiApiKey], # assume openaiApiKey is in place in config.py
    api_type="openai",
    api_version=None,
)

#print(config_list)

def getResponse(message):
    assistant = autogen.AssistantAgent(
        name="assistant",
        llm_config={
            #"cache_seed": 42,  # seed for caching and reproducibility
            "config_list": config_list,  # a list of OpenAI API configurations
            "temperature": config.chatGPTApiTemperature,  # temperature for sampling
        },  # configuration for autogen's enhanced inference API which is compatible with OpenAI API
    )
    # create a UserProxyAgent instance named "user_proxy"
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=config.max_consecutive_auto_reply,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={
            "work_dir": "coding",
            "use_docker": False,  # set to True or image name like "python:3" to use docker
        },
    )
    # the assistant receives a message from the user_proxy, which contains the task description
    user_proxy.initiate_chat(
        assistant,
        message=message,
    )

def getInput():
    message = input(">>> ")
    getResponse(message)

print("Autogen mini launched!")
print("[press 'ctrl+c' to exit]")
while True:
    getInput()