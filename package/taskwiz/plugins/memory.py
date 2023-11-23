"""
My Hand Bot Plugin - memory

Save and retrieve memory

modified from source: https://medium.com/@simon_attard/building-a-memory-layer-for-gpt-using-function-calling-da17d66920d0

[FUNCTION_CALL]
"""

from taskwiz import config
#from taskwiz.utils.shared_utils import SharedUtil
import numpy as np
from numpy.linalg import norm
import uuid, os, chromadb, getpass, geocoder, datetime, json
from openai import OpenAI
#import tiktoken
from pathlib import Path

memory_store = os.path.join(config.getFiles(), "memory")
Path(memory_store).mkdir(parents=True, exist_ok=True)
chroma_client = chromadb.PersistentClient(memory_store)

def cosine_similarity(A, B):
    cosine = np.dot(A, B) / (norm(A) * norm(B))
    return cosine

def get_or_create_collection(collection_name):
    collection = chroma_client.get_or_create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})
    return collection

def get_embedding(text, model="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   #tokenizer = tiktoken.get_encoding("cl100k_base")
   #tokens = tokenizer.encode(text)
   #we can use tiktoken tokenizer to count tokens and ensure token limit is not exceeded.  In this case we will simply pass text to ada v2 model.
   return OpenAI().embeddings.create(input = [text], model=model).data[0].embedding

def add_vector(collection, text, metadata):
    id = str(uuid.uuid4())
    embedding = get_embedding(text)
    collection.add(
        embeddings = [embedding],
        documents = [text],
        metadatas = [metadata],
        ids = [id]
    )

def save_memory(function_args):
    memory = function_args.get("memory") # required
    memory_title = function_args.get("title") # required
    memory_type = function_args.get("type") # required
    memory_tags = function_args.get("tags") # required
    if not isinstance(memory_tags, str):
        memory_tags = str(memory_tags)
    collection = get_or_create_collection("memories")
    g = geocoder.ip('me')
    metadata = {
        "timestamp": str(datetime.datetime.now()),
        "tags": memory_tags,
        "title": memory_title,
        "type": memory_type,
        "user": getpass.getuser(),
        "location": f"{g.city}, {g.state}, {g.country}",
    }
    if config.developer:
        config.print(config.divider)
        print(">>> saving memory: ")
        config.print(f"memory: {memory}")
        print(metadata)
        config.print(config.divider)
    add_vector(collection, memory, metadata)
    config.stopSpinning()
    return "I saved it in my memory!"

def query_vectors(collection, query, n):
    query_embedding = get_embedding(query)
    return collection.query(
        query_embeddings = [query_embedding],
        n_results = n
    )

def retrieve_memories(function_args):
    query = function_args.get("query") # required
    collection = get_or_create_collection("memories")
    res = query_vectors(collection, query, config.numberOfMemoryClosestMatches)
    if config.developer:
        config.print(config.divider)
        print(">>> retrieved memories: ") 
        print(res["documents"])
        config.print(config.divider)
    info = {}
    for index, description in enumerate(res["documents"][0]):
        info[f"memory {index}"] = {
            "description": description,
        }
    config.stopSpinning()
    return json.dumps(info)

functionSignature1 = {
    "name": "save_memory",
    "description": """Use this function if I mention something which you think would be useful in the future and should be saved as a memory. Saved memories will allow you to retrieve snippets of past conversations when needed.""",
    "parameters": {
        "type": "object",
        "properties": {
            "memory": {
                "type": "string",
                "description": "Full description of the memory to be saved. I would like you to help me with converting relative dates and times, if any, into exact dates and times based on the given current date and time."
            },
            "title": {
                "type": "string",
                "description": "Title of the memory"
            },
            "type": {
                "type": "string",
                "description": "Type of the memory, return either 'general', 'instruction', 'fact', 'event', or 'concept'"
            },
            "tags": {
                "type": "string",
                "description": """Return a list of tags about the memory, e.g. '["work", "to_do", "follow_up"]'"""
            },
        },
        "required": ["memory", "title", "type", "tags"]
    }
}
functionSignature2 = {
    "name": "retrieve_memories",
    "description": """Use this function to query and retrieve memories of important conversation snippets that we had in the past. Use this function if the information you require is not in the current prompt or you need additional information to refresh your memory.""",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The query to be used to look up memories from a vector database"
            },
        },
        "required": ["query"]
    }
}

config.inputSuggestions += ["Remember, "]
config.pluginsWithFunctionCall += ["save_memory", "retrieve_memories"]
config.chatGPTApiFunctionSignatures += [functionSignature1, functionSignature2]
config.chatGPTApiAvailableFunctions["save_memory"] = save_memory
config.chatGPTApiAvailableFunctions["retrieve_memories"] = retrieve_memories