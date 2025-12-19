from pydantic import BaseModel, HttpUrl, field_validator
from typing import List, Optional


class IngestRequest(BaseModel):
    name: str
    keywords: List[str]
    image_urls: List[HttpUrl]
    description: str

    @field_validator("keywords", "image_urls")
    @classmethod
    def non_empty(cls, v):
        if not v:
            raise ValueError("Must provide at least one item.")
        return v

    @field_validator("description")
    @classmethod
    def description_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Description is required and cannot be empty.")
        return v.strip()


class GenerateDescriptionRequest(BaseModel):
    name: str
    keywords: List[str]
    image_urls: List[HttpUrl]

    @field_validator("keywords", "image_urls")
    @classmethod
    def non_empty(cls, v):
        if not v:
            raise ValueError("Must provide at least one item.")
        return v


class GenerateDescriptionResponse(BaseModel):
    description: str


class IngestResponse(BaseModel):
    product_id: str
    description: str
    metadata: dict


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    product_id: str
    score: float
    metadata: dict


class SearchResponse(BaseModel):
    results: List[SearchResult]

