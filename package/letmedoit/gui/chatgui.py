from letmedoit import config
from letmedoit.utils.shared_utils import SharedUtil
from letmedoit.gui.worker import Worker
import json, getpass
from typing import Tuple

from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtCore import Qt, QThread, QRegularExpression, QRunnable, Slot, Signal, QObject, QThreadPool
from PySide6.QtGui import QStandardItemModel, QStandardItem, QGuiApplication, QAction, QIcon, QFontMetrics, QTextDocument
from PySide6.QtWidgets import QCompleter, QMenu, QSystemTrayIcon, QApplication, QMainWindow, QWidget, QDialog, QFileDialog, QDialogButtonBox, QFormLayout, QLabel, QMessageBox, QCheckBox, QPlainTextEdit, QProgressBar, QPushButton, QListView, QHBoxLayout, QVBoxLayout, QLineEdit, QSplitter, QComboBox

class CentralWidget(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # set up variables
        self.setupVariables()
        # set up interface
        self.setupUI()
    
    def setupVariables(self):
        # username
        self.user = getpass.getuser()
        # load LetMeDoIt AI system message
        config.currentMessages=SharedUtil.resetMessages()
        # thread pool
        self.threadpool = QThreadPool()

    def setupUI(self):
        # a layout with left and right columns and a splitter placed between them
        layout000 = QHBoxLayout()
        self.setLayout(layout000)
        
        widgetLt = QWidget()
        layout000Lt = QVBoxLayout()
        widgetLt.setLayout(layout000Lt)
        widgetRt = QWidget()
        layout000Rt = QVBoxLayout()
        widgetRt.setLayout(layout000Rt)
        
        splitter = QSplitter(Qt.Horizontal, self)
        splitter.addWidget(widgetLt)
        splitter.addWidget(widgetRt)
        layout000.addWidget(splitter)

        # add widgets to left column later
        widgetLt.hide()

        # widgets
        # user input
        self.userInput = QLineEdit()
        completer = QCompleter(config.inputSuggestions)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.userInput.setCompleter(completer)
        self.userInput.setPlaceholderText("Enter your request here ...")
        self.userInput.mousePressEvent = lambda _ : self.userInput.selectAll()
        self.userInput.setClearButtonEnabled(True)
        # content view
        self.contentView = QPlainTextEdit()
        self.contentView.setReadOnly(True)
        # progress bar
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 0) # Set the progress bar to use an indeterminate progress indicator
        
        # update layout
        layout000Rt.addWidget(self.userInput)
        layout000Rt.addWidget(self.contentView)
        layout000Rt.addWidget(self.progressBar)
        self.progressBar.hide()

        # Connections
        self.userInput.returnPressed.connect(self.submit)

    def workOnGetResponse(self):
        # Pass the function to execute
        worker = Worker(self.submit) # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.processResponse)
        worker.signals.progress.connect(self.printStream)
        # Connection
        #worker.signals.finished.connect(None)
        # Execute
        self.threadpool.start(worker)

    def processResponse(self):
        ...

    def printStream(self):
        ...

    def submit(self, progress_callback="") -> None:
        request = self.userInput.text().strip()
        if request:
            self.userInput.setDisabled(True)
            self.addContent(request)
            extendChat, response = self.chat_tools(request)
            if extendChat:
                response = self.chat()
            self.addContent(response, False)
            # reset user input field
            self.userInput.setText("")
            self.userInput.setEnabled(True)
            self.userInput.setFocus()

    def addContent(self, newContent, user=True) -> None:
        content = self.contentView.toPlainText()
        if content:
            self.contentView.insertPlainText("\n\n")
        self.contentView.insertPlainText(f"[{self.user}] " if user else f"[{config.letMeDoItName}] ")
        self.contentView.insertPlainText(newContent)

    def chat(self) -> str:
        # run completion
        completion = config.oai_client.chat.completions.create(
            model=config.chatGPTApiModel,
            messages=config.currentMessages,
            n=1,
            temperature=config.llmTemperature,
            max_tokens=SharedUtil.getDynamicTokens(config.currentMessages, config.chatGPTApiFunctionSignatures.values()),
            #stream=True,
        )
        # update message chain
        if response := completion.choices[0].message.content:
            config.currentMessages.append({"role": "assistant", "content": response})
            return response
        return ""

    def chat_tools(self, request) -> Tuple[bool, str]:
        user_request = {"role": "user", "content": request}
        # temporary update of messages
        messages = config.currentMessages + [user_request]
        # run completion
        completion = config.oai_client.chat.completions.create(
            model=config.chatGPTApiModel,
            messages=messages,
            n=1,
            temperature=config.llmTemperature,
            max_tokens=SharedUtil.getDynamicTokens(messages, config.chatGPTApiFunctionSignatures.values()),
            tools=SharedUtil.convertFunctionSignaturesIntoTools(config.chatGPTApiFunctionSignatures.values()),
            tool_choice="auto",
            #stream=True,
        )
        output = completion.choices[0].message
        if output.content:
            # direct answer
            response = output.content
            extendChat = False
            # update message chain
            config.currentMessages += [user_request, {"role": "assistant", "content": response}]
        elif output.tool_calls:
            for tool_call in output.tool_calls:
                tool = tool_call.function
                name, arguments = tool.name, tool.arguments
                response = config.chatGPTApiAvailableFunctions[name](json.loads(arguments))

                function_call_message = {
                    "role": "assistant",
                    "content": "",
                    "function_call": {
                        "name": name,
                        "arguments": arguments,
                    }
                }

                function_call_response = {
                    "role": "function",
                    "name": name,
                    "content": response if response else config.tempContent,
                }
                # empty tempContent
                config.tempContent = ""

                # handle response
                if not response:
                    # update message chain
                    config.currentMessages += [user_request, function_call_message, function_call_response]
                    # function executed without chat extension
                    extendChat = False
                elif response == "[INVALID]":
                    # update message chain
                    config.currentMessages.append(user_request)
                    # function attempted to be executed but found invalid tool applied
                    response = request
                    extendChat = True
                else:
                    # update message chain
                    config.currentMessages += [user_request, function_call_message, function_call_response]
                    # function executed with chat extension
                    extendChat = True
        else:
            response = ""
            extendChat = False
        # ignore response for now
        return (extendChat, response)

class ChatGui(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        # set title
        self.setWindowTitle(config.letMeDoItName)
        # set variables
        self.setupVariables()
        # run plugins
        SharedUtil.runPlugins()
        # gui
        self.initUI()

    def closeEvent(self, event):
        # hiding it, instead of closing it, to save from reloading time
        event.ignore()
        self.hide()
        #config.mainWindowHidden = True

    def setupVariables(self):
        SharedUtil.setAPIkey() # create a gui for it later
        def stopSpinning():
            ...
        config.stopSpinning = stopSpinning

    def initUI(self):
        self.centralWidget = CentralWidget(self)
        self.setCentralWidget(self.centralWidget)
