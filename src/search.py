import json
from typing import List, Dict, Any

from src.schemas import SearchRequest, SearchResponse, SearchResult
from src.vector_store import get_chroma_client, get_collection


def search_products(payload: SearchRequest) -> SearchResponse:
    client = get_chroma_client()
    collection = get_collection(client)

    results = collection.query(
        query_texts=[payload.query],
        n_results=payload.top_k,
        include=["metadatas", "distances"],  # IDs are always returned, don't include in the list
    )

    ids = results.get("ids", [[]])[0]
    distances = results.get("distances", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    search_results: List[SearchResult] = []
    for pid, dist, meta in zip(ids, distances, metadatas):
        score = 1 - dist  # convert distance to similarity-ish score
        # Parse JSON strings back to lists for keywords and image_urls
        parsed_meta: Dict[str, Any] = {}
        for key, value in meta.items():
            if key in ("keywords", "image_urls") and isinstance(value, str):
                try:
                    parsed_meta[key] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    # Fallback if parsing fails
                    parsed_meta[key] = value
            else:
                parsed_meta[key] = value
        search_results.append(SearchResult(product_id=pid, score=score, metadata=parsed_meta))

    return SearchResponse(results=search_results)

