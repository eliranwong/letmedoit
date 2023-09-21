import config

from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from prompt_toolkit.filters import Condition
from utils.promptValidator import NumberValidator

class Prompts:

    def __init__(self):
        self.promptStyle = Style.from_dict({
            # User input (default text).
            "": config.terminalCommandEntryColor2,
            # Prompt.
            "indicator": config.terminalPromptIndicatorColor2,
        })
        self.inputIndicator = [
            ("class:indicator", ">>> "),
        ]

    def getToolBar(self, multiline=False):
        if multiline:
            return f" [ctrl+q] {config.terminal_cancel_action}; [escape+enter] enter "
        return f" [ctrl+q] {config.terminal_cancel_action}; [enter] enter"

    def simplePrompt(self, numberOnly=False, validator=None, multiline=False, inputIndicator="", default="", accept_default=False, completer=None, promptSession=None):
        inputPrompt = promptSession.prompt if promptSession is not None else prompt
        if not inputIndicator:
            inputIndicator = self.inputIndicator
        if numberOnly:
            validator = NumberValidator()
        userInput = inputPrompt(
            inputIndicator,
            #key_bindings=self.prompt_multiline_shared_key_bindings if multiline else self.prompt_shared_key_bindings,
            bottom_toolbar=self.getToolBar(multiline),
            enable_system_prompt=True,
            swap_light_and_dark_colors=Condition(lambda: not config.terminalResourceLinkColor.startswith("ansibright")),
            style=self.promptStyle,
            validator=validator,
            multiline=multiline,
            default=default,
            accept_default=accept_default,
            completer=completer,
        ).strip()
        return userInput