from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from config.settings import QDRANT_URL, EMBEDDING_MODEL

# Initialize client and encoder
client = QdrantClient(QDRANT_URL)
encoder = SentenceTransformer(EMBEDDING_MODEL)

def retrieve_context(user_query: str, top_k: int = 3) -> str:
    """Retrieve the most relevant metadata context from Qdrant."""
    query_vector = encoder.encode(user_query)

    results = client.search(
        collection_name="db_metadata",
        query_vector=query_vector,
        limit=top_k
    )

    # Combine all matched descriptions
    context = "\n".join([hit.payload["text"] for hit in results])

    return context
