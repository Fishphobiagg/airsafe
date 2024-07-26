from sqlalchemy.orm import Session
from sqlalchemy import text, func, or_
from app.models import Category, SearchHistory, ProhibitedItem, SearchHistory, Suggestion, Subcategory, Condition, FlightOption, FieldOption
from app.schemas import ProhibitedItemCreate, SuggestionCreate, ConditionCreate, SubcategoryCreate
import asyncio
from typing import List

def search_subcategory_with_items(db: Session, search_term: str):
    subcategory = db.query(Subcategory).filter(Subcategory.name.ilike(f'%{search_term}%')).first()
    if subcategory:
        items = db.query(ProhibitedItem).filter(ProhibitedItem.subcategory_id == subcategory.id).all()
        return subcategory, items
    return None, []

async def create_prohibited_item(db: Session, item: ProhibitedItemCreate):
    db_item = ProhibitedItem(**item.model_dump())
    db.add(db_item)
    await asyncio.to_thread(db.commit)
    await asyncio.to_thread(db.refresh, db_item)
    return db_item

def search_prohibited_items(db: Session, query: str):
    items = db.query(ProhibitedItem).filter(ProhibitedItem.item_name.ilike(f'{query}%')).all()
    return items

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

def get_flight_option_id(db: Session, option_name: str):
    flight_option = db.query(FlightOption).filter(FlightOption.option == option_name).first()
    return flight_option.id if flight_option else None

def get_item_conditions(db: Session, prohibited_item_id: int, is_international: bool = None, is_domestic: bool = None):
    flight_option_ids = []
    if is_international:
        flight_option_ids.append(1)  # 국제선
    if is_domestic:
        flight_option_ids.append(2)  # 국내선

    conditions = db.query(Condition).filter(Condition.prohibited_item_id == prohibited_item_id).filter(
        or_(Condition.flight_option_id.in_(flight_option_ids), len(flight_option_ids) == 0)).all()
    return conditions

def get_prohibited_item_by_id(db: Session, id: int, is_international: bool = None, is_domestic: bool = None) -> ProhibitedItem:
    item = db.query(ProhibitedItem).filter(ProhibitedItem.id == id).first()
    if item:
        item.conditions = get_item_conditions(db, item.id, is_international, is_domestic)
    return item

def get_condition_by_name(db: Session, name: str, is_international: bool = None, is_domestic: bool = None):
    item = db.query(ProhibitedItem).filter(ProhibitedItem.item_name.ilike(f'%{name}%')).first()
    if item:
        item.conditions = get_item_conditions(db, item.id, is_international=is_international, is_domestic=is_domestic)
    return item

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

def get_top_search_histories(db: Session, limit: int) -> List[SearchHistory]:
    return db.query(SearchHistory)\
             .filter(SearchHistory.prohibited_item_id.isnot(None))\
             .order_by(SearchHistory.search_count.desc())\
             .limit(limit)\
             .all()

def get_categories(db: Session) -> List[Category]:
    return db.query(Category)\
            .all()

def get_subcategories(db: Session) -> List[Subcategory]:
    return db.query(Subcategory)\
            .all()

def get_flight_options(db: Session) -> List[FlightOption]:
    return db.query(FlightOption)\
            .all()

def get_field_options(db: Session) -> List[FieldOption]:
    return db.query(FieldOption)\
            .all()
    
def create_prohibited_item_with_conditions(db: Session, item: ProhibitedItemCreate):
    new_item = ProhibitedItem(
        item_name=item.item_name,
        image_path=item.image_path,
        subcategory_id=item.subcategory_id
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    for condition in item.conditions:
        db_condition = Condition(
            prohibited_item_id=new_item.id,
            flight_option_id=condition.flight_option_id,
            field_option_id=condition.field_option_id,
            condition=condition.condition,
            allowed=condition.allowed
        )
        db.add(db_condition)
    
    db.commit()