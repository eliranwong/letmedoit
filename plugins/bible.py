import config, os, re
try:
    import apsw
except:
    os.system("pip3 install apsw")
    import apsw
from plugins.bibleTools.utils.BibleBooks import BibleBooks
from plugins.bibleTools.utils.TextUtil import TextUtil
from prompt_toolkit import print_formatted_text, HTML

def search_bible(function_args):
    # get the sql query statement
    query = function_args.get("query") # required
    # formulate a list of search words
    searchWords = [m for m in re.findall("LIKE ['\"]%(.*?)%['\"]", query, flags=0 if config.enableCaseSensitiveSearch else re.IGNORECASE)]
    searchWords = [m.split("%") for m in searchWords]
    searchWords = [m2 for m1 in searchWords for m2 in m1]

    def highlightSearchResults(textContent):
        for eachString in searchWords:
            textContent = TextUtil.highlightSearchString(textContent, eachString)
        # fix highlighting
        textContent = TextUtil.fixTextHighlighting(textContent)
        return TextUtil.htmlToPlainText(textContent)

    print("loading bible ...")
    print(query)

    database = os.path.join(config.biblelData if config.biblelData else os.path.join(config.myHandAIFolder, "plugins", "bibleTools", "bibleData"), "bibles", "NET.bible")
    if os.path.isfile(database):
        config.tempContent = ""
        with apsw.Connection(database) as connection:
            connection.createscalarfunction("REGEXP", TextUtil.regexp)
            cursor = connection.cursor()
            cursor.execute(TextUtil.getQueryPrefix()+query)
            abbrev = BibleBooks.abbrev["eng"]
            book = 0
            print("--------------------")
            for b, c, v, verseText in cursor.fetchall():
                if not book == b:
                    book = b
                    bookName = abbrev[str(b)][-1]
                    bookName = f"<u><b><{config.terminalHeadingTextColor}>{bookName}</{config.terminalHeadingTextColor}></b></u>"
                    print_formatted_text(HTML(bookName))
                verseText = highlightSearchResults(verseText)
                thisVerse = f"<{config.terminalResourceLinkColor}>{c}:{v}</{config.terminalResourceLinkColor}> {verseText.strip()}"
                print_formatted_text(HTML(thisVerse))
                config.tempContent += thisVerse
            print("--------------------")
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
Give me only the sql query statement, starting with "SELECT * FROM Verses WHERE " without any extra explanation or comment.""",
            },
        },
        "required": ["query"],
    },
}

config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["search_bible"] = search_bible