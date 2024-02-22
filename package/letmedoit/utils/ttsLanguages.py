class TtsLanguages:

    # voices for reference

    # package gtts languages
    # gtts-cli --all
    gtts = {
        "Afrikaans": "af",
        "Arabic": "ar",
        "Bulgarian": "bg",
        "Bengali": "bn",
        "Bosnian": "bs",
        "Catalan": "ca",
        "Czech": "cs",
        "Welsh": "cy",
        "Danish": "da",
        "German": "de",
        "Greek": "el",
        "English": "en",
        "Esperanto": "eo",
        "Spanish": "es",
        "Estonian": "et",
        "Finnish": "fi",
        "French": "fr",
        "Gujarati": "gu",
        "Hebrew": "he",
        "Hindi": "hi",
        "Croatian": "hr",
        "Hungarian": "hu",
        "Armenian": "hy",
        "Indonesian": "id",
        "Icelandic": "is",
        "Italian": "it",
        "Japanese": "ja",
        "Javanese": "jw",
        "Khmer": "km",
        "Kannada": "kn",
        "Korean": "ko",
        "Latin": "la",
        "Latvian": "lv",
        "Macedonian": "mk",
        "Malayalam": "ml",
        "Marathi": "mr",
        "Myanmar (Burmese)": "my",
        "Nepali": "ne",
        "Dutch": "nl",
        "Norwegian": "no",
        "Polish": "pl",
        "Portuguese": "pt",
        "Romanian": "ro",
        "Russian": "ru",
        "Sinhala": "si",
        "Slovak": "sk",
        "Albanian": "sq",
        "Serbian": "sr",
        "Sundanese": "su",
        "Swedish": "sv",
        "Swahili": "sw",
        "Tamil": "ta",
        "Telugu": "te",
        "Thai": "th",
        "Filipino": "tl",
        "Turkish": "tr",
        "Ukrainian": "uk",
        "Urdu": "ur",
        "Vietnamese": "vi",
        "Mandarin": "zh",
    }

    # official google cloud text-to-speech voices
    # https://cloud.google.com/text-to-speech/docs/voices
    gctts = {
        "Afrikaans (South Africa)": "af-ZA",
        "Arabic": "ar-XA",
        "Basque (Spain)": "eu-ES",
        "Bengali (India)": "bn-IN",
        "Bulgarian (Bulgaria)": "bg-BG",
        "Catalan (Spain)": "ca-ES",
        "Chinese (Hong Kong)": "yue-HK",
        "Czech (Czech Republic)": "cs-CZ",
        "Danish (Denmark)": "da-DK",
        "Dutch (Belgium)": "nl-BE",
        "Dutch (Netherlands)": "nl-NL",
        "English (Australia)": "en-AU",
        "English (India)": "en-IN",
        "English (UK)": "en-GB",
        "English (US)": "en-US",
        "Filipino (Philippines)": "fil-PH",
        "Finnish (Finland)": "fi-FI",
        "French (Canada)": "fr-CA",
        "French (France)": "fr-FR",
        "Galician (Spain)": "gl-ES",
        "German (Germany)": "de-DE",
        "Greek (Greece)": "el-GR",
        "Gujarati (India)": "gu-IN",
        "Hebrew (Israel)": "he-IL",
        "Hindi (India)": "hi-IN",
        "Hungarian (Hungary)": "hu-HU",
        "Icelandic (Iceland)": "is-IS",
        "Indonesian (Indonesia)": "id-ID",
        "Italian (Italy)": "it-IT",
        "Japanese (Japan)": "ja-JP",
        "Kannada (India)": "kn-IN",
        "Korean (South Korea)": "ko-KR",
        "Latvian (Latvia)": "lv-LV",
        "Lithuanian (Lithuania)": "lt-LT",
        "Malay (Malaysia)": "ms-MY",
        "Malayalam (India)": "ml-IN",
        "Mandarin Chinese": "cmn-CN",
        "Mandarin Chinese": "cmn-TW",
        "Marathi (India)": "mr-IN",
        "Norwegian (Norway)": "nb-NO",
        "Polish (Poland)": "pl-PL",
        "Portuguese (Brazil)": "pt-BR",
        "Portuguese (Portugal)": "pt-PT",
        "Punjabi (India)": "pa-IN",
        "Romanian (Romania)": "ro-RO",
        "Russian (Russia)": "ru-RU",
        "Serbian (Cyrillic)": "sr-RS",
        "Slovak (Slovakia)": "sk-SK",
        "Spanish (Spain)": "es-ES",
        "Spanish (US)": "es-US",
        "Swedish (Sweden)": "sv-SE",
        "Tamil (India)": "ta-IN",
        "Telugu (India)": "te-IN",
        "Thai (Thailand)": "th-TH",
        "Turkish (Turkey)": "tr-TR",
        "Ukrainian (Ukraine)": "uk-UA",
        "Vietnamese (Vietnam)": "vi-VN",
    }

    # espeak --voices
    espeak = {
        "af": ("af", "afrikaans", "other/af"),
        "an": ("an", "aragonese", "europe/an"),
        "bg": ("bg", "bulgarian", "europe/bg"),
        "bs": ("bs", "bosnian", "europe/bs"),
        "ca": ("ca", "catalan", "europe/ca"),
        "cs": ("cs", "czech", "europe/cs"),
        "cy": ("cy", "welsh", "europe/cy"),
        "da": ("da", "danish", "europe/da"),
        "de": ("de", "german", "de"),
        # espeak el voice cannot read accented Greek words
        "el": ("el", "greek", "europe/el"),
        # To read accented Greek words, use grc instead of el
        "grc": ("grc", "greek-ancient", "other/grc"),
        #"en": ("en", "default", "default"),
        "en": ("en", "english", "default"),
        #"en-gb": ("en-gb", "english", "en"),
        "en-gb": ("en-gb", "english-gb", "en"),
        "en-sc": ("en-sc", "en-scottish", "other/en-sc"),
        "en-uk-north": ("en-uk-north", "english-north", "other/en-n"),
        "en-uk-rp": ("en-uk-rp", "english_rp", "other/en-rp"),
        "en-uk-wmids": ("en-uk-wmids", "english_wmids", "other/en-wm"),
        "en-us": ("en-us", "english-us", "en-us"),
        "en-wi": ("en-wi", "en-westindies", "other/en-wi"),
        "eo": ("eo", "esperanto", "other/eo"),
        "es": ("es", "spanish", "europe/es"),
        "es-la": ("es-la", "spanish-latin-am", "es-la"),
        "et": ("et", "estonian", "europe/et"),
        "fa": ("fa", "persian", "asia/fa"),
        "fa-pin": ("fa-pin", "persian-pinglish", "asia/fa-pin"),
        "fi": ("fi", "finnish", "europe/fi"),
        "fr-be": ("fr-be", "french-Belgium", "europe/fr-be"),
        "fr": ("fr-fr", "french", "fr"),
        "ga": ("ga", "irish-gaeilge", "europe/ga"),
        "hi": ("hi", "hindi", "asia/hi"),
        "hr": ("hr", "croatian", "europe/hr"),
        "hu": ("hu", "hungarian", "europe/hu"),
        "hy": ("hy", "armenian", "asia/hy"),
        "hy-west": ("hy-west", "armenian-west", "asia/hy-west"),
        "id": ("id", "indonesian", "asia/id"),
        "is": ("is", "icelandic", "europe/is"),
        "it": ("it", "italian", "europe/it"),
        "jbo": ("jbo", "lojban", "other/jbo"),
        "ka": ("ka", "georgian", "asia/ka"),
        "kn": ("kn", "kannada", "asia/kn"),
        "ku": ("ku", "kurdish", "asia/ku"),
        "la": ("la", "latin", "other/la"),
        "lfn": ("lfn", "lingua_franca_nova", "other/lfn"),
        "lt": ("lt", "lithuanian", "europe/lt"),
        "lv": ("lv", "latvian", "europe/lv"),
        "mk": ("mk", "macedonian", "europe/mk"),
        "ml": ("ml", "malayalam", "asia/ml"),
        "ms": ("ms", "malay", "asia/ms"),
        "ne": ("ne", "nepali", "asia/ne"),
        "nl": ("nl", "dutch", "europe/nl"),
        "no": ("no", "norwegian", "europe/no"),
        "pa": ("pa", "punjabi", "asia/pa"),
        "pl": ("pl", "polish", "europe/pl"),
        "pt-br": ("pt-br", "brazil", "pt"),
        "pt": ("pt-pt", "portugal", "europe/pt-pt"),
        "ro": ("ro", "romanian", "europe/ro"),
        "ru": ("ru", "russian", "europe/ru"),
        "sk": ("sk", "slovak", "europe/sk"),
        "sq": ("sq", "albanian", "europe/sq"),
        "sr": ("sr", "serbian", "europe/sr"),
        "sv": ("sv", "swedish", "europe/sv"),
        "sw": ("sw", "swahili-test", "other/sw"),
        "ta": ("ta", "tamil", "asia/ta"),
        "tr": ("tr", "turkish", "asia/tr"),
        "vi": ("vi", "vietnam", "asia/vi"),
        "vi-hue": ("vi-hue", "vietnam_hue", "asia/vi-hue"),
        "vi-sgn": ("vi-sgn", "vietnam_sgn", "asia/vi-sgn"),
        "zh-cn": ("zh", "mandarin", "asia/zh"),
        "zh-tw": ("zh-yue", "cantonese", "asia/zh-yue"),
        "yue": ("zh-yue", "cantonese", "asia/zh-yue"),
        "he": ("he", "hebrew", "he"),
    }