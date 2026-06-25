from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Tuple,List,Optional


class Entities(BaseModel):
    """Identifying information from entities."""
    name: List[str] = Field(
        ...,
        description="Captute all the symptoms names from the given text"
    )
    
    
    