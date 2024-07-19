from fastapi import FastAPI, Depends, Path, Body, Query
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from app.schemas import ProhibitedItemCreateResponse, SearchResponse,ProhibitedItemBase, ItemNotFound, Suggestion, ProhibitedItemList, SuggestionCreate, Condition, Subcategory, SubcategoryCreate, ProhibitedItemCreate, ConditionCreate, ProhibitedItemCondition
from app.crud import get_prohibited_item_by_id, get_prohibited_item_by_name, create_search_history, search_prohibited_items, create_suggestion, insert_condition, insert_prohibited_item, insert_subcategory
from app.database import SessionLocal, init_db

from fastapi.middleware.cors import CORSMiddleware

from typing import Optional, Union

init_db()

app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})

origins = ["*"]

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
         response_model=Union[ProhibitedItemList, ItemNotFound],
         summary="검색어를 통해 자동완성된 검색 결과를 반환하는 api",
         description="입력된 검색어를 통해 자동완성 되는 품목을 반환",
         status_code=200)
async def search_items(
    search_term: Optional[str] = None,
    db: Session = Depends(get_db)
):
    items = search_prohibited_items(db, query=search_term)
    if not items:
        await create_search_history(db, search_term=search_term)
        return JSONResponse(content=ItemNotFound(message=f"No items found for search term: {search_term}").model_dump(),
                            status_code=404,
                            media_type="application/json")

    await create_search_history(db, search_term=search_term)
    return ProhibitedItemList(
        search_result=[ProhibitedItemBase(
            id=item.id,
            item_name=item.item_name,
            category=item.subcategory.category.name,
            subcategory=item.subcategory.name,
            image_path=item.image_path,
            category_image=item.subcategory.category.image
        ) for item in items]
    )

@app.get("/items/{item_id}/", 
         response_model=Union[ProhibitedItemCondition, ItemNotFound],
         status_code=200,
         summary="아이템 id로 아이템을 단건 검색하는 api",
         description="국제선, 국내선 구분을 두고 아이템 id의 반입 조건을 반환"
         )
