from prompt_toolkit.application import Application
from prompt_toolkit.layout import HSplit, VSplit, Layout, Dimension
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.application.current import get_app
from prompt_toolkit.key_binding import KeyBindings

class DynamicLayout:

    def __init__(self):
        self.text_area1 = TextArea(text='Text Area 1')
        self.text_area2 = TextArea(text='Text Area 2')

    def getLayout(self):
        height, width = self.app.output.get_size()
        #print(width, height)

        if width > height:
            #print("landscape")
            return Layout(VSplit([self.text_area1, self.text_area2]))
        else:
            #print("portrait")
            return Layout(HSplit([self.text_area1, self.text_area2]))

    def updateLayout(self):
        self.app.layout = self.getLayout()

    def run(self):
        kb = KeyBindings()

        @kb.add('c-l')  # change layout
        def _(event):
            self.updateLayout()

        self.app = Application(full_screen=True, key_bindings=kb)
        self.app.layout = self.getLayout()
        self.app.run()

DynamicLayout().run()