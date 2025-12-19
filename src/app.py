from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uvicorn
import logging

from src.schemas import (
    GenerateDescriptionRequest,
    GenerateDescriptionResponse,
    IngestRequest,
    IngestResponse,
    SearchRequest,
    SearchResponse,
)
from src.ingestion import ingest_product
from src.search import search_products
from src.gemini_client import generate_description

logger = logging.getLogger(__name__)

app = FastAPI(title="Semantic Product Retrieval")

# Allow CORS for local dev UI; adjust origins as needed for production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with detailed messages."""
    errors = exc.errors()
    error_messages = []
    for error in errors:
        field = " -> ".join(str(loc) for loc in error["loc"])
        msg = error["msg"]
        error_messages.append(f"{field}: {msg}")
    return JSONResponse(
        status_code=400,
        content={"detail": "; ".join(error_messages), "errors": errors},
    )

@app.post("/ingest", response_model=IngestResponse)
def ingest(payload: IngestRequest):
    try:
        logger.info(f"Ingesting product: {payload.name}")
        logger.info(f"Keywords: {payload.keywords}")
        logger.info(f"Image URLs: {[str(u) for u in payload.image_urls]}")
        logger.info(f"Description length: {len(payload.description)} chars")
        return ingest_product(payload)
    except ValueError as exc:
        logger.error(f"Validation error: {exc}")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - surface unexpected errors
        logger.error(f"Ingestion error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Ingestion failed") from exc


@app.post("/search", response_model=SearchResponse)
def search(payload: SearchRequest):
    try:
        return search_products(payload)
    except Exception as exc:  # pragma: no cover
        logger.error(f"Search error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Search failed") from exc


@app.post("/generate_description", response_model=GenerateDescriptionResponse)
def generate_description_route(payload: GenerateDescriptionRequest):
    try:
        description = generate_description(
            image_urls=[str(u) for u in payload.image_urls],
            name=payload.name,
            keywords=payload.keywords,
        )
        return GenerateDescriptionResponse(description=description)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=500, detail="Description generation failed"
        ) from exc


def main():
    """Launch the uvicorn server."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8000
    )


if __name__ == "__main__":
    main()

