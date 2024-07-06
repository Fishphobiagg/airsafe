from fastapi import FastAPI, Depends, Response
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from app.schemas import ProhibitedItem, SearchResponse, ItemNotFound
from app.crud import get_prohibited_item_by_id, get_prohibited_item_by_name, create_search_history, search_prohibited_items
from app.database import SessionLocal, init_db

from fastapi.middleware.cors import CORSMiddleware

from typing import Optional, Union

init_db()

app = FastAPI()

origins = ["https://air-safe.co.kr", "http://air-safe.co.kr"]

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

@app.get("/items/", 
         response_model=Union[SearchResponse, ItemNotFound],
         summary="검색어를 통해 검색되는 여러 건의 결과를 검색하는 api",
         description="입력된 검색어를 통해 검색되는 품목을 반환",
         status_code=200)
async def search_items(
    search_term: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    items = search_prohibited_items(db, query=search_term)
    if not items:
        await create_search_history(db, search_term=search_term)
        return JSONResponse(content=ItemNotFound(message=f"id : {search_term} is not found").model_dump_json(), 
                status_code=404, 
                media_type="application/json"
        )
    await create_search_history(db, search_term=search_term, prohibited_item_id=items[0].id)
    return SearchResponse(search_term=search_term, results=items)

@app.get("/items/{item_id}", 
         response_model=Union[ProhibitedItem, ItemNotFound],
         status_code=200,
         summary="아이템 id로 아이템을 단건 검색하는 api",
         )
async def get_item_by_id(item_id: int, db: Session = Depends(get_db)):
    item = get_prohibited_item_by_id(db=db, id=item_id)
    if item is None:
        await create_search_history(db, search_term=f"id: {item_id}")
        return JSONResponse(content=ItemNotFound(message=f"id : {item_id} is not found").model_dump_json(), 
                        status_code=404, 
                        media_type="application/json"
        )
    await create_search_history(db, search_term=f"id: {item_id}", prohibited_item_id=item.id)
    return 

@app.get("/items/search/", 
         response_model=Union[ProhibitedItem, ItemNotFound],
         status_code=200,
         summary="사용자가 입력한 검색어를 단건 검색",
         description="쿼리 스트링으로 검색어 요청"
        )
async def get_item_by_search_term(
    search_term: Optional[str],
    db: Session = Depends(get_db)
):
    item = get_prohibited_item_by_name(name=search_term, db=db)
    if item is None:    
        await create_search_history(db, search_term=search_term)
        return JSONResponse(content=ItemNotFound(message=f"id : {search_term} is not found").model_dump_json(), 
                        status_code=404, 
                        media_type="application/json"
        )
    await create_search_history(db, search_term=search_term, prohibited_item_id=item.id)
    return item
