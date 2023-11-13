#!/usr/bin/env python
import subprocess
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import SearchToolbar, TextArea

help_text = """A simple terminal emulator by Eliran Wong"""


class TerminalEmulator:

    def __init__(self):

        # The layout.
        self.output_field = TextArea(
            style="class:output-field",
            text=help_text,
            focusable=True,
            focus_on_click=True,
            read_only=True,
        )
        self.search_field = SearchToolbar()
        self.input_field = TextArea(
            height=1,
            prompt=">>> ",
            style="class:input-field",
            multiline=False,
            wrap_lines=False,
            search_field=self.search_field,
            focusable=True,
            focus_on_click=True,
        )
        self.input_field.accept_handler = self.run_command

    def run_command(self, buffer):
        self.output_field.text = f"{self.output_field.text}\n\n>>> {buffer.text}"

        # Start the subprocess with stdout set to PIPE
        process = subprocess.Popen(self.input_field.text, shell=True, stdout=subprocess.PIPE)

        # Read the output in real-time
        while True:
            # Read a line from the output
            output = process.stdout.readline().decode().strip()

            # If there is no more output, break the loop
            if not output:
                break

            # Do something with the output
            self.output_field.text = f"{self.output_field.text}\n{output}"
            self.output_field.buffer.cursor_position = len(self.output_field.text)

        # Wait for the process to complete
        process.wait()
        # reset is necessary after another full-screen application is closed
        self.app.reset()


    def run(self):

        # The key bindings.
        kb = KeyBindings()

        @kb.add("c-c")
        @kb.add("c-q")
        def _(event):
            "Pressing Ctrl-Q or Ctrl-C will exit the user interface."
            event.app.exit()

        # Style.
        style = Style(
            [
                ("output-field", "bg:#000000 #ffffff"),
                ("input-field", "bg:#000000 #ffffff"),
                ("line", "#004400"),
            ]
        )

        # Run application.
        container = HSplit(
            [
                self.output_field,
                Window(height=1, char="-", style="class:line"),
                self.input_field,
                self.search_field,
            ]
        )
        self.app = Application(
            layout=Layout(container, focused_element=self.input_field),
            key_bindings=kb,
            style=style,
            mouse_support=True,
            full_screen=True,
        )

        self.app.run()


if __name__ == "__main__":
    TerminalEmulator().run()
