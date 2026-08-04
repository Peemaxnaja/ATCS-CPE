from pydantic import BaseModel, Field

class ChunkItem(BaseModel):
    """Schema for individual text chunk item"""
    chunk_id: str = Field(..., description="Unique chunk ID formatted as {filename}_c{index:03d}")
    text: str = Field(..., description="Text content of the chunk")
    token_count: int = Field(..., description="Actual token count calculated by tokenizer")

class ChunkingOutput(BaseModel):
    """Data Contract for Chunking Step Output"""
    chunks_directory: str = Field(..., description="Directory path containing generated JSON chunk files")
    chunks_by_file: dict[str, list[ChunkItem]] = Field(
        default_factory=dict,
        description="Mapping from original filename to list of ChunkItems"
    )
