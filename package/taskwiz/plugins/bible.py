"""
My Hand Bot Plugin - bible

read, compare or search the bible

[FUNCTION_CALL]
"""

try:
    import apsw
except:
    from taskwiz.utils.install import *
    installmodule(f"--upgrade apsw")
from taskwiz import config
import os, re, json, shutil
from prompt_toolkit import print_formatted_text, HTML
from taskwiz.utils.file_utils import FileUtil
from taskwiz.plugins.bibleTools.utils.TextUtil import TextUtil
from taskwiz.plugins.bibleTools.utils.BibleBooks import BibleBooks

def getBibleList(version=""):
    bibleFolder = os.path.join(config.bibleDataCurrent, "bibles")
    bibleList = FileUtil.fileNamesWithoutExtension(bibleFolder, "bible")
    if version in bibleList:
        config.mainText = version
    if not config.mainText in bibleList:
        config.mainText = "NET"
    return bibleList

def search_bible(function_args):
    terminal_width = shutil.get_terminal_size().columns
    # get the sql query statement
    query = function_args.get("query") # required
    version = function_args.get("version") # required
    allVersions = getBibleList(version)
    # exclude mainText from allVersions
    if config.mainText in allVersions:
        allVersions.remove(config.mainText)
    compare = function_args.get("compare") # required
    compareMode = (compare == "yes")
    versions = function_args.get("versions", "")
    if versions:
        try:
            compareVersions = eval(versions) if isinstance(versions, str) else versions
            compareVersions = [i for i in compareVersions if i in allVersions]
            if config.mainText in compareVersions:
                compareVersions.remove(config.mainText)
            if not compareVersions:
                compareVersions = allVersions
        except:
            compareVersions = allVersions
    else:
        compareVersions = allVersions
    # formulate a list of search words
    searchWordsRegex = [m for m in re.findall("Scripture REGEXP ['\"](.*?)['\"]", query)]
    searchWordsPlain = [m for m in re.findall("Scripture LIKE ['\"]%(.*?)%['\"]", query)]
    searchWords = searchWordsRegex + searchWordsPlain

    def highlightSearchResults(textContent):
        for eachString in searchWords:
            textContent = TextUtil.highlightSearchString(textContent, eachString)
        # fix highlighting
        textContent = TextUtil.fixTextHighlighting(textContent)
        return TextUtil.htmlToPlainText(textContent)
    def displaySingleVerse(bible, c, v, verseText):
        selectedBible = bible
        if searchWords:
            verseText = highlightSearchResults(verseText)
        verseText = verseText.strip()
        if bible == config.mainText and compareMode and compareVersions:
            bible = f"<{config.terminalPromptIndicatorColor2}>{bible}</{config.terminalPromptIndicatorColor2}>"
            verseText = f"<{config.terminalPromptIndicatorColor2}>{verseText}</{config.terminalPromptIndicatorColor2}>"
        bible = f"[{bible}] " if compareMode and compareVersions else ""
        thisVerse = f"<{config.terminalResourceLinkColor}>{c}:{v}</{config.terminalResourceLinkColor}> {verseText}"
        verseContent = f"{bible}{thisVerse}"
        if config.wrapWords and not selectedBible in config.noWordWrapBibles:
            verseContent = config.getWrappedHTMLText(verseContent, terminal_width)
        print_formatted_text(HTML(verseContent))
        config.addPagerText(verseContent)
        return thisVerse
    def getSingleVerse(bible, b, c, v):
        database = os.path.join(config.bibleDataCurrent, "bibles", f"{bible}.bible")
        if os.path.isfile(database):
            with apsw.Connection(database) as connection:
                cursor = connection.cursor()
                query = "SELECT * FROM Verses WHERE Book=? AND Chapter=? AND Verse=?"
                cursor.execute(query, (b, c, v))
                result = cursor.fetchone()
                if result:
                    return result if result[-1] else ()
                else:
                    return ()
        return ()

    addText = f"loading bible {config.mainText} ..."
    config.print(addText)
    config.addPagerText(addText)
    # display sql query statement for developer
    if config.developer:
        config.print(query)
        config.addPagerText(query)

    database = os.path.join(config.bibleDataCurrent, "bibles", f"{config.mainText}.bible")
    if os.path.isfile(database):
        config.tempContent = ""
        config.stopSpinning()
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
            config.print(config.divider)
            config.addPagerText(config.divider)
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
                    config.addPagerText(bookName)
                displaySingleVerse(config.mainText, c, v, verseText)
                config.tempContent += f"{c}:{v}\n"
                # thisVerse = displaySingleVerse(config.mainText, c, v, verseText)
                # config.tempContent += f"{thisVerse}\n"
                subTotal += 1
                # bible comparison
                if compareMode and compareVersions:
                    for bible in compareVersions:
                        singleVerse = getSingleVerse(bible, b, c, v)
                        if singleVerse:
                            _, c, v, verseText = getSingleVerse(bible, b, c, v)
                            displaySingleVerse(bible, c, v, verseText)
            # include statistics of the last book
            if bookName:
                total += subTotal
                bookName = re.sub("<u><b>|</b></u>", "", bookName)
                subTotals[bookName] = subTotal
            config.tempContent = re.sub("<[^<>]*?>", "", config.tempContent)
            config.print(config.divider)
            config.addPagerText(config.divider)
            for key, value in subTotals.items():
                addText = f"{key} x {value}"
                print_formatted_text(HTML(addText))
                config.addPagerText(addText)
            config.print(config.divider)
            config.addPagerText(config.divider)
            addText = f"Total: {total} verse(s)"
            print_formatted_text(HTML(addText))
            config.addPagerText(addText)
    return ""

# add bible books to input suggestions
config.inputSuggestions += [
    "go to ",
    "go to chapter ",
    "next chapter",
    "previous chapter",
    "search for verses that ",
    "enable comparison",
    "disable comparison",
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
    ("noWordWrapBibles", []), # some bibles display better, without word wrap feature, e.g. CUV
)
config.setConfig(persistentConfigs)
# temporary
temporaryConfigs = (
    ("runMode", "terminal"),
    ("bibleDataCurrent", config.bibleData if config.bibleData else os.path.join(config.myHandAIFolder, "plugins", "bibleTools", "bibleData")),
)
config.setConfig(temporaryConfigs, temporary=True)

bibleList = getBibleList()
functionSignature = {
    "name": "search_bible",
    "description": "read, compare or search the bible",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": """Formulate a sql query over a table created with statement "CREATE TABLE Verses (Book INT, Chapter INT, Verse INT, Scripture TEXT)".
The book numbers range from 1 to 66, corresponding to the canonical order from Genesis to Revevlation in the bible.
Give me only the sql query statement, starting with "SELECT * FROM Verses WHERE " without any extra explanation or comment.""",
            },
            "version": {
                "type": "string",
                "description": "Specify a bible version to read.  Answer 'XXX' if none is specified.",
                "enum": ['XXX'] + bibleList,
            },
            "compare": {
                "type": "string",
                "description": "Tell if comparison is intended. Answer 'no' if none is indicated.",
                "enum": ['yes', 'no'],
            },
            "versions": {
                "type": "string",
                "description": f"List of bible versions for comparison, e.g. {bibleList}",
            },
        },
        "required": ["query", "version", "compare"],
    },
}

# make available for function calling
config.pluginsWithFunctionCall.append("search_bible")
config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["search_bible"] = search_bible
