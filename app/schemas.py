from pydantic import BaseModel, ConfigDict
from typing import List
from datetime import datetime


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

class SuggestionBase(BaseModel):
    suggestion_text: str

class SuggestionCreate(SuggestionBase):
    pass

class Suggestion(SuggestionBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    def to_dict(self):
        data = self.model_dump()
        data['created_at'] = self.created_at.isoformat()
        return data