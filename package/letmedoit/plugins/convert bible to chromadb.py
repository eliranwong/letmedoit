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
from letmedoit.plugins.bibleTools.utils.AGBsubheadings import agbSubheadings
from letmedoit.plugins.bibleTools.utils.AGBparagraphs_expanded import agbParagraphs
from letmedoit.health_check import HealthCheck
from chromadb.config import Settings
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
    chroma_client = chromadb.PersistentClient(dbpath, Settings(anonymized_telemetry=False))
    # collection
    collectionVerse = chroma_client.get_or_create_collection(
        name="verses",
        metadata={"hnsw:space": "cosine"},
        embedding_function=HealthCheck.getEmbeddingFunction(embeddingModel="all-mpnet-base-v2"),
    )
    collectionParagraph = chroma_client.get_or_create_collection(
        name="paragraphs",
        metadata={"hnsw:space": "cosine"},
        embedding_function=HealthCheck.getEmbeddingFunction(embeddingModel="all-mpnet-base-v2"),
    )

    paragraphTitle = ""
    paragraphStart = ""
    paragraphStartB = ""
    paragraphStartC = ""
    paragraphStartV = ""
    paragraphEnd = ""
    paragraphEndB = ""
    paragraphEndC = ""
    paragraphEndV = ""
    paragraphContent = ""            

    with ProgressBar() as pb:
        for book, chapter, verse, scripture in pb(getAllVerses()):
            bcv = f"{book}.{chapter}.{verse}"

            abbrev = BibleBooks.abbrev["eng"]
            book_abbr = abbrev[str(book)][0]
            metadata = {
                "book_abbr": book_abbr,
                "book": book,
                "chapter": chapter,
                "verse": verse,
                "reference": bcv,
            }
            id = str(uuid.uuid4())
            collectionVerse.add(
                documents = [scripture],
                metadatas = [metadata],
                ids = [id]
            )

            if bcv in agbSubheadings:
                if paragraphStart and paragraphEnd:
                    # save previous paragraph
                    metadata = {
                        "title": paragraphTitle,
                        "start": paragraphStart,
                        "book_start": paragraphStartB,
                        "chapter_start": paragraphStartC,
                        "verse_start": paragraphStartV,
                        "end": paragraphEnd,
                        "book_end": paragraphEndB,
                        "chapter_end": paragraphEndC,
                        "verse_end": paragraphEndV,
                    }
                    id = str(uuid.uuid4())
                    collectionParagraph.add(
                        documents = [paragraphContent],
                        metadatas = [metadata],
                        ids = [id]
                    )
                paragraphTitle = agbSubheadings.get(bcv)
                paragraphStart = bcv
                paragraphStartB = str(book)
                paragraphStartC = str(chapter)
                paragraphStartV = str(verse)
                paragraphContent = f"{paragraphTitle}\n{chapter}:{verse} {scripture}"
            else:
                if (book, chapter, verse) in agbParagraphs:
                    paragraphContent += "\n"
                paragraphContent += f"\n{chapter}:{verse} {scripture}"
            paragraphEnd = bcv
            paragraphEndB = str(book)
            paragraphEndC = str(chapter)
            paragraphEndV = str(verse)

        # save the last paragraph
        metadata = {
            "title": paragraphTitle,
            "start": paragraphStart,
            "book_start": paragraphStartB,
            "chapter_start": paragraphStartC,
            "verse_start": paragraphStartV,
            "end": paragraphEnd,
            "book_end": paragraphEndB,
            "chapter_end": paragraphEndC,
            "verse_end": paragraphEndV,
        }
        id = str(uuid.uuid4())
        collectionParagraph.add(
            documents = [paragraphContent],
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
