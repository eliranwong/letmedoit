import config, pydoc, traceback
from prompt_toolkit.key_binding import KeyBindings


prompt_shared_key_bindings = KeyBindings()

# selection
"""
# select all
@prompt_shared_key_bindings.add("c-a")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_position = 0
    buffer.start_selection()
    buffer.cursor_position = len(buffer.text)
"""

# navigation

# go to current line starting position
@prompt_shared_key_bindings.add("c-j")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_position = buffer.cursor_position - buffer.document.cursor_position_col
# go to current line ending position
@prompt_shared_key_bindings.add("c-e")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_position = buffer.cursor_position + buffer.document.get_end_of_line_position()
# go to current line starting position
@prompt_shared_key_bindings.add("home")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_position = buffer.cursor_position - buffer.document.cursor_position_col
# go to current line ending position
@prompt_shared_key_bindings.add("end")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_position = buffer.cursor_position + buffer.document.get_end_of_line_position()
# go to the end of the text
@prompt_shared_key_bindings.add("escape", "e")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_position = len(buffer.text)
# go to the beginning of the text
@prompt_shared_key_bindings.add("escape", "j")
def _(event):
    buffer = event.app.current_buffer
    buffer.cursor_position = 0

# delete after cusor
@prompt_shared_key_bindings.add("c-d")
def _(event):
    buffer = event.app.current_buffer
    data = buffer.delete(1)

# swap color theme
@prompt_shared_key_bindings.add("escape", "s")
def _(_):
    swapTerminalColors()

@staticmethod
def swapTerminalColors():
    if config.terminalResourceLinkColor in config.terminalColors:
        config.terminalResourceLinkColor = config.terminalColors[config.terminalResourceLinkColor]
    if config.terminalPromptIndicatorColor1 in config.terminalColors:
        config.terminalPromptIndicatorColor1 = config.terminalColors[config.terminalPromptIndicatorColor1]
    if config.terminalCommandEntryColor1 in config.terminalColors:
        config.terminalCommandEntryColor1 = config.terminalColors[config.terminalCommandEntryColor1]
    if config.terminalPromptIndicatorColor2 in config.terminalColors:
        config.terminalPromptIndicatorColor2 = config.terminalColors[config.terminalPromptIndicatorColor2]
    if config.terminalCommandEntryColor2 in config.terminalColors:
        config.terminalCommandEntryColor2 = config.terminalColors[config.terminalCommandEntryColor2]
    if config.terminalHeadingTextColor in config.terminalColors:
        config.terminalHeadingTextColor = config.terminalColors[config.terminalHeadingTextColor]
#    if config.terminalVerseNumberColor in config.terminalColors:
#        config.terminalVerseNumberColor = config.terminalColors[config.terminalVerseNumberColor]
#    if config.terminalVerseSelectionBackground in config.terminalColors:
#        config.terminalVerseSelectionBackground = config.terminalColors[config.terminalVerseSelectionBackground]
#    if config.terminalVerseSelectionForeground in config.terminalColors:
#        config.terminalVerseSelectionForeground = config.terminalColors[config.terminalVerseSelectionForeground]
#    if config.terminalSearchHighlightBackground in config.terminalColors:
#        config.terminalSearchHighlightBackground = config.terminalColors[config.terminalSearchHighlightBackground]
#    if config.terminalSearchHighlightForeground in config.terminalColors:
#        config.terminalSearchHighlightForeground = config.terminalColors[config.terminalSearchHighlightForeground]
#    if config.terminalFindHighlightBackground in config.terminalColors:
#        config.terminalFindHighlightBackground = config.terminalColors[config.terminalFindHighlightBackground]
#    if config.terminalFindHighlightForeground in config.terminalColors:
#        config.terminalFindHighlightForeground = config.terminalColors[config.terminalFindHighlightForeground]
    #config.terminalSwapColors = (config.terminalResourceLinkColor.startswith("ansibright"))

# change text

# delete text, Ctrl+H or Backspace
@prompt_shared_key_bindings.add("c-h")
def _(event):
    buffer = event.app.current_buffer
    data = buffer.cut_selection()
    # delete one char before cursor as Backspace usually does when there is no text selection.
    if not data.text and buffer.cursor_position >= 1:
        buffer.start_selection()
        buffer.cursor_position = buffer.cursor_position - 1
        buffer.cut_selection()

# binded in this set
#a, j, e, c, v, x, h, i