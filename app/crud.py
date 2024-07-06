from sqlalchemy.orm import Session
from sqlalchemy import text, func
from app.models import ProhibitedItem, SearchHistory
from app.schemas import ProhibitedItemCreate
import asyncio

async def create_prohibited_item(db: Session, item: ProhibitedItemCreate):
    db_item = ProhibitedItem(**item.model_dump())
    db.add(db_item)
    await asyncio.to_thread(db.commit)
    await asyncio.to_thread(db.refresh, db_item)
    return db_item

def search_prohibited_items(db: Session, query: str):
    return db.query(ProhibitedItem).filter(
        text("search_vector @@ plainto_tsquery('english', :query)")
    ).params(query=query).limit(10).all()

async def create_search_history(db: Session, search_term: str, prohibited_item_id: int = None):
    existing_record = db.query(SearchHistory).filter(SearchHistory.search_term == search_term).first()
    if existing_record:
        existing_record.search_count += 1
        existing_record.search_date = func.now()
        await asyncio.to_thread(db.commit)
        await asyncio.to_thread(db.refresh, existing_record)
        return existing_record
    else:
        search_history = SearchHistory(search_term=search_term, prohibited_item_id=prohibited_item_id)
        db.add(search_history)
        await asyncio.to_thread(db.commit)
        await asyncio.to_thread(db.refresh, search_history)
        return search_history
    
def get_prohibited_item_by_id(db: Session, id: int) -> ProhibitedItem:
    return db.query(ProhibitedItem).filter(ProhibitedItem.id == id).first()

def get_prohibited_item_by_name(db: Session, name: str):
    return db.query(ProhibitedItem).filter(text("search_vector @@ plainto_tsquery('english', :name)")).params(name=name).first()
