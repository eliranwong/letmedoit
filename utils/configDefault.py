import config, pprint

def setConfig():
    thisTranslation = {
        #'chat': 'Chat',
    }
    defaultSettings = (
        ('chatGPTApiModel', 'gpt-3.5-turbo'),
        ('chatGPTApiPredefinedContext', '[none]'),
        ('chatGPTApiCustomContext', ''),
        ('chatGPTApiMaxTokens', 4097),
        #('chatGPTApiNoOfChoices', 1),
        ('chatGPTApiTemperature', 0.8),
        ('chatGPTApiFunctionCall', "auto"),
        ('chatAfterFunctionCalled', True),
        ('runPythonScriptGlobally', False),
        ('openaiApiKey', ''),
        ('openaiApiOrganization', ''),
        ('loadingInternetSearches', "auto"),
        ('maximumInternetSearchResults', 5),
        ('chatGPTApiContextInAllInputs', False),
        ('thisTranslation', thisTranslation),
        ('chatGPTPluginExcludeList', []),
        ('terminalEnableTermuxAPI', False),
        ('terminalEnableTermuxAPIToast', False),
        ('terminal_cancel_action', '.quit'),
        ('terminalResourceLinkColor', 'ansiyellow'),
        ('terminalCommandEntryColor1', 'ansiyellow'),
        ('terminalPromptIndicatorColor1', 'ansimagenta'),
        ('terminalCommandEntryColor2', 'ansigreen'),
        ('terminalPromptIndicatorColor2', 'ansicyan'),
        ('terminalHeadingTextColor', 'ansigreen'),
        ('terminal_cancel_action', '.quit'),
        ('developer', False),
        ('pythonExecution', True),
        ('pythonExecutionConfirmation', True),
        ('pythonExecutionDisplay', False),
        ('autoUpdate', True),
        ('terminalEditorScrollLineCount', 10),
        ('terminalEditorTabText', "    "),
        ('blankEntryAction', "..."),
        ('defaultBlankEntryAction', ".context"),
        ('startupdirectory', ""),
    )
    for key, value in defaultSettings:
        if not hasattr(config, key):
            value = pprint.pformat(value)
            exec(f"""config.{key} = {value} """)
    for i in thisTranslation:
        if not i in config.thisTranslation:
            config.thisTranslation[i] = thisTranslation[i]

setConfig()