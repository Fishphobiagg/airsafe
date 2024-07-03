from pydantic import BaseModel

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