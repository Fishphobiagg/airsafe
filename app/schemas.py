# app/schemas.py

from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class ConditionBase(BaseModel):
    is_international: bool
    is_domestic: bool
    cabin: str
    trust: str
    condition_description: str
    reference: Optional[str] = None

class ConditionCreate(ConditionBase):
    pass

class Condition(ConditionBase):
    id: int

    class Config:
        from_attributes = True

class ProhibitedItemBase(BaseModel):
    id: int
    item_name: str
    category: str
    subcategory: str
    category_image: str

class ProhibitedItemList(BaseModel):
    search_result: List[ProhibitedItemBase]

class ProhibitedItemCreate(BaseModel):
    item_name: str
    image_path: str
    search_vector: str

class ProhibitedItemCreateResponse(ProhibitedItemCreate):
    id: int

class ProhibitedItem(ProhibitedItemBase):
    conditions: List[Condition]

    class Config:
        from_attributes = True

class ProhibitedItemCondition(BaseModel):
    id: int
    category: str
    subcategory: str
    item_name: str
    image_path: Optional[str] = None
    conditions: List[Condition]

    class Config:
        from_attributes = True

class SubcategoryBase(BaseModel):
    name: str
    search_vector: str

class SubcategoryCreate(SubcategoryBase):
    pass

class Subcategory(SubcategoryBase):
    id: int

    class Config:
        from_attributes = True

class SearchResponse(BaseModel):
    search_term: str
    results: List[ProhibitedItemCondition] = []

    class Config:
        from_attributes = True

class ItemNotFound(BaseModel):
    message: str

    class Config:
        from_attributes = True

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