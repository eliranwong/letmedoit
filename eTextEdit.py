#!/usr/bin/env python
"""
# eTextEdit

An Extensible Text Editor, built with prompt toolkit.

Originally a simple text editor created by Jonathan Slenders
Source: https://github.com/prompt-toolkit/python-prompt-toolkit/blob/master/examples/full-screen/text-editor.py

Modified and Enhanced by Eliran Wong:
* added file and clipboard utilities
* added regex search & replace feature
* added key bindings
* added handling of unasaved changes
* added dark theme and lexer style
* support stdin, e.g. echo "Hello world!" | python3 eTextEdit.py
* support file argument, e.g. python3 eTextEdit.py <filename>
* support plugins (forthcoming)

eTextEdit repository:
https://github.com/eliranwong/eTextEdit
"""
import datetime, sys, os, re, webbrowser
from asyncio import Future, ensure_future
from prompt_toolkit.clipboard.pyperclip import PyperclipClipboard
from prompt_toolkit.input import create_input
from prompt_toolkit.styles import merge_styles
from pygments.styles import get_style_by_name
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from prompt_toolkit.shortcuts import set_title, clear_title
from prompt_toolkit import HTML
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import (
    ConditionalContainer,
    Float,
    HSplit,
    VSplit,
    Window,
    WindowAlign,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.lexers import DynamicLexer, PygmentsLexer
from prompt_toolkit.search import start_search, SearchDirection
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import (
    Button,
    Dialog,
    Label,
    MenuContainer,
    MenuItem,
    SearchToolbar,
    TextArea,
    Checkbox,
)

class ApplicationState:
    """
    Application state.

    For the simplicity, we store this as a global, but better would be to
    instantiate this as an object and pass at around.
    """

    show_status_bar = True
    current_path = None
    focus_menu = False
    saved_text = ""
    enable_regex_search = False
    enable_case_sensitive_search = False
    search_pattern = ""
    replace_pattern = ""
    clipboard = PyperclipClipboard()

def get_statusbar_text():
    return " [esc-m] menu [ctrl+k] help "

def get_statusbar_right_text():
    return " {}:{}  ".format(
        text_field.document.cursor_position_row + 1,
        text_field.document.cursor_position_col + 1,
    )

def formatDialogTitle(title):
    return HTML(f"<ansimagenta>{title}</ansimagenta>")

search_toolbar = SearchToolbar(ignore_case=True)
text_field = TextArea(
    style="class:textarea",
    lexer=DynamicLexer(
        lambda: PygmentsLexer.from_filename(
            ApplicationState.current_path or ".md", sync_from_start=False
        )
    ),
    scrollbar=True,
    line_numbers=True,
    search_field=search_toolbar,
    focus_on_click=True,
)

class NumberValidator(Validator):
    def validate(self, document):
        text = document.text
        if text and not text.isdigit():
            i = 0
            # Get index of first non numeric character.
            # We want to move the cursor here.
            for i, c in enumerate(text):
                if not c.isdigit():
                    break
            raise ValidationError(message='Integer ONLY!', cursor_position=i)

class TextInputDialog:
    def __init__(self, title="", label_text="", completer=None, validator=None):
        self.future = Future()

        def accept_text(buf):
            get_app().layout.focus(ok_button)
            buf.complete_state = None
            return True

        def accept():
            self.future.set_result(self.text_area.text)

        def cancel():
            self.future.set_result(None)

        self.text_area = TextArea(
            validator=validator,
            completer=completer,
            multiline=False,
            width=D(preferred=40),
            accept_handler=accept_text,
            focus_on_click=True,
        )

        ok_button = Button(text="OK", handler=accept)
        cancel_button = Button(text="Cancel", handler=cancel)

        self.dialog = Dialog(
            title=formatDialogTitle(title),
            body=HSplit([Label(text=label_text), self.text_area]),
            buttons=[ok_button, cancel_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog

class SearchReplaceDialog:
    def __init__(self, title="", label_find="", label_replace="", completer=None):
        self.future = Future()

        def accept_find(buf):
            get_app().layout.focus(self.replace_area)
            buf.complete_state = None
            return True

        def accept_replace(buf):
            get_app().layout.focus(selection_only_button)
            buf.complete_state = None
            return True

        def replace_all():
            self.future.set_result((True, self.case_sensitivity.checked, self.regex_search.checked, self.search_area.text, self.replace_area.text))

        def selection_only():
            self.future.set_result((False, self.case_sensitivity.checked, self.regex_search.checked, self.search_area.text, self.replace_area.text))

        def cancel():
            self.future.set_result(None)

        current_text_selection = text_field.buffer.copy_selection().text
        self.search_area = TextArea(
            text=current_text_selection if current_text_selection else ApplicationState.search_pattern,
            completer=completer,
            multiline=True,
            width=D(preferred=40),
            height=D(preferred=3),
            focus_on_click=True,
            accept_handler=accept_find,
        )

        self.replace_area = TextArea(
            text=ApplicationState.replace_pattern,
            completer=completer,
            multiline=True,
            width=D(preferred=40),
            height=D(preferred=3),
            focus_on_click=True,
            accept_handler=accept_replace,
        )

        self.case_sensitivity = Checkbox(text="case-sensitive", checked=ApplicationState.enable_case_sensitive_search)
        self.regex_search = Checkbox(text="regular expression", checked=ApplicationState.enable_regex_search)

        replace_all_button = Button(text="All", handler=replace_all)
        selection_only_button = Button(text="Selection", handler=selection_only)
        cancel_button = Button(text="Cancel", handler=cancel)

        self.dialog = Dialog(
            title=formatDialogTitle(title),
            body=HSplit([Label(text=label_find), self.search_area, Label(text=label_replace), self.replace_area, VSplit([self.case_sensitivity, self.regex_search])]),
            buttons=[replace_all_button, selection_only_button, cancel_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog

class MessageDialog:
    def __init__(self, title, text):
        self.future = Future()

        def set_done():
            self.future.set_result(None)

        ok_button = Button(text="OK", handler=(lambda: set_done()))

        self.dialog = Dialog(
            title=formatDialogTitle(title),
            body=HSplit([Label(text=text)]),
            buttons=[ok_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog

class ConfirmDialog:
    def __init__(self, title, text):
        self.future = Future()

        def yes():
            self.future.set_result(True)

        def no():
            self.future.set_result(False)

        ok_button = Button(text="YES", handler=yes)
        no_button = Button(text="NO", handler=no)

        self.dialog = Dialog(
            title=formatDialogTitle(title),
            body=HSplit([Label(text=text)]),
            buttons=[ok_button, no_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog

body = HSplit(
    [
        text_field,
        search_toolbar,
        ConditionalContainer(
            content=VSplit(
                [
                    Window(
                        FormattedTextControl(get_statusbar_text), style="class:status"
                    ),
                    Window(
                        FormattedTextControl(get_statusbar_right_text),
                        style="class:status.right",
                        width=9,
                        align=WindowAlign.RIGHT,
                    ),
                ],
                height=1,
            ),
            filter=Condition(lambda: ApplicationState.show_status_bar),
        ),
    ]
)

# Global key bindings.
bindings = KeyBindings()

@bindings.add("escape", "m")
def _(event):
    if ApplicationState.focus_menu:
        # Focus text area
        event.app.layout.focus(text_field)
        ApplicationState.focus_menu = False
    else:
        # Focus menu
        event.app.layout.focus(root_container.window)
        ApplicationState.focus_menu = True
    
@bindings.add("c-k")
def _(_):
    do_help()

@bindings.add("c-q")
def _(_):
    do_exit()

@bindings.add("escape", "a")
def _(_):
    do_deselect_all()

@bindings.add("c-a")
def _(_):
    do_select_all()

@bindings.add("c-c")
def _(_):
    do_copy()

@bindings.add("c-v")
def _(_):
    do_paste()

@bindings.add("c-x")
def _(_):
    do_cut()

@bindings.add("c-z")
def _(_):
    do_undo()

@bindings.add("c-i")
def _(_):
    do_add_spaces()

@bindings.add("c-f")
def _(_):
    do_find()

@bindings.add("c-r")
def _(_):
    do_find_replace()

@bindings.add("c-l")
def _(_):
    do_go_to()

@bindings.add("c-d")
def _(_):
    do_delete()

@bindings.add("c-n")
def _(_):
    do_new_file()

@bindings.add("c-s")
def _(_):
    do_save_file()

@bindings.add("c-o")
def _(_):
    do_open_file()

@bindings.add("c-w")
def _(_):
    do_save_as_file()

#
# Handlers for menu items.
#

def do_save_file():
    if ApplicationState.current_path:
        try:
            with open(ApplicationState.current_path, "w", encoding="utf-8") as fileObj:
                fileObj.write(text_field.text)
            ApplicationState.saved_text = text_field.text
        except OSError as e:
            show_message("Error", f"{e}")
    else:
        do_save_as_file()
    update_title()

def do_save_as_file():
    async def coroutine():
        save_dialog = TextInputDialog(
            title="Save as file",
            label_text="Enter the path of a file:",
            completer=PathCompleter(),
        )

        path = await show_dialog_as_float(save_dialog)
        ApplicationState.current_path = path

        if path is not None:
            do_save_file()

    ensure_future(coroutine())

def do_open_file():
    check_changes_before_execute(confirm_open_file)

def confirm_open_file():
    async def coroutine():
        open_dialog = TextInputDialog(
            title="Open file",
            label_text="Enter the path of a file:",
            completer=PathCompleter(),
        )

        path = await show_dialog_as_float(open_dialog)
        ApplicationState.current_path = path

        if path is not None:
            try:
                #with open(path, "rb") as f:
                #    text_field.text = f.read().decode("utf-8", errors="ignore")
                with open(path, "r", encoding="utf-8") as fileObj:
                    text_field.text = fileObj.read()
            except OSError as e:
                show_message("Error", f"{e}")
                ApplicationState.current_path = None
        update_title()

    ensure_future(coroutine())

def do_find_replace():
    async def coroutine():
        search_replace_dialog = SearchReplaceDialog(
            title="Find & Replace",
            label_find="Find:",
            label_replace="Replace with:",
        )

        response = await show_dialog_as_float(search_replace_dialog)

        if response is not None:
            replace_all, case_sensitive, regex_search, search_pattern, replace_pattern = response
            ApplicationState.enable_case_sensitive_search = case_sensitive
            ApplicationState.enable_regex_search = regex_search
            ApplicationState.search_pattern = search_pattern
            ApplicationState.replace_pattern = replace_pattern
            buffer = text_field.buffer
            original_text = buffer.text if replace_all else buffer.copy_selection().text
            replaced_text = re.sub(search_pattern if regex_search else re.escape(search_pattern), replace_pattern if regex_search else re.escape(replace_pattern), original_text, flags=re.M if case_sensitive else re.I | re.M)
            if replace_all:
                buffer.text = replaced_text
            else:
                buffer.cut_selection()
                buffer.insert_text(replaced_text)

    ensure_future(coroutine())

def do_about():
    # source https://github.com/prompt-toolkit/python-prompt-toolkit/blob/master/examples/full-screen/text-editor.py
    enhancedFeatures = """
* added file and clipboard utilities
* added regex search & replace feature
* added key bindings
* added handling of unasaved changes
* added dark theme and lexer style
* support stdin, e.g. echo "Hello world!" | python3 eTextEdit.py
* support file argument, e.g. python3 eTextEdit.py <filename>
* support plugins (forthcoming)"""
    show_message("About", f"Text Editor\nOriginally created by Jonathan Slenders\nEnhanced by Eliran Wong:{enhancedFeatures}")

def show_message(title, text):
    async def coroutine():
        dialog = MessageDialog(title, text)
        await show_dialog_as_float(dialog)

    ensure_future(coroutine())

async def show_dialog_as_float(dialog):
    "Coroutine."
    float_ = Float(content=dialog)
    root_container.floats.insert(0, float_)

    app = get_app()

    focused_before = app.layout.current_window
    app.layout.focus(dialog)
    result = await dialog.future
    app.layout.focus(focused_before)

    if float_ in root_container.floats:
        root_container.floats.remove(float_)

    return result

def do_new_file():
    check_changes_before_execute(confirm_new_file)

def confirm_new_file():
    ApplicationState.current_path = None
    text_field.text = ""
    ApplicationState.saved_text = text_field.text
    update_title()

# check if there are unsaved changes before executing a function
def check_changes_before_execute(func):
    async def coroutine():
        if not text_field.text == ApplicationState.saved_text:
            title = 'Changes unsaved!'
            text = 'Do you want to save your changes first?'
            dialog = ConfirmDialog(title, text)
            response = await show_dialog_as_float(dialog)
            if response:
                do_save_file()
            else:
                # execute function if users discard the changes
                func()
        else:
            # execute function if no changes are made
            func()
    ensure_future(coroutine())

def do_help():
    webbrowser.open("https://github.com/eliranwong/eTextEdit")

def do_exit():
    check_changes_before_execute(get_app().exit)

def do_time_date():
    text = datetime.datetime.now().isoformat()
    text_field.buffer.insert_text(text)

def do_add_spaces():
    text_field.buffer.insert_text("    ")

def do_go_to():
    async def coroutine():
        dialog = TextInputDialog(title="Go to line", label_text="Line number:", validator=NumberValidator())

        line_number = await show_dialog_as_float(dialog)
        if line_number is not None:
            try:
                line_number = int(line_number)
            except ValueError:
                show_message("Invalid line number")
            else:
                text_field.buffer.cursor_position = (
                    text_field.buffer.document.translate_row_col_to_index(
                        line_number - 1, 0
                    )
                )
    ensure_future(coroutine())

def do_undo():
    text_field.buffer.undo()

def do_redo():
    #it does not work properly
    text_field.buffer.redo()

def do_cut():
    data = text_field.buffer.cut_selection()
    get_app().clipboard.set_data(data)

def do_copy():
    data = text_field.buffer.copy_selection()
    get_app().clipboard.set_data(data)

def do_delete():
    text_field.buffer.cut_selection()

def do_find():
    start_search(text_field.control)

def do_find_reverse():
    start_search(text_field.control, direction=SearchDirection.BACKWARD)

def do_find_next():
    search_state = get_app().current_search_state

    cursor_position = text_field.buffer.get_search_position(
        search_state, include_current_position=False
    )
    text_field.buffer.cursor_position = cursor_position

def do_paste():
    buffer = text_field.buffer
    buffer.cut_selection()
    clipboardText = ApplicationState.clipboard.get_data().text
    buffer.insert_text(clipboardText)
    # the following line does not work well; cursor position not aligned
    #text_field.buffer.paste_clipboard_data(get_app().clipboard.get_data())

def do_deselect_all():
    buffer = text_field.buffer
    cursor_position = buffer.cursor_position
    text = buffer.text
    buffer.reset()
    buffer.text = text
    buffer.cursor_position = cursor_position

def do_select_all():
    # toggle between select all and deselect all
    buffer = text_field.buffer
    # select all
    text_field.buffer.cursor_position = 0
    text_field.buffer.start_selection()
    text_field.buffer.cursor_position = len(buffer.text)

def do_status_bar():
    ApplicationState.show_status_bar = not ApplicationState.show_status_bar

#
# The menu container.
#

root_container = MenuContainer(
    body=body,
    menu_items=[
        MenuItem(
            "File",
            children=[
                MenuItem("[N] New", handler=do_new_file),
                MenuItem("[O] Open", handler=do_open_file),
                MenuItem("[S] Save", handler=do_save_file),
                MenuItem("[W] Save as", handler=do_save_as_file),
                MenuItem("-", disabled=True),
                MenuItem("[Q] Exit", handler=do_exit),
            ],
        ),
        MenuItem(
            "Edit",
            children=[
                MenuItem("[A] Select All", handler=do_select_all),
                MenuItem("-", disabled=True),
                MenuItem("[Z] Undo", handler=do_undo),
                #MenuItem("[Y] Redo", handler=do_redo),
                MenuItem("-", disabled=True),
                MenuItem("[C] Copy", handler=do_copy),
                MenuItem("[V] Paste", handler=do_paste),
                MenuItem("[X] Cut", handler=do_cut),
                MenuItem("[D] Delete", handler=do_delete),
                MenuItem("-", disabled=True),
                MenuItem("[F] Find", handler=do_find),
                MenuItem("[R] Find & Replace", handler=do_find_reverse),
                #MenuItem("Find next", handler=do_find_next),
                #MenuItem("Replace"),
                MenuItem("[L] Go To Line", handler=do_go_to),
                MenuItem("-", disabled=True),
                MenuItem("[I] Spaces", handler=do_add_spaces),
                MenuItem("Time / Date", handler=do_time_date),
            ],
        ),
        MenuItem(
            "View",
            children=[MenuItem("Status Bar", handler=do_status_bar)],
        ),
        MenuItem(
            "Info",
            children=[
                MenuItem("About", handler=do_about),
                MenuItem("Help", handler=do_help),
            ],
        ),
    ],
    floats=[
        Float(
            xcursor=True,
            ycursor=True,
            content=CompletionsMenu(max_height=16, scroll_offset=1),
        ),
    ],
    key_bindings=bindings,
)

# Combine custom and monokai styles
custom_style = Style.from_dict(
    {
        "status": "reverse",
        "shadow": "bg:#440044",
        "textarea": "bg:#1E1E1E",
        "search-toolbar": "bg:#1E1E1E",
        "button.focused": "bg:#F9AAF8 fg:#000000"
    }
)
#https://github.com/prompt-toolkit/python-prompt-toolkit/issues/765#issuecomment-434465617
#(Not to a TextArea or any other UI component.)
# convert pygments style to prompt toolkit style
# To check available pygments styles, run
"""
import pygments.styles 
 
styles = pygments.styles.get_all_styles() 
for i in styles: 
    print(i) 
"""
monokai_style = style_from_pygments_cls(get_style_by_name("github-dark"))
combined_style = merge_styles([
    custom_style,
    monokai_style,
])

layout = Layout(root_container, focused_element=text_field)

def update_title():
    set_title(f'''eTextEdit - {os.path.basename(ApplicationState.current_path) if ApplicationState.current_path else "NEW"}''')

def launch(input_text=None, filename=None):
    if filename and os.path.isfile(filename):
        try:
            with open(filename, "r", encoding="utf-8") as fileObj:
                fileText = fileObj.read()
        except:
            filename = None
    else:
        filename = None
    if filename:
        ApplicationState.current_path = filename
        ApplicationState.saved_text = fileText
    update_title()
    if filename and input_text:
        # append file text with input text
        text_field.text = f"{fileText}\n{input_text}"
    elif filename:
        text_field.text = fileText
    elif input_text:
        text_field.text = input_text
    # create a custom input to work with stdin without EOFError
    input = create_input(always_prefer_tty=True)
    application = Application(
        layout=layout,
        enable_page_navigation_bindings=True,
        style=combined_style,
        mouse_support=True,
        full_screen=True,
        input=input,
        clipboard=ApplicationState.clipboard,
    )
    application.run()
    clear_title()
    return text_field.text

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # users may use unescaped space for filename
        filename = sys.argv[1] if len(sys.argv) == 2 else " ".join(sys.argv[1:])
        try:
            # create file if it does not exist
            if not os.path.isfile(filename):
                open(filename, "a", encoding="utf-8").close()
            if not sys.stdin.isatty():
                input_text = sys.stdin.read()
                text = launch(input_text=input_text, filename=filename)
            else:
                text = launch(filename=filename)
        except:
            text = launch()
    elif not sys.stdin.isatty():
        input_text = sys.stdin.read()
        text = launch(input_text=input_text)
    else:
        text = launch()
    #print(text)