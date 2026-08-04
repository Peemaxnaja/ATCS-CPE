from pydantic import BaseModel, Field

class NormalizationOutput(BaseModel):
    """Data Contract for Normalization Step Output"""
    normalized_files_directory: str = Field(..., description="Directory path containing normalized text files")
    normalized_file_list: list[str] = Field(default_factory=list, description="List of normalized file paths or names")
