from pydantic import BaseModel, Field
from typing import Any

class EmbeddedChunkItem(BaseModel):
    """Schema for individual chunk item with generated embedding vector and metadata"""
    chunk_id: str = Field(..., description="Unique ID of the chunk")
    text: str = Field(..., description="Text content of the chunk")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary associated with chunk")
    embedding: list[float] = Field(..., description="Raw floating point vector embedding array")

class EmbeddingOutput(BaseModel):
    """Data Contract for Embedding Step Output"""
    embeddings_directory: str = Field(..., description="Directory path containing generated embedding JSON files")
    embedded_chunks: list[EmbeddedChunkItem] = Field(
        default_factory=list,
        description="List of all embedded chunk items across files"
    )
