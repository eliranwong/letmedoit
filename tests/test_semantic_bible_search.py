from letmedoit.health_check import HealthCheck
import os, chromadb, re


# testing combined semantic and literal and regular expression searches

def getAndItems(query):
    splits = query.split("&&")
    return {"$and": [{"$contains": i} for i in splits]} if len(splits) > 1 else {"$contains": query}

#dbpath
dbpath = os.path.join(os.path.expanduser("~/letmedoit"), "bibles", "NET")
# client
chroma_client = chromadb.PersistentClient(dbpath)
# collection
collection = chroma_client.get_or_create_collection(
    name="verses",
    metadata={"hnsw:space": "cosine"},
    embedding_function=HealthCheck.getEmbeddingFunction(embeddingModel="all-mpnet-base-v2"),
)

meaning = ""
while not meaning == ".quit":
    # user input
    meaning = input("Search for meaning: ")
    if meaning == ".quit":
        break
    books = input("In books: ")
    if books := books.strip():
        splits = books.split("||")
        books = {"$or": [{"book_abbr": i.strip()} for i in splits]} if len(splits) > 1 else {"book_abbr": books.strip()}
    contains = input("In verses that literally contain: ")
    if contains.strip():
        splits = contains.split("||")
        contains = {"$or": [getAndItems(i) for i in splits]} if len(splits) > 1 else getAndItems(contains)
    else:
        contains = ""
    regex = input("With regular expression: ")
    if meaning:
        res = collection.query(
            query_texts=[meaning],
            n_results = 10,
            where=books if books else None,
            where_document=contains if contains else None,
        )
    else:
        res = collection.get(
            where=books if books else None,
            where_document=contains if contains else None,
        )
    print("--------------------")
    print(">>> retrieved verses: \n")
    metadatas = res["metadatas"][0] if meaning else res["metadatas"]
    refs = [f'''{i["book_abbr"]} {i["chapter"]}:{i["verse"]}''' for i in metadatas]
    # results = filter(lambda scripture: re.search(regex, scripture, flags=re.IGNORECASE), zip(refs, res["documents"][0] if meaning else res["documents"]))
    for ref, scripture in zip(refs, res["documents"][0] if meaning else res["documents"]):
        if not regex or (regex and re.search(regex, scripture, flags=re.IGNORECASE)):
            print(f"({ref}) {scripture}")
    print("--------------------")
