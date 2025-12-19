import os
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

def get_chroma_client() -> chromadb.Client:
    persist_dir = os.getenv("CHROMA_DIR", ".chroma")
    return chromadb.Client(
        Settings(
            persist_directory=persist_dir,
            is_persistent=True,
        )
    )


def get_collection(client: chromadb.Client):
    return client.get_or_create_collection(
        name="products"
    )

