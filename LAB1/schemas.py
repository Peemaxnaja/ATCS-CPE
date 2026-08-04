from pydantic import BaseModel, Field
from typing import Optional

class EnrichedChunkItem(BaseModel):
    """Schema for individual chunk item with enriched metadata"""
    chunk_id: str = Field(..., description="Unique ID of the chunk")
    text: str = Field(..., description="Text content of the chunk")
    source: str = Field(..., description="Source file path or origin of the chunk document")
    filename: str = Field(..., description="Original filename associated with chunk")
    page: Optional[int] = Field(None, description="Page number if available")
    language: str = Field("th", description="Language code of text content (e.g. 'th', 'en')")
    author: Optional[str] = Field(None, description="Author or creator of document")
    created_at: Optional[str] = Field(None, description="ISO timestamp of creation/processing time")

class MetadataOutput(BaseModel):
    """Data Contract for Metadata Enrichment Step Output"""
    metadata_directory: str = Field(..., description="Directory path containing generated metadata JSON files")
    enriched_chunks: list[EnrichedChunkItem] = Field(
        default_factory=list,
        description="List of all enriched chunk items across files"
    )
