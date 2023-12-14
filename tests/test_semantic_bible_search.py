from letmedoit.health_check import HealthCheck
import os, chromadb

if __name__ == '__main__':
    # testing
    
    #dbpath
    dbpath = os.path.join("/home/eliran/letmedoit", "bibles", "NET")
    # client
    chroma_client = chromadb.PersistentClient(dbpath)
    # collection
    collection = chroma_client.get_or_create_collection(
        name="verses",
        metadata={"hnsw:space": "cosine"},
        embedding_function=HealthCheck.getEmbeddingFunction(),
    )

    query = ""
    while not query == ".quit":
        query = input("Enter your query: ")
        if query == ".quit":
            break
        res = collection.query(
            include=["metadatas", "documents"],
            query_texts=[query],
            n_results = 10,
        )
        print("--------------------")
        print(">>> retrieved verses: \n")
        refs = [i["book_abb"]+" "+str(i["chapter"])+":"+str(i["verse"]) for i in res["metadatas"][0]] 
        for key, value in dict(zip(refs, res["documents"][0])).items():
            print(f"({key}) {value}")
        print("--------------------")