async def get_item_by_id(
    item_id: int = Path(..., description="The ID of the item to retrieve"),
    is_international: Optional[bool] = Query(None),
    is_domestic: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    item = get_prohibited_item_by_id(db=db, id=item_id, is_international=is_international, is_domestic=is_domestic)
    if item is None:
        await create_search_history(db, search_term=f"id: {item_id}")
        return JSONResponse(content=ItemNotFound(message=f"id : {item_id} is not found").model_dump(), 
                            status_code=404, 
                            media_type="application/json")
    await create_search_history(db, search_term=item.item_name, prohibited_item_id=item.id)

    cabin_conditions = [condition.condition for condition in item.conditions if condition.field_option.option == "cabin"]
    trust_conditions = [condition.condition for condition in item.conditions if condition.field_option.option == "trust"]
    
    cabin_allowed = [condition.allowed for condition in item.conditions if condition.field_option.option == "cabin"]
    trust_allowed = [condition.allowed for condition in item.conditions if condition.field_option.option == "trust"]

    cabin_status = '△' if True in cabin_allowed and False in cabin_allowed else ('O' if all(c == True for c in cabin_allowed) else 'X')
    trust_status = '△' if True in trust_allowed and False in trust_allowed else ('O' if all(c == True for c in trust_allowed) else 'X')

    return {
        "id": item.id,
        "category": item.subcategory.category.name,
        "subcategory": item.subcategory.name,
        "item_name": item.item_name,
        "image_path": item.image_path,
        "cabin": {
            "availability": cabin_status,
            "condition_description": cabin_conditions
        },
        "trust": {
            "availability": trust_status,
            "condition_description": trust_conditions
        }
    }

@app.get("/items/search/conditions/", 
         response_model=Union[SearchResponse, ItemNotFound],
         status_code=200,
         summary="사용자가 입력한 검색어를 단건 검색",
         description="쿼리 스트링으로 검색어 요청"
        )
async def get_item_by_search_term(
    search_term: Optional[str] = Query(None),
    is_international: Optional[bool] = Query(None),
    is_domestic: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    items = get_prohibited_item_by_name(db=db, name=search_term, is_international=is_international, is_domestic=is_domestic)
    if not items:
        await create_search_history(db, search_term=search_term)
        return JSONResponse(content=ItemNotFound(message=f"Item : {search_term} is not found").model_dump(), 
                            status_code=404, 
                            media_type="application/json")
    
    results = []
    for item in items:
        cabin_conditions = [condition.condition for condition in item.conditions if condition.field_option.option == "cabin"]
        trust_conditions = [condition.condition for condition in item.conditions if condition.field_option.option == "trust"]
        
        cabin_allowed = [condition.allowed for condition in item.conditions if condition.field_option.option == "cabin"]
        trust_allowed = [condition.allowed for condition in item.conditions if condition.field_option.option == "trust"]

        cabin_status = '△' if True in cabin_allowed and False in cabin_allowed else ('O' if all(c == True for c in cabin_allowed) else 'X')
        trust_status = '△' if True in trust_allowed and False in trust_allowed else ('O' if all(c == True for c in trust_allowed) else 'X')

        item_dict = {
            "id": item.id,
            "category": item.subcategory.category.name,
            "subcategory": item.subcategory.name,
            "item_name": item.item_name,
            "image_path": item.image_path,
            "cabin": {
                "availability": cabin_status,
                "condition_description": cabin_conditions
            },
            "trust": {
                "availability": trust_status,
                "condition_description": trust_conditions
            }
        }
        results.append(item_dict)
    await create_search_history(db, search_term=search_term, prohibited_item_id=items[0].id)
    return SearchResponse(search_term=search_term, results=results)

@app.post("/suggestions/", 
          response_model=Suggestion,
          status_code=201,
          summary="사용자의 건의사항을 추가하는 API",
          description="사용자가 입력한 건의사항을 데이터베이스에 저장합니다.")
async def create_user_suggestion(
    suggestion: SuggestionCreate,
    db: Session = Depends(get_db)
):
    new_suggestion = await create_suggestion(db=db, suggestion=suggestion)
    validated_suggestion = Suggestion.model_validate(new_suggestion)
    return JSONResponse(content={"message": "건의사항이 성공적으로 전달되었습니다.", "data": validated_suggestion.to_dict()}, status_code=201)

@app.post("/categories/{category_id}/subcategories/", 
          response_model=Subcategory,
          status_code=201,
          summary="서브카테고리를 추가하는 API",
          description="카테고리 ID와 서브카테고리 이름을 입력받아 서브카테고리를 추가합니다.")
async def create_subcategory(
    subcategory: SubcategoryCreate,
    category_id: int,
    db: Session = Depends(get_db)
):
    new_subcategory = await insert_subcategory(db=db, subcategory=subcategory, category_id=category_id)
    return new_subcategory

@app.post("/subcategorys/{subcategory_id}/items/", 
          response_model=ProhibitedItemCreateResponse,
          status_code=201,
          summary="아이템을 추가하는 API",
          description="서브카테고리 ID와 아이템 정보를 입력받아 아이템을 추가합니다.")
async def create_prohibited_item(
    subcategory_id: int = Path(..., description="서브카테고리 ID"),
    item: ProhibitedItemCreate = Body(...),
    db: Session = Depends(get_db)
):
    new_item = await insert_prohibited_item(db=db, item=item, subcategory_id=subcategory_id)
    return ProhibitedItemCreateResponse(
        id= new_item.id,
        item_name= new_item.item_name,
        image_path = new_item.item_name,
        search_vector = new_item.search_vector
    )

@app.post("/items/{item_id}/conditions/", 
          response_model=Condition,
          status_code=201,
          summary="조건을 추가하는 API",
          description="아이템 ID와 조건 정보를 입력받아 조건을 추가합니다.")
async def create_condition(
    item_id: int = Path(..., description="아이템 id"),
    condition: ConditionCreate= Body(...),
    db: Session = Depends(get_db)
):
    new_condition = await insert_condition(db=db, prohibited_item_id=item_id, condition=condition)
    return new_condition