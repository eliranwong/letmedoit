# install package apsw if it is not available
from utils.install import *
try:
    import apsw
except:
    print("installing package 'apsw' ...")
    installmodule("--upgrade apsw")
    try:
        import apsw
    except:
        print("Install package 'apsw' first! Run:\n> source venv/bin/activate\n> 'pip3 install apsw'")

import config, os, re
from prompt_toolkit import print_formatted_text, HTML
from utils.file_utils import FileUtil
from plugins.bibleTools.utils.TextUtil import TextUtil
from plugins.bibleTools.utils.BibleBooks import BibleBooks

def getBibleList(version=""):
    bibleFolder = os.path.join(config.bibleDataCurrent, "bibles")
    bibleList = FileUtil.fileNamesWithoutExtension(bibleFolder, "bible")
    if version in bibleList:
        config.mainText = version
    if not config.mainText in bibleList:
        config.mainText = "NET"
    return bibleList

def search_bible(function_args):
    # get the sql query statement
    query = function_args.get("query") # required
    version = function_args.get("version")
    getBibleList(version)
    # formulate a list of search words
    searchWordsRegex = [m for m in re.findall("Scripture REGEXP ['\"](.*?)['\"]", query, flags=0 if config.enableCaseSensitiveSearch else re.IGNORECASE)]
    searchWordsPlain = [m for m in re.findall("Scripture LIKE ['\"]%(.*?)%['\"]", query, flags=0 if config.enableCaseSensitiveSearch else re.IGNORECASE)]
    searchWords = searchWordsRegex + searchWordsPlain

    def highlightSearchResults(textContent):
        for eachString in searchWords:
            textContent = TextUtil.highlightSearchString(textContent, eachString)
        # fix highlighting
        textContent = TextUtil.fixTextHighlighting(textContent)
        return TextUtil.htmlToPlainText(textContent)

    print(f"loading bible {config.mainText} ...")
    # display sql query statement for developer
    if config.developer:
        print(query)

    database = os.path.join(config.bibleDataCurrent, "bibles", f"{config.mainText}.bible")
    if os.path.isfile(database):
        config.tempContent = ""
        with apsw.Connection(database) as connection:
            # support regular expression
            connection.createscalarfunction("REGEXP", TextUtil.regexp)
            cursor = connection.cursor()
            # support case sensitive search in query prefix
            cursor.execute(TextUtil.getQueryPrefix()+query)
            if not query.lower().startswith("select * from verses where"):
                results = cursor.fetchall()
                # return information, e.g. how many chapters in Genesis
                return json.dumps(results)
            book = 0
            bookName = ""
            total = 0
            subTotal = 0
            subTotals = {}
            print("--------------------")
            for b, c, v, verseText in cursor.fetchall():
                config.mainB, config.mainC, config.mainV = b, c, v
                if not book == b:
                    if not book == 0 and bookName:
                        total += subTotal
                        bookName = re.sub("<u><b>|</b></u>", "", bookName)
                        subTotals[bookName] = subTotal
                        subTotal = 0
                    book = b
                    bookName = abbrev[str(b)][-1]
                    config.tempContent += f"{bookName}\n"
                    bookName = f"<u><b><{config.terminalHeadingTextColor}>{bookName}</{config.terminalHeadingTextColor}></b></u>"
                    print_formatted_text(HTML(bookName))
                if searchWords:
                    verseText = highlightSearchResults(verseText)
                thisVerse = f"<{config.terminalResourceLinkColor}>{c}:{v}</{config.terminalResourceLinkColor}> {verseText.strip()}"
                print_formatted_text(HTML(thisVerse))
                config.tempContent += f"{thisVerse}\n"
                subTotal += 1
            # include statistics of the last book
            if bookName:
                total += subTotal
                bookName = re.sub("<u><b>|</b></u>", "", bookName)
                subTotals[bookName] = subTotal
            config.tempContent = re.sub("<[^<>]*?>", "", config.tempContent)
            print("--------------------")
            for key, value in subTotals.items():
                print_formatted_text(HTML(f"{key} x {value}"))
            print("--------------------")
            print_formatted_text(HTML(f"Total: {total} verse(s)"))
    return ""

# add bible books to input suggestions
config.inputSuggestions += [
    "next chapter",
    "previous chapter",
    "go to chapter "
]
abbrev = BibleBooks.abbrev["eng"]
for i in abbrev:
    abb, fullname = abbrev[i]
    if abb:
        config.inputSuggestions += [abb, fullname]
# configs particular to this plugin
# persistent
persistentConfigs = (
    ("mainText", "NET"),
    ("mainB", 43),
    ("mainC", 3),
    ("mainV", 16),
    ("bibleData", ""),
    ("enableCaseSensitiveSearch", False),
)
config.setConfig(persistentConfigs)
# temporary
temporaryConfigs = (
    ("runMode", "terminal"),
    ("bibleDataCurrent", config.bibleData if config.bibleData else os.path.join(config.myHandAIFolder, "plugins", "bibleTools", "bibleData")),
)
config.setConfig(temporaryConfigs, temporary=True)

functionSignature = {
    "name": "search_bible",
    "description": "read or search the bible",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": """Formulate a sql query over a table created with statement "CREATE TABLE Verses (Book INT, Chapter INT, Verse INT, Scripture TEXT)".
The book numbers range from 1 to 66, corresponding to the canonical order from Genesis to Revevlation in the bible.
Remember, when you are provided with bible references, e.g. John 3:16; Rm 5:8, parse them to get corresponding Book, Chapter and Verse numbers.
Also, in case regular expression is specified, it is expressed as (Scripture REGEXP ?).
Give me only the sql query statement, starting with "SELECT * FROM Verses WHERE " without any extra explanation or comment.""",
            },
            "version": {
                "type": "string",
                "description": "Specify a bible version to read.  Answer 'XXX' if none is specified.",
                "enum": ['XXX'] + getBibleList(),
            },
        },
        "required": ["query", "version"],
    },
}

# make available for function calling
config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["search_bible"] = search_bible