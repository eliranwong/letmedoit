# install package apsw if it is not available
import os
try:
    import apsw
except:
    print("installing package 'apsw' ...")
    os.system("pip3 install apsw")
    import apsw
# continue only if apsw is installed
import config, re
from plugins.bibleTools.utils.BibleBooks import BibleBooks
from plugins.bibleTools.utils.TextUtil import TextUtil
from prompt_toolkit import print_formatted_text, HTML

def search_bible(function_args):
    # get the sql query statement
    query = function_args.get("query") # required
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

    print("loading bible ...")
    if config.developer:
        print(query)

    database = os.path.join(config.biblelData if config.biblelData else os.path.join(config.myHandAIFolder, "plugins", "bibleTools", "bibleData"), "bibles", "NET.bible")
    if os.path.isfile(database):
        config.tempContent = ""
        with apsw.Connection(database) as connection:
            # support regular expression
            connection.createscalarfunction("REGEXP", TextUtil.regexp)
            cursor = connection.cursor()
            # support case sensitive search in query prefix
            cursor.execute(TextUtil.getQueryPrefix()+query)
            abbrev = BibleBooks.abbrev["eng"]
            book = 0
            bookName = ""
            total = 0
            subTotal = 0
            subTotals = {}
            print("--------------------")
            for b, c, v, verseText in cursor.fetchall():
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
            config.tempContent = re.sub("<[^<>]*?>", "", config.tempContent)
            print("--------------------")
            for key, value in subTotals.items():
                print_formatted_text(HTML(f"{key} x {value}"))
            print("--------------------")
            print_formatted_text(HTML(f"Total: {total} verse(s)"))
    return ""

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
Also, regular expression is expressed as (Scripture REGEXP ?).
Give me only the sql query statement, starting with "SELECT * FROM Verses WHERE " without any extra explanation or comment.""",
            },
        },
        "required": ["query"],
    },
}

# configs particular to this plugin
# temporary
temporaryConfigs = (
    ("runMode", "terminal"),
)
config.setConfig(temporaryConfigs, temporary=True)
# persistent
persistentConfigs = (
    ("biblelData", ""),
    ("enableCaseSensitiveSearch", False),
)
config.setConfig(persistentConfigs)

# make available for function calling
config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["search_bible"] = search_bible