from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models import ProhibitedItem
from app.schemas import ProhibitedItemCreate

def get_prohibited_item_by_name(db: Session, item_name: str):
    return db.query(ProhibitedItem).filter(ProhibitedItem.item_name == item_name).first()

def get_prohibited_items(db: Session, skip: int = 0, limit: int = 10):
    return db.query(ProhibitedItem).offset(skip).limit(limit).all()

def create_prohibited_item(db: Session, item: ProhibitedItemCreate):
    db_item = ProhibitedItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def search_prohibited_items(db: Session, query: str):
    return db.query(ProhibitedItem).filter(
        text("search_vector @@ plainto_tsquery('english', :query)")
    ).params(query=query).all()