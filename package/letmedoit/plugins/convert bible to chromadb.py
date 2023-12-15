"""
LetMeDoIt AI Plugin - convert bible to chromadb format

convert UniqueBible App *.bible sql file to chromadb format

[FUNCTION_CALL]
"""

try:
    import apsw
except:
    from letmedoit.utils.install import *
    installmodule(f"--upgrade apsw")
from letmedoit import config
from letmedoit.utils.file_utils import FileUtil
from letmedoit.plugins.bibleTools.utils.BibleBooks import BibleBooks
from letmedoit.health_check import HealthCheck
import uuid, os, chromadb
from pathlib import Path
from prompt_toolkit.shortcuts import ProgressBar


def getBibleList(version=""):
    bibleFolder = os.path.join(config.bibleDataCurrent, "bibles")
    bibleList = FileUtil.fileNamesWithoutExtension(bibleFolder, "bible")
    if version in bibleList:
        config.mainText = version
    if not config.mainText in bibleList:
        config.mainText = "NET"
    return bibleList

def convert_bible(function_args):
    # get the bible version
    version = function_args.get("version") # required
    def getAllVerses(bible=version):
        database = os.path.join(config.bibleDataCurrent, "bibles", f"{bible}.bible")
        if os.path.isfile(database):
            with apsw.Connection(database) as connection:
                cursor = connection.cursor()
                query = "SELECT * FROM Verses ORDER BY Book, Chapter, Verse"
                cursor.execute(query)
                allVerses = cursor.fetchall()
                return allVerses
        return ()

    # database path
    dbpath = os.path.join(config.getFiles(), "bibles", version)
    if os.path.isdir(dbpath):
        config.print3(f"Database exists: {dbpath}")
        return "Aborted!"
    Path(dbpath).mkdir(parents=True, exist_ok=True)
    # client
    chroma_client = chromadb.PersistentClient(dbpath)
    # collection
    collection = chroma_client.get_or_create_collection(
        name="verses",
        metadata={"hnsw:space": "cosine"},
        embedding_function=HealthCheck.getEmbeddingFunction(embeddingModel="all-mpnet-base-v2"),
    )
    with ProgressBar() as pb:
        for book, chapter, verse, scripture in pb(getAllVerses()):
            abbrev = BibleBooks.abbrev["eng"]
            book_abbr = abbrev[str(book)][0]
            metadata = {
                "book_abbr": book_abbr,
                "book": book,
                "chapter": chapter,
                "verse": verse,
            }
            id = str(uuid.uuid4())
            collection.add(
                documents = [scripture],
                metadatas = [metadata],
                ids = [id]
            )
    return "Done!"

if not "bible" in config.pluginExcludeList:

    bibleList = getBibleList()
    functionSignature = {
        "name": "convert_bible",
        "description": "convert bible to chromadb database format",
        "parameters": {
            "type": "object",
            "properties": {
                "version": {
                    "type": "string",
                    "description": "Specify a bible version to read.  Answer 'XXX' if none is specified.",
                    "enum": ['XXX'] + bibleList,
                },
            },
            "required": ["version"],
        },
    }

    # make available for function calling
    config.pluginsWithFunctionCall.append("convert_bible")
    config.chatGPTApiFunctionSignatures.append(functionSignature)
    config.chatGPTApiAvailableFunctions["convert_bible"] = convert_bible
