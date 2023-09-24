import config

from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from utils.prompt_shared_key_bindings import prompt_shared_key_bindings
from utils.prompt_multiline_shared_key_bindings import prompt_multiline_shared_key_bindings
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
        self.shareKeyBindings()
        config.terminalColors = {
            "ansidefault": "ansidefault",
            "ansiblack": "ansiwhite",
            "ansired": "ansibrightred",
            "ansigreen": "ansibrightgreen",
            "ansiyellow": "ansibrightyellow",
            "ansiblue": "ansibrightblue",
            "ansimagenta": "ansibrightmagenta",
            "ansicyan": "ansibrightcyan",
            "ansigray": "ansibrightblack",
            "ansiwhite": "ansiblack",
            "ansibrightred": "ansired",
            "ansibrightgreen": "ansigreen",
            "ansibrightyellow": "ansiyellow",
            "ansibrightblue": "ansiblue",
            "ansibrightmagenta": "ansimagenta",
            "ansibrightcyan": "ansicyan",
            "ansibrightblack": "ansigray",
        }

    def getToolBar(self, multiline=False):
        if multiline:
            return f" [ctrl+q] {config.terminal_cancel_action}; [blank] actions; [escape+enter] send "
        return f" [ctrl+q] {config.terminal_cancel_action}; [blank] actions; [enter] send "

    def shareKeyBindings(self):
        this_key_bindings = KeyBindings()
        @this_key_bindings.add("c-q")
        def _(event):
            event.app.current_buffer.text = config.terminal_cancel_action
            event.app.current_buffer.validate_and_handle()
        @this_key_bindings.add("c-n")
        def _(event):
            event.app.current_buffer.text = ".new"
            event.app.current_buffer.validate_and_handle()
        @this_key_bindings.add("c-s")
        def _(event):
            event.app.current_buffer.text = ".save"
            event.app.current_buffer.validate_and_handle()
        @this_key_bindings.add("c-l")
        def _(event):
            config.defaultEntry = event.app.current_buffer.text
            event.app.current_buffer.text = ".swapmultiline"
            event.app.current_buffer.validate_and_handle()
        @this_key_bindings.add("c-o")
        def _(event):
            event.app.current_buffer.text = ".context"
            event.app.current_buffer.validate_and_handle()

        self.prompt_shared_key_bindings = merge_key_bindings([
            prompt_shared_key_bindings,
            this_key_bindings,
        ])
        self.prompt_multiline_shared_key_bindings = merge_key_bindings([
            prompt_shared_key_bindings,
            prompt_multiline_shared_key_bindings,
            this_key_bindings,
        ])

    def simplePrompt(self, numberOnly=False, validator=None, multiline=False, inputIndicator="", default="", accept_default=False, completer=None, promptSession=None):
        inputPrompt = promptSession.prompt if promptSession is not None else prompt
        if not inputIndicator:
            inputIndicator = self.inputIndicator
        if numberOnly:
            validator = NumberValidator()
        userInput = inputPrompt(
            inputIndicator,
            key_bindings=self.prompt_multiline_shared_key_bindings if multiline else self.prompt_shared_key_bindings,
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