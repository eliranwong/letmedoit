import config

from prompt_toolkit import prompt
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.styles import Style
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from utils.prompt_shared_key_bindings import prompt_shared_key_bindings
from utils.prompt_multiline_shared_key_bindings import prompt_multiline_shared_key_bindings
from utils.promptValidator import NumberValidator

class Prompts:

    def __init__(self):
        self.promptStyle1 = Style.from_dict({
            # User input (default text).
            "": config.terminalCommandEntryColor1,
            # Prompt.
            "indicator": config.terminalPromptIndicatorColor1,
        })
        self.promptStyle2 = Style.from_dict({
            # User input (default text).
            "": config.terminalCommandEntryColor2,
            # Prompt.
            "indicator": config.terminalPromptIndicatorColor2,
        })
        self.inputIndicator = [
            ("class:indicator", ">>> "),
        ]
        self.shareKeyBindings()
        config.showKeyBindings = self.showKeyBindings
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
            return f" [ctrl+q] {config.exit_entry}; [blank] actions; [escape+enter] send "
        return f" [ctrl+q] {config.exit_entry}; [blank] actions; [enter] send "

    def shareKeyBindings(self):
        this_key_bindings = KeyBindings()
        @this_key_bindings.add("c-q")
        def _(event):
            event.app.current_buffer.text = config.exit_entry
            event.app.current_buffer.validate_and_handle()
        @this_key_bindings.add("c-n")
        def _(event):
            event.app.current_buffer.text = ".new"
            event.app.current_buffer.validate_and_handle()
        @this_key_bindings.add("c-y")
        def _(event):
            config.chatGPTApiPredefinedContextTemp = config.chatGPTApiPredefinedContext
            config.chatGPTApiPredefinedContext = "[none]"
            event.app.current_buffer.text = ".new"
            event.app.current_buffer.validate_and_handle()
            run_in_terminal(lambda: print("Predefined context is now temporarily changed to '[none]'."))
        @this_key_bindings.add("c-s")
        def _(event):
            event.app.current_buffer.text = ".save"
            event.app.current_buffer.validate_and_handle()
        @this_key_bindings.add("c-c")
        def _(event):
            event.app.current_buffer.text = config.cancel_entry
            event.app.current_buffer.validate_and_handle()
        @this_key_bindings.add("c-d")
        def _(_):
            config.developer = not config.developer
            run_in_terminal(lambda: print(f"Developer mode {'enabled' if config.developer else 'disabled'}!"))
        @this_key_bindings.add("c-e")
        def _(_):
            config.enhanceCommandExecution = not config.enhanceCommandExecution
            run_in_terminal(lambda: print(f"Command execution mode changed to '{'enhanced' if config.enhanceCommandExecution else 'auto'}'!"))
        @this_key_bindings.add("c-l")
        def _(event):
            config.defaultEntry = event.app.current_buffer.text
            event.app.current_buffer.text = ".swapmultiline"
            event.app.current_buffer.validate_and_handle()
        @this_key_bindings.add("c-o")
        def _(event):
            event.app.current_buffer.text = ".context"
            event.app.current_buffer.validate_and_handle()
        @this_key_bindings.add("escape", "t")
        def _(event):
            event.app.current_buffer.text = ".system"
            event.app.current_buffer.validate_and_handle()
        @this_key_bindings.add("c-k")
        def _(_):
            run_in_terminal(self.showKeyBindings)
        @this_key_bindings.add("c-g")
        def _(_):
            config.displayImprovedWriting = not config.displayImprovedWriting
            run_in_terminal(lambda: print(f"Improved Writing Display '{'enabled' if config.displayImprovedWriting else 'disabled'}'!"))

        self.prompt_shared_key_bindings = merge_key_bindings([
            prompt_shared_key_bindings,
            this_key_bindings,
        ])
        self.prompt_multiline_shared_key_bindings = merge_key_bindings([
            prompt_shared_key_bindings,
            prompt_multiline_shared_key_bindings,
            this_key_bindings,
        ])

    def showKeyBindings(self):
        bindings = {
            "ctrl+q": "quit or exit current feature",
            "ctrl+c": "cancel",
            "ctrl+n": "new chat",
            "ctrl+y": "new chat without context",
            "ctrl+s": "save chat",
            "ctrl+o": "change predefined context",
            "ctrl+d": "swap developer mode",
            "ctrl+e": "swap command execution mode",
            "ctrl+l": "toggle multi-line entry",
            "ctrl+g": "toggle improved writing feature",
            "ctrl+k": "show key bindings",
            "escape+m": "toggle mouse support",
            "escape+t": "system command prompt",
            "escape+b": "move cursor to line beginning",
            "escape+e": "move cursor to line end",
            "escape+a": "move cursor to entry beginning",
            "escape+z": "move cursor to entry end",
            "escape+d": "forward delete",
            "escape+s": "swap text brightness",
        }
        multilineBindings = {
            "escape+1": "go up 10 lines",
            "escape+2": "go up 20 lines",
            "escape+3": "go up 30 lines",
            "escape+4": "go up 40 lines",
            "escape+5": "go up 50 lines",
            "escape+6": "go up 60 lines",
            "escape+7": "go up 70 lines",
            "escape+8": "go up 80 lines",
            "escape+9": "go up 90 lines",
            "escape+0": "go up 100 lines",
            "f1": "go down 10 lines",
            "f2": "go down 20 lines",
            "f3": "go down 30 lines",
            "f4": "go down 40 lines",
            "f5": "go down 50 lines",
            "f6": "go down 60 lines",
            "f7": "go down 70 lines",
            "f8": "go down 80 lines",
            "f9": "go down 90 lines",
            "f10": "go down 100 lines",
            "ctrl+i": f"insert '{config.terminalEditorTabText}' [configurable]",
            "ctrl+u": f"go up '{config.terminalEditorScrollLineCount}' lines [configurable]",
            "ctrl+j": f"go down '{config.terminalEditorScrollLineCount}' lines [configurable]",
        }
        print(config.divider)
        print("# Key Bindings")
        print("[blank]: launch action menu")
        for key, value in bindings.items():
            print(f"{key}: {value}")
        print("## Key Bindings [multiline entry only]")
        for key, value in multilineBindings.items():
            print(f"{key}: {value}")
        print(config.divider)
        

    def simplePrompt(self, numberOnly=False, validator=None, multiline=False, inputIndicator="", default="", accept_default=False, completer=None, promptSession=None, style=None, is_password=False):
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
            style=self.promptStyle1 if style is None else style,
            validator=validator,
            multiline=multiline,
            default=default,
            accept_default=accept_default,
            completer=completer,
            is_password=is_password,
            mouse_support=Condition(lambda: config.mouseSupport),
        ).strip()
        return userInput