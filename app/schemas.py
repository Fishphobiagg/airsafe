from pydantic import BaseModel
from typing import List

class ProhibitedItemBase(BaseModel):
    category: str
    subcategory: str
    item_name: str
    cabin: bool
    trust: bool
    description: str

class ProhibitedItemCreate(ProhibitedItemBase):
    pass

class ProhibitedItem(ProhibitedItemBase):
    id: int
    
    class Config:
        from_attributes = True

class SearchResponse(BaseModel):
    search_term: str
    results: List[ProhibitedItem] = []

    class Config:
        from_attributes = True

class ItemNotFound(BaseModel):
    message: str