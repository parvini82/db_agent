from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from config.settings import QDRANT_URL, EMBEDDING_MODEL

# Connect to Qdrant
client = QdrantClient(QDRANT_URL)
encoder = SentenceTransformer(EMBEDDING_MODEL)

# Metadata descriptions (each entry = one table or relation)
metadata = [
    {
        "id": 1,
        "text": "Table Products: contains product information such as id, name, category, and description."
    },
    {
        "id": 2,
        "text": "Table Suppliers: contains supplier information such as id, name, city, and address."
    },
    {
        "id": 3,
        "text": "Table Purchases: contains data about products purchased from suppliers, including product_id, supplier_id, purchase_date, quantity, and unit_cost."
    },
    {
        "id": 4,
        "text": "Table Sales: contains information about product sales including product_id, sale_date, quantity, and unit_price."
    },
    {
        "id": 5,
        "text": "Relation: Purchases.product_id refers to Products.id."
    },
    {
        "id": 6,
        "text": "Relation: Purchases.supplier_id refers to Suppliers.id."
    },
    {
        "id": 7,
        "text": "Relation: Sales.product_id refers to Products.id."
    }
]

def prepare_metadata_collection():
    """Create metadata embeddings and upload them to Qdrant."""
    collection_name = "db_metadata"

    # Create collection if not exists
    client.create_collection(
        collection_name=collection_name,
        vectors_config={"size": 384, "distance": "Cosine"}  # 384 for MiniLM-L6-v2
    )

    # Encode metadata descriptions
    texts = [m["text"] for m in metadata]
    vectors = encoder.encode(texts)

    # Upload to Qdrant
    client.upload_collection(
        collection_name=collection_name,
        ids=[m["id"] for m in metadata],
        vectors=vectors,
        payload=metadata
    )

    print(f"✅ Uploaded {len(metadata)} metadata entries to Qdrant ({collection_name})")

if __name__ == "__main__":
    prepare_metadata_collection()