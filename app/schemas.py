from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ConditionBase(BaseModel):
    flight_option_id: int
    condition: str
    allowed: bool
    field_option_id: int

class ConditionCreate(ConditionBase):
    pass

class Condition(ConditionBase):
    id: int

    class Config:
        from_attributes = True

class ProhibitedItemBase(BaseModel):
    id: int
    item_name: str
    category_image: str

class ProhibitedItemList(BaseModel):
    items: List[ProhibitedItemBase]

class ConditionCreate(BaseModel):
    condition: str
    allowed: bool
    flight_option_id: int
    field_option_id: int

class ProhibitedItemCreate(BaseModel):
    item_name: str
    image_path: str
    subcategory_id: int
    conditions: List[ConditionCreate]

class SubcategoryDetails(BaseModel):
    id: int
    name: str

class SubcategoryWithItemsResponse(BaseModel):
    subcategory: SubcategoryDetails
    items: List[ProhibitedItemBase]

class SubcategoryCreate(BaseModel):
    name: str
    category_id: int

class ProhibitedItem(BaseModel):
    id: int
    item_name: str
    category: str
    subcategory: str
    image_path: Optional[str]
    conditions: List[Condition]

    class Config:
        from_attributes = True

class ProhibitedItemCondition(BaseModel):
    id: int
    category: str
    subcategory: str
    item_name: str
    image_path: Optional[str] = None
    flight_option: str
    cabin: dict
    trust: dict

    class Config:
        from_attributes = True

class SubcategoryBase(BaseModel):
    id: int
    name: str

class Subcategory(SubcategoryBase):
    id: int
    name: str

    class Config:
        from_attributes = True

class Category(BaseModel):
    id: int
    name:str

    class Config:
        from_attributes = True

class FieldOption(BaseModel):
    id: int
    option: str

    class Config:
        from_attributes = True

class FlightOption(BaseModel):
    id: int
    option: str

    class Config:
        from_attributes = True

class SearchResponse(BaseModel):
    search_term: str
    items: List[ProhibitedItemCondition] = []

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

    class Config:
        from_attributes = True

    def to_dict(self):
        data = self.model_dump()
        data['created_at'] = self.created_at.isoformat()
        return data
    
class SearchHistoryResponse(BaseModel):
    prohibited_item_id: int
    search_term: str