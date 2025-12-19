import uuid
import json
from typing import Dict

from src.schemas import IngestRequest, IngestResponse
from src.vector_store import get_chroma_client, get_collection


def ingest_product(payload: IngestRequest) -> IngestResponse:
    client = get_chroma_client()
    collection = get_collection(client)

    # Use the provided description (already generated and possibly edited by user)
    description = payload.description.strip()
    if not description:
        raise ValueError("Description is required and cannot be empty.")

    product_id = str(uuid.uuid4())
    # ChromaDB metadata only accepts primitive types, so convert lists to JSON strings
    metadata: Dict[str, object] = {
        "name": payload.name,
        "keywords": json.dumps(payload.keywords),  # Convert list to JSON string
        "image_urls": json.dumps([str(u) for u in payload.image_urls]),  # Convert list to JSON string
        "description": description,
    }

    collection.add(
        ids=[product_id],
        documents=[description],
        metadatas=[metadata],
    )

    # Return metadata with original list format (not JSON strings) for API response
    response_metadata: Dict[str, object] = {
        "name": payload.name,
        "keywords": payload.keywords,
        "image_urls": [str(u) for u in payload.image_urls],
        "description": description,
    }
    
    return IngestResponse(
        product_id=product_id,
        description=description,
        metadata=response_metadata,
    )

