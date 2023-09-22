import config, pprint

def setConfig():
    thisTranslation = {
        #'chat': 'Chat',
    }
    defaultSettings = (
        ('chatGPTApiModel', 'gpt-3.5-turbo'),
        ('chatGPTApiPredefinedContext', '[none]'),
        ('chatGPTApiCustomContext', ''),
        ('chatGPTApiMaxTokens', 2048),
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
        ('terminalCommandEntryColor2', 'ansigreen'),
        ('terminalPromptIndicatorColor2', 'ansicyan'),
        ('terminal_cancel_action', '.quit'),
        ('developer', False),
        ('enhancedScreening', True),
        ('autoUpdate', True),
    )
    for key, value in defaultSettings:
        if not hasattr(config, key):
            value = pprint.pformat(value)
            exec(f"""config.{key} = {value} """)
    for i in thisTranslation:
        if not i in config.thisTranslation:
            config.thisTranslation[i] = thisTranslation[i]

setConfig()