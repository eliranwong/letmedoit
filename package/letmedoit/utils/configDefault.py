from letmedoit import config
import pprint, re, os, shutil, sys, subprocess, platform
from prompt_toolkit.shortcuts import yes_no_dialog

def loadConfig(configPath):
    with open(configPath, "r", encoding="utf-8") as fileObj:
        configs = fileObj.read()
    configs = "from letmedoit import config\n" + re.sub("^([A-Za-z])", r"config.\1", configs, flags=re.M)
    exec(configs, globals())
config.loadConfig = loadConfig

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

def isPackageInstalled(package):
    return True if shutil.which(package.split(" ", 1)[0]) else False

pluginExcludeList = [
    "awesome prompts",
    "counselling",
    "edit text",
    "simplified Chinese to traditional Chinese",
]
if config.isTermux:
    pluginExcludeList += [
        "analyze files",
        "analyze web content",
        "ask codey",
        "ask gemini pro",
        "ask palm2",
        "create ai assistants",
        "create statistical graphics",
        "dates and times",
        "memory",
        "remove image background",
        "solve math problems",
        "search chat records",
        "check pyaudio",
    ]

defaultSettings = (
    ('includeIpInSystemMessage', False),
    ('translateToLanguage', ''),
    ('dynamicTokenCount', False),
    ('use_oai_assistant', False), # support OpenAI Assistants API in AutoGen Agent Builder
    ('max_agents', 5), # maximum number of agents build manager can create.
    ('max_group_chat_round', 12), # AutoGen group chat maximum round
    ('env_QT_QPA_PLATFORM_PLUGIN_PATH', ''), # e.g. # deal with error: qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "~/apps/letmedoit/lib/python3.10/site-packages/cv2/qt/plugins" even though it was found.
    ('systemMessage_letmedoit', ''), # letmedoit system message
    ('systemMessage_chatgpt', 'You are a helpful assistant.'), # system message for standalone chatgpt chatbot
    ('systemMessage_geminipro', 'You are a helpful assistant.'), # system message for standalone geminipro chatbot
    ('systemMessage_palm2', 'You are a helpful assistant.'), # system message for standalone palm2 chatbot
    ('systemMessage_codey', 'You are an expert on coding.'), # system message for standalone codey chatbot
    ('embeddingModel', 'paraphrase-multilingual-mpnet-base-v2'), # reference: https://www.sbert.net/docs/pretrained_models.html
    ('historyParentFolder', ""),
    ('customTextEditor', ""), # e.g. 'micro -softwrap true -wordwrap true'; built-in text editor eTextEdit is used when it is not defined.
    ('pagerView', False),
    ('usePygame', False),
    ('wrapWords', True),
    ('mouseSupport', False),
    ('autoUpgrade', True),
    ('chatbot', 'chatgpt'),
    ('chatGPTApiModel', 'gpt-3.5-turbo-16k'),
    ('chatGPTApiMaxTokens', 4000),
    ('chatGPTApiMinTokens', 256),
    #('chatGPTApiNoOfChoices', 1),
    ('chatGPTApiFunctionCall', "auto"),
    ('passFunctionCallReturnToChatGPT', True),
    ('llmTemperature', 0.8),
    ('max_consecutive_auto_reply', 10), # work with pyautogen
    ('memoryClosestMatches', 5),
    ('chatRecordClosestMatches', 5),
    ('runPythonScriptGlobally', False),
    ('openaiApiKey', ''),
    ('openaiApiOrganization', ''),
    ('loadingInternetSearches', "auto"),
    ('maximumInternetSearchResults', 5),
    ('predefinedContext', '[none]'),
    ('customPredefinedContext', ''),
    ('applyPredefinedContextAlways', False), # True: apply predefined context with all use inputs; False: apply predefined context only in the beginning of the conversation
    ('thisTranslation', {}),
    ('terminalEnableTermuxAPI', True if config.isTermux and isPackageInstalled("termux-open-url") else False),
    ('terminalEnableTermuxAPIToast', False),
    ('pluginExcludeList', pluginExcludeList),
    ('cancel_entry', '.cancel'),
    ('exit_entry', '.exit'),
    ('terminalHeadingTextColor', 'ansigreen'),
    ('terminalResourceLinkColor', 'ansiyellow'),
    ('terminalCommandEntryColor1', 'ansiyellow'),
    ('terminalPromptIndicatorColor1', 'ansimagenta'),
    ('terminalCommandEntryColor2', 'ansigreen'),
    ('terminalPromptIndicatorColor2', 'ansicyan'),
    ('terminalSearchHighlightBackground', 'ansiblue'),
    ('terminalSearchHighlightForeground', 'ansidefault'),
    ('pygments_style', ''),
    ('developer', False),
    #('enhanceCommandExecution', False),
    ('confirmExecution', "always"), # 'always', 'high_risk_only', 'medium_risk_or_above', 'none'
    ('codeDisplay', False),
    ('terminalEditorScrollLineCount', 20),
    ('terminalEditorTabText', "    "),
    ('blankEntryAction', "..."),
    ('defaultBlankEntryAction', ".context"),
    ('storagedirectory', ""),
    ('suggestSystemCommand', True),
    ('displayImprovedWriting', False),
    ('improvedWritingSytle', 'standard English'), # e.g. British spoken English
    ('ttsInput', False),
    ('ttsOutput', False),
    ('vlcSpeed', 1.0),
    ('gcttsLang', "en-GB"),
    ('gcttsSpeed', 1.0),
    ('gttsLang', "en"), # gTTS is used by default if ttsCommand is not given
    ('gttsTld', ""), # https://gtts.readthedocs.io/en/latest/module.html#languages-gtts-lang
    ('ttsCommand', ""), # ttsCommand is used if it is given; offline tts engine runs faster; on macOS [suggested speak rate: 100-300], e.g. "say -r 200 -v Daniel"; on Ubuntu [espeak; speed in approximate words per minute; 175 by default], e.g. "espeak -s 175 -v en"; remarks: always place the voice option, if any, at the end
    ('ttsCommandSuffix', ""), # try on Windows; ttsComand = '''Add-Type -TypeDefinition 'using System.Speech.Synthesis; class TTS { static void Main(string[] args) { using (SpeechSynthesizer synth = new SpeechSynthesizer()) { synth.Speak(args[0]); } } }'; [TTS]::Main('''; ttsCommandSuffix = ")"; a full example is Add-Type -TypeDefinition 'using System.Speech.Synthesis; class TTS { static void Main(string[] args) { using (SpeechSynthesizer synth = new SpeechSynthesizer()) { synth.Speak(args[0]); } } }'; [TTS]::Main("Text to be read")
    ("ttsLanguages", ["en", "en-gb", "en-us", "zh", "yue", "el"]), # users can edit this item in config.py to support more or less languages
    ("ttsLanguagesCommandMap", {"en": "", "en-gb": "", "en-us": "", "zh": "", "yue": "", "el": "",}), # advanced users need to edit this item manually to support different voices with customised tts command, e.g. ttsCommand set to "say -r 200 -v Daniel" and ttsLanguagesCommandMap set to {"en": "Daniel", "en-gb": "Daniel", "en-us": "", "zh": "", "yue": "", "el": "",}
    ("openweathermapApi", ""),
    ("pyaudioInstalled", False),
    ("voiceTypingModel", "google"),
    ("voiceTypingLanguage", "en-US"),
    ("voiceTypingAdjustAmbientNoise", False),
    ("keyBinding_exit", ["c-q"]),
    ("keyBinding_cancel", ["c-z"]),
    ("keyBinding_insert_path", ["c-i"]),
    ("keyBinding_new", ["c-n"]),
    ("keyBinding_newline", ["escape", "enter"]),
    ("keyBinding_remove_context_temporarily", ["c-y"]),
    ("keyBinding_export", ["c-s"]),
    ("keyBinding_display_device_info", ["escape", "i"]),
    ("keyBinding_count_tokens", ["escape", "c"]),
    ("keyBinding_launch_pager_view", ["c-g"]),
    ("keyBinding_toggle_developer_mode", ["escape", "d"]),
    ("keyBinding_toggle_multiline_entry", ["escape", "l"]),
    ("keyBinding_list_directory_content", ["c-l"]),
    ("keyBinding_select_context", ["c-o"]),
    ("keyBinding_launch_system_prompt", ["escape", "t"]),
    ("keyBinding_voice_entry", ["c-f"]),
    ("keyBinding_voice_entry_config", ["escape", "f"]),
    ("keyBinding_display_key_combo", ["c-k"]),
    ("keyBinding_toggle_input_audio", ["c-b"]),
    ("keyBinding_toggle_response_audio", ["c-p"]),
    ("keyBinding_restart_app", ["escape", "r"]),
    ("keyBinding_toggle_writing_improvement", ["escape", "w"]),
    ("keyBinding_toggle_word_wrap", ["c-w"]),
    ("keyBinding_toggle_mouse_support", ["escape", "m"]),
    ("keyBinding_edit_last_response", ["escape", "p"]),
    ("keyBinding_edit_current_entry", ["c-e"]),
    ("keyBinding_swap_text_brightness", ["escape", "s"]),
)

