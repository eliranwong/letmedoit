import config, pprint

def setConfig(defaultSettings, thisTranslation={}, temporary=False):
    for key, value in defaultSettings:
        if not hasattr(config, key):
            value = pprint.pformat(value)
            exec(f"""config.{key} = {value} """)
            if temporary:
                config.excludeConfigList.append(key)
    if thisTranslation:
        for i in thisTranslation:
            if not i in config.thisTranslation:
                config.thisTranslation[i] = thisTranslation[i]

defaultSettings = (
    ('chatGPTApiModel', 'gpt-3.5-turbo'),
    ('chatGPTApiPredefinedContext', '[none]'),
    ('chatGPTApiPredefinedContextLast', '[none]'),
    ('chatGPTApiCustomContext', ''),
    ('chatGPTApiMaxTokens', 2000),
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
    ('thisTranslation', {}),
    ('chatGPTPluginExcludeList', ["counselling"]),
    ('terminalEnableTermuxAPI', False),
    ('terminalEnableTermuxAPIToast', False),
    ('cancel_entry', '.cancel'),
    ('exit_entry', '.quit'),
    ('terminalHeadingTextColor', 'ansigreen'),
    ('terminalResourceLinkColor', 'ansiyellow'),
    ('terminalCommandEntryColor1', 'ansiyellow'),
    ('terminalPromptIndicatorColor1', 'ansimagenta'),
    ('terminalCommandEntryColor2', 'ansigreen'),
    ('terminalPromptIndicatorColor2', 'ansicyan'),
    ('terminalSearchHighlightBackground', 'ansiblue'),
    ('terminalSearchHighlightForeground', 'ansidefault'),
    ('developer', False),
    ('enhanceCommandExecution', True),
    ('confirmExecution', "always"), # 'always', 'high_risk_only', 'medium_risk_or_above', 'none'
    ('codeDisplay', False),
    ('autoUpdate', True),
    ('terminalEditorScrollLineCount', 10),
    ('terminalEditorTabText', "    "),
    ('blankEntryAction', "..."),
    ('defaultBlankEntryAction', ".context"),
    ('startupdirectory', ""),
    ('suggestSystemCommand', True),
    ('displayImprovedWriting', False),
    ('improvedWritingSytle', 'standard English'), # e.g. British spoken English
    ('ttsInput', False),
    ('ttsOutput', False),
    ('vlcSpeed', 1.0),
    ('gttsLang', "en"), # gTTS is used by default if ttsCommand is not given
    ('gttsTld', ""), # https://gtts.readthedocs.io/en/latest/module.html#languages-gtts-lang
    ('ttsCommand', ""), # ttsCommand is used if it is given; offline tts engine runs faster; on macOS [suggested speak rate: 100-300], e.g. "say -r 200 -v Daniel"; on Ubuntu [espeak; speed in approximate words per minute; 175 by default], e.g. "espeak -s 175 -v {1}"
    ('ttsCommandSuffix', ""), # try on Windows; ttsComand = '''Add-Type -TypeDefinition 'using System.Speech.Synthesis; class TTS { static void Main(string[] args) { using (SpeechSynthesizer synth = new SpeechSynthesizer()) { synth.Speak(args[0]); } } }'; [TTS]::Main('''; ttsCommandSuffix = ")"; a full example is Add-Type -TypeDefinition 'using System.Speech.Synthesis; class TTS { static void Main(string[] args) { using (SpeechSynthesizer synth = new SpeechSynthesizer()) { synth.Speak(args[0]); } } }'; [TTS]::Main("Text to be read")
)

setConfig(defaultSettings)
# allow plugins to add customised config
# e.g. check plugins/bible.py
config.setConfig = setConfig
