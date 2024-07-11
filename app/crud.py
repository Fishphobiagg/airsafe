from sqlalchemy.orm import Session
from sqlalchemy import text, func
from app.models import ProhibitedItem, SearchHistory, Suggestion, Subcategory, Condition
from app.schemas import ProhibitedItemCreate, SuggestionCreate, ConditionCreate, SubcategoryCreate
import asyncio

async def create_prohibited_item(db: Session, item: ProhibitedItemCreate):
    db_item = ProhibitedItem(**item.model_dump())
    db.add(db_item)
    await asyncio.to_thread(db.commit)
    await asyncio.to_thread(db.refresh, db_item)
    return db_item


def search_prohibited_items(db: Session, query: str):
    ts_query = func.to_tsquery('pg_catalog.english', f'{query}:*')
    items = db.query(ProhibitedItem).filter(ProhibitedItem.search_vector.op('@@')(ts_query)).all()

    for item in items:
        conditions_query = db.query(Condition).filter(Condition.prohibited_item_id == item.id)
        item.conditions = conditions_query.all()
    return items
def get_item_conditions_by_id(db: Session, prohibited_item_id: int, is_international: bool = None, is_domestic: bool = None):
    conditions_query = db.query(Condition).filter(Condition.prohibited_item_id == prohibited_item_id)

    if is_international:
        conditions_query = conditions_query.filter(Condition.is_international == is_international)
    if is_domestic:
        conditions_query = conditions_query.filter(Condition.is_domestic == is_domestic)
    return conditions_query.all()

async def create_search_history(db: Session, search_term: str, prohibited_item_id: int = None):
    existing_record = db.query(SearchHistory).filter(SearchHistory.search_term == search_term).first()
    if existing_record:
        existing_record.search_count += 1
        await asyncio.to_thread(db.commit)
        await asyncio.to_thread(db.refresh, existing_record)
        return existing_record
    else:
        search_history = SearchHistory(search_term=search_term, prohibited_item_id=prohibited_item_id)
        db.add(search_history)
        await asyncio.to_thread(db.commit)
        await asyncio.to_thread(db.refresh, search_history)
        return search_history
    
def get_item_conditions(db: Session, prohibited_item_id: int, is_international: bool = None, is_domestic: bool = None):
    query = db.query(Condition).filter(Condition.prohibited_item_id == prohibited_item_id)
    if is_international:
        query = query.filter(Condition.is_international == True)
    if is_domestic:
        query = query.filter(Condition.is_domestic == True)
    return query.all()

def get_prohibited_item_by_id(db: Session, id: int, is_international: bool = None, is_domestic: bool = None) -> ProhibitedItem:
    item = db.query(ProhibitedItem).filter(ProhibitedItem.id == id).first()
    if item:
        item.conditions = get_item_conditions(db, item.id, is_international, is_domestic)
    return item

def get_prohibited_item_by_name(db: Session, name: str, is_international:bool = None, is_domestic: bool = None):
    subcategory_query = db.query(Subcategory).filter(Subcategory.name == name).first()
    if subcategory_query:
        items = db.query(ProhibitedItem).filter(ProhibitedItem.subcategory_id == subcategory_query.id).all()
    else:
        items = db.query(ProhibitedItem).filter(text("search_vector @@ plainto_tsquery('english', :name)")).params(name=name).all()
    
    for item in items:
        conditions_query = db.query(Condition).filter(Condition.prohibited_item_id == item.id)
        if is_international is not None:
            conditions_query = conditions_query.filter(Condition.is_international == is_international)
        if is_domestic is not None:
            conditions_query = conditions_query.filter(Condition.is_domestic == is_domestic)
        item.conditions = conditions_query.all()
    return items

async def create_suggestion(db: Session, suggestion: SuggestionCreate):
    db_suggestion = Suggestion(**suggestion.model_dump())
    db.add(db_suggestion)
    await asyncio.to_thread(db.commit)
    await asyncio.to_thread(db.refresh, db_suggestion)
    return db_suggestion

async def insert_subcategory(db: Session, subcategory: SubcategoryCreate, category_id: int):
    db_subcategory = Subcategory(category_id=category_id, **subcategory.model_dump())
    db.add(db_subcategory)
    await asyncio.to_thread(db.commit)
    await asyncio.to_thread(db.refresh, db_subcategory)
    return db_subcategory

async def insert_prohibited_item(db: Session, item: ProhibitedItemCreate, subcategory_id: int):
    db_item = ProhibitedItem(subcategory_id=subcategory_id, **item.model_dump())
    db.add(db_item)
    await asyncio.to_thread(db.commit)
    await asyncio.to_thread(db.refresh, db_item)
    return db_item

async def insert_condition(db: Session, prohibited_item_id: int, condition: ConditionCreate):
    db_condition = Condition(prohibited_item_id=prohibited_item_id, **condition.model_dump())
    db.add(db_condition)
    await asyncio.to_thread(db.commit)
    await asyncio.to_thread(db.refresh, db_condition)
    return db_condition