storageDir = config.getStorageDir()
if os.path.isdir(storageDir):
    configFile = os.path.join(config.letMeDoItAIFolder, "config.py")
    if os.path.getsize(configFile) == 0:
        # It means that it is either a newly installed copy or an upgraded copy
        
        # delete old shortcut files so that newer versions of shortcuts can be created
        appName = config.letMeDoItName.split()[0]
        shortcutFiles = (f"{appName}.bat", f"{appName}.command", f"{appName}.desktop", f"{appName}Tray.bat", f"{appName}Tray.command", f"{appName}Tray.desktop")
        for shortcutFile in shortcutFiles:
            shortcut = os.path.join(config.letMeDoItAIFolder, shortcutFile)
            if os.path.isfile(shortcut):
                os.remove(shortcut)
        # delete system tray shortcuts
        shortcut_dir = os.path.join(config.letMeDoItAIFolder, "shortcuts")
        shutil.rmtree(shortcut_dir, ignore_errors=True)

        # check if config backup is available
        backupFile = os.path.join(storageDir, "config_backup.py")
        if os.path.isfile(backupFile):
            restore_backup = yes_no_dialog(
                title="Configuration Backup Found",
                text=f"Do you want to use the following backup?\n{backupFile}"
            ).run()
            if restore_backup:
                try:
                    loadConfig(backupFile)
                    shutil.copy(backupFile, configFile)
                    print("Configuration backup restored!")
                    #config.restartApp()
                except:
                    print("Failed to restore backup!")
setConfig(defaultSettings)
# allow plugins to add customised config
# read https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Work-with-LetMeDoIt-AI-Configurations#example
config.setConfig = setConfig
