"""
LetMeDoIt AI Plugin - build agents

build a group of agents to execute a task with "AutoGen Agent Builder"

[FUNCTION_CALL]
"""


from letmedoit import config
import os
from letmedoit.autobuilder import AutoGenBuilder

def build_agents(function_args):
    task = function_args.get("task") # required
    title = function_args.get("title") # required
    config.print2("AutoGen Agent Builder launched!")
    config.print3(f"Title: {title}")
    config.print3(f"Description: {task}")
    messages = AutoGenBuilder().getResponse(task, title)
    if not messages[-1]["content"]:
        del messages[-1]
    # add context to the message chain
    config.currentMessages += messages
    config.print2("\nAutoGen Agent Builder closed!")
    return ""

functionSignature = {
    "name": "build_agents",
    "description": "build a group of AI assistants or agents to execute a complicated task that other functions cannot resolve",
    "parameters": {
        "type": "object",
        "properties": {
            "task": {
                "type": "string",
                "description": "Task description in as much detail as possible",
            },
            "title": {
                "type": "string",
                "description": "A short title to describe the task",
            },
        },
        "required": ["task", "title"],
    },
}

config.pluginsWithFunctionCall.append("build_agents")
config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["build_agents"] = build_agents