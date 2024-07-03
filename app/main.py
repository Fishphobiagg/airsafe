from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from app.schemas import ProhibitedItemCreate, ProhibitedItem, ProhibitedItemBase
from app.crud import create_prohibited_item, get_prohibited_item_by_name, search_prohibited_items
from app.database import SessionLocal, init_db

from fastapi.middleware.cors import CORSMiddleware

init_db()

app = FastAPI()

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/items/", response_model=ProhibitedItem)
def create_item(item: ProhibitedItemCreate, db: Session = Depends(get_db)):
    return create_prohibited_item(db=db, item=item)

@app.get("/items/", response_model=list[ProhibitedItem])
def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    items = get_prohibited_item_by_name(db, skip=skip, limit=limit)
    return items

@app.get("/items/{query}", response_model=list[ProhibitedItem])
def read_item(query: str, skip:int=0, limit: int=10, db: Session = Depends(get_db)):
    items = search_prohibited_items(db, query=query, skip=skip, limit=limit)
    if items is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return items