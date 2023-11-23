from taskwiz import config
from taskwiz.utils.shared_utils import SharedUtil
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.application import run_in_terminal
#from prompt_toolkit.application import get_app
try:
    import tiktoken
    tiktokenImported = True
except:
    tiktokenImported = False


class TokenValidator(Validator):
    def validate(self, document):
        #current_buffer = get_app().current_buffer
        currentInput = document.text
        if currentInput.lower() in (config.exit_entry, config.cancel_entry, ".new", ".share", ".save", ""):
            pass
        elif tiktokenImported:
            try:
                encoding = tiktoken.encoding_for_model(config.chatGPTApiModel)
            except:
                encoding = tiktoken.get_encoding("cl100k_base")
            if "[NO_FUNCTION_CALL]" in currentInput:
                availableFunctionTokens = 0
                currentInput = currentInput.replace("[NO_FUNCTION_CALL]", "")
            else:
                availableFunctionTokens = SharedUtil.count_tokens_from_functions(config.chatGPTApiFunctionSignatures)
            currentInputTokens = len(encoding.encode(config.fineTuneUserInput(currentInput)))
            loadedMessageTokens = SharedUtil.count_tokens_from_messages(config.currentMessages)
            selectedModelLimit = SharedUtil.tokenLimits[config.chatGPTApiModel]
            #estimatedAvailableTokens = selectedModelLimit - availableFunctionTokens - loadedMessageTokens - currentInputTokens

            config.dynamicToolBarText = f" Tokens: {(availableFunctionTokens + loadedMessageTokens + currentInputTokens)}/{selectedModelLimit} [ctrl+k] shortcut keys "
            #if config.conversationStarted:
            #    config.dynamicToolBarText = config.dynamicToolBarText + " [ctrl+n] new"
            if selectedModelLimit - (availableFunctionTokens + loadedMessageTokens + currentInputTokens) >= config.chatGPTApiMinTokens:
                pass
            else:
                run_in_terminal(lambda: print("Press 'ctrl+n' to start a new chat!"))
                raise ValidationError(message='Token limit reached!', cursor_position=document.cursor_position)
        else:
            pass


class NumberValidator(Validator):
    def validate(self, document):
        text = document.text

        if text.lower() in (config.exit_entry, config.cancel_entry):
            pass
        elif text and not text.isdigit():
            i = 0

            # Get index of first non numeric character.
            # We want to move the cursor here.
            for i, c in enumerate(text):
                if not c.isdigit():
                    break

            raise ValidationError(message='This entry accepts numbers only!', cursor_position=i)


class FloatValidator(Validator):
    def validate(self, document):
        text = document.text

        if text.lower() in (config.exit_entry, config.cancel_entry):
            pass
        try:
            float(text)
        except:
            raise ValidationError(message='This entry accepts floating point numbers only!', cursor_position=0)


class NoAlphaValidator(Validator):
    def validate(self, document):
        text = document.text

        if text.lower() in (config.exit_entry, config.cancel_entry):
            pass
        elif text and text.isalpha():
            i = 0

            # Get index of first non numeric character.
            # We want to move the cursor here.
            for i, c in enumerate(text):
                if c.isalpha():
                    break

            raise ValidationError(message='This entry does not accept alphabet letters!', cursor_position=i)