from letmedoit import config
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from prompt_toolkit.shortcuts import input_dialog, radiolist_dialog, checkboxlist_dialog, message_dialog
from prompt_toolkit.completion import WordCompleter, FuzzyCompleter
from letmedoit.utils.promptValidator import NumberValidator


class TerminalModeDialogs:

    def __init__(self, parent) -> None:
        self.parent = parent
        self.style = Style.from_dict(
            {
                "dialog": "bg:ansiblack",
                "dialog text-area": f"bg:ansiblack {config.terminalCommandEntryColor2}",
                "dialog text-area.prompt": config.terminalPromptIndicatorColor2,
                "dialog radio-checked": config.terminalResourceLinkColor,
                "dialog checkbox-checked": config.terminalResourceLinkColor,
                "dialog button.arrow": config.terminalResourceLinkColor,
                "dialog button.focused": f"bg:{config.terminalResourceLinkColor} ansiblack",
                "dialog frame.border": config.terminalResourceLinkColor,
                "dialog frame.label": f"bg:ansiblack {config.terminalResourceLinkColor}",
                "dialog.body": "bg:ansiblack ansiwhite",
                "dialog shadow": "bg:ansiblack",
            }
        ) if config.terminalResourceLinkColor.startswith("ansibright") else Style.from_dict(
            {
                "dialog": "bg:ansiwhite",
                "dialog text-area": f"bg:ansiblack {config.terminalCommandEntryColor2}",
                "dialog text-area.prompt": config.terminalPromptIndicatorColor2,
                "dialog radio-checked": config.terminalResourceLinkColor,
                "dialog checkbox-checked": config.terminalResourceLinkColor,
                "dialog button.arrow": config.terminalResourceLinkColor,
                "dialog button.focused": f"bg:{config.terminalResourceLinkColor} ansiblack",
                "dialog frame.border": config.terminalResourceLinkColor,
                "dialog frame.label": f"bg:ansiwhite {config.terminalResourceLinkColor}",
                "dialog.body": "bg:ansiwhite ansiblack",
                "dialog shadow": "bg:ansiwhite",
            }
        )

    # a wrapper to standard input_dialog; open radiolist_dialog showing available options when user input is not a valid option.
    def searchableInput(self, title="Text Entry", text="Enter / Search:", default="", completer=None, options=[], descriptions=[], validator=None, numberOnly=False, password=False, ok_text="OK", cancel_text="Cancel"):
        if completer is None and options:
            completer = FuzzyCompleter(WordCompleter(options, ignore_case=True))
        if validator is None and numberOnly:
            validator=NumberValidator()
        result = input_dialog(
            title=title,
            text=text,
            default=default,
            completer=completer,
            validator=validator,
            password=password,
            ok_text=ok_text,
            cancel_text=cancel_text,
            style=self.style,
        ).run().strip()
        if result.lower() == config.cancel_entry:
            return result
        if options:
            if result and result in options:
                return result
            else:
                return self.getValidOptions(options=options, descriptions=descriptions, filter=result, default=default)
        else:
            if result:
                return result
            else:
                return ""

    def getValidOptions(self, options=[], descriptions=[], bold_descriptions=False, filter="", default="", title="Available Options", text="Select an option:"):
        if not options:
            return ""
        filter = filter.strip().lower()
        if descriptions:
            descriptionslower = [i.lower() for i in descriptions]
            values = [(option, HTML(f"<b>{descriptions[index]}</b>") if bold_descriptions else descriptions[index]) for index, option in enumerate(options) if (filter in option.lower() or filter in descriptionslower[index])]
        else:
            values = [(option, option) for option in options if filter in option.lower()]
        if not values:
            if descriptions:
                values = [(option, HTML(f"<b>{descriptions[index]}</b>") if bold_descriptions else descriptions[index]) for index, option in enumerate(options)]
            else:
                values = [(option, option) for option in options]
        result = radiolist_dialog(
            title=title,
            text=text,
            values=values,
            default=default if default and default in options else values[0][0],
            style=self.style,
        ).run()
        if result:
            notice = f"You've chosen: {result}"
            config.print3(notice)
            return result
        return ""

    def displayFeatureMenu(self, heading, features):
        values = [(command, command if config.terminalDisplayCommandOnMenu else self.parent.dotCommands[command][0]) for command in features]
        result = radiolist_dialog(
            title=heading,
            text="Select a feature:",
            values=values,
            default=features[0],
            style=self.style,
        ).run()
        if result:
            self.parent.printRunningCommand(result)
            return self.parent.getContent(result)
        else:
            return self.parent.exitAction()
            #return ""

    def getMultipleSelection(self, title="Multiple Selection", text="Select item(s):", options=["ALL"], descriptions=[], default_values=["ALL"]):
        if descriptions:
            values = [(option, descriptions[index]) for index, option in enumerate(options)]
        else:
            values = [(option, option) for option in options]
        return checkboxlist_dialog(
            title=title,
            text=text,
            values=values,
            default_values=default_values,
            style=self.style,
        ).run()
