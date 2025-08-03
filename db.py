import chromadb
from embedding import embed_fn

chroma_client = chromadb.Client()
DB_NAME = "googlecar_collection"

db = chroma_client.get_or_create_collection(
    name=DB_NAME,
    embedding_function=embed_fn,
)
