import chromadb
from sentence_transformers import SentenceTransformer


# Create embedding model
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# Create persistent ChromaDB client
chroma_client = chromadb.PersistentClient(
    path="memory/chroma_db"
)


# Create or load memory collection
memory_collection = chroma_client.get_or_create_collection(
    name="user_memories"
)


def add_memory(memory_text):
    """
    Store a long-term memory in ChromaDB.
    """

    embedding = embedding_model.encode(
        memory_text
    ).tolist()

    memory_id = str(
        memory_collection.count() + 1
    )

    memory_collection.add(
        ids=[memory_id],
        documents=[memory_text],
        embeddings=[embedding]
    )


def search_memories(query, top_k=3):
    """
    Search for memories relevant to the user's query.
    """

    query_embedding = embedding_model.encode(
        query
    ).tolist()

    results = memory_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    if not results["documents"]:
        return []

    return results["documents"][0]

