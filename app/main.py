from fastapi import FastAPI, Depends, Path, Request, Query, Form
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse, HTMLResponse

from app.schemas import SearchHistoryResponse, SubcategoryCreate, SearchResponse,ProhibitedItemBase, ItemNotFound, Suggestion, ProhibitedItemList, SuggestionCreate, Subcategory, SubcategoryCreate, ProhibitedItemCreate, ConditionCreate, ProhibitedItemCondition, Category, FieldOption, FlightOption
from app.crud import get_item_conditions, create_prohibited_item_with_conditions, get_top_search_histories, get_prohibited_item_by_id, get_condition_by_name, create_search_history, search_prohibited_items, create_suggestion, insert_subcategory, get_categories, get_field_options, get_flight_options, get_subcategories
from app.database import SessionLocal, init_db

from fastapi.staticfiles import StaticFiles

from fastapi.middleware.cors import CORSMiddleware

from typing import Optional, Union, List

init_db()

app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})

app.mount("/static", StaticFiles(directory="static"), name="static")

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


@app.get("/", response_class=HTMLResponse)
async def get_form():
    with open("static/form.html") as f:
        return HTMLResponse(content=f.read())

@app.get("/create_subcategory/", response_class=HTMLResponse)
async def get_subcategory_form():
    with open("static/subcategory_form.html") as f:
        return HTMLResponse(content=f.read())

@app.get("/items/",
         response_model=Union[ProhibitedItemList, ItemNotFound],
         summary="검색어를 통해 자동완성된 검색 결과를 반환하는 api",
         description="입력된 검색어를 통해 자동완성 되는 품목을 반환",
         status_code=200)
async def search_items(
    search_term: Optional[str] = None,
    db: Session = Depends(get_db)
):
    if search_term is None:
        return JSONResponse(content=ItemNotFound(message="Search term is required").model_dump(),
                            status_code=400,
                            media_type="application/json")

    items = search_prohibited_items(db, query=search_term)
    if not items:
        await create_search_history(db, search_term=search_term)
        return JSONResponse(content=ItemNotFound(message=f"No items found for search term: {search_term}").model_dump(),
                            status_code=404,
                            media_type="application/json")

    await create_search_history(db, search_term=search_term)
    return ProhibitedItemList(
        items=[ProhibitedItemBase(
            id=item.id,
            item_name=item.item_name,
            category_image=item.subcategory.category.image
        ) for item in items]
    )

@app.post("/subcategories/{subcategory_id}/items/")
async def create_item_with_conditions(
    request: Request,
    subcategory_id: int = Path(...),
    item_name: str = Form(...),
    image_path: str = Form(...),
    db: Session = Depends(get_db)
):
    form = await request.form()
    conditions = []

    for key in form:
        if key.startswith("condition_"):
            index = key.split("_")[1]
            condition_text = form.get(f"condition_{index}")
            allowed = form.get(f"allowed_{index}") == "true"
            flight_option_id = int(form.get(f"flight_option_id_{index}"))
            field_option_id = int(form.get(f"field_option_id_{index}"))

            condition = ConditionCreate(
                condition=condition_text,
                allowed=allowed,
                flight_option_id=flight_option_id,
                field_option_id=field_option_id
            )
            conditions.append(condition)

    new_item = ProhibitedItemCreate(
        item_name=item_name,
        image_path=image_path,
        subcategory_id=subcategory_id,
        conditions=conditions
    )

    await create_prohibited_item_with_conditions(db, new_item)

    return {"message": "Item with conditions created successfully"}

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
    item = get_prohibited_item_by_id(db=db, id=item_id)
    if item is None:
        await create_search_history(db, search_term=f"id: {item_id}")
        return JSONResponse(content=ItemNotFound(message=f"id : {item_id} is not found").model_dump(), 
                            status_code=404, 
                            media_type="application/json")
    
    await create_search_history(db, search_term=item.item_name, prohibited_item_id=item.id)

    # 조건을 조회
    conditions = get_item_conditions(db, item.id, is_international, is_domestic)

    cabin_conditions = [condition.condition for condition in conditions if condition.field_option.option == "cabin"]
    trust_conditions = [condition.condition for condition in conditions if condition.field_option.option == "trust"]
    
    cabin_allowed = [condition.allowed for condition in conditions if condition.field_option.option == "cabin"]
    trust_allowed = [condition.allowed for condition in conditions if condition.field_option.option == "trust"]

    cabin_status = '△' if True in cabin_allowed and False in cabin_allowed else ('O' if all(c == True for c in cabin_allowed) else 'X')
    trust_status = '△' if True in trust_allowed and False in trust_allowed else ('O' if all(c == True for c in trust_allowed) else 'X')

    result = {
        "id": item.id,
        "category": item.subcategory.category.name,
        "subcategory": item.subcategory.name,
        "item_name": item.item_name,
        "image_path": item.image_path,
        "flight_option": conditions[0].flight_option.option if conditions else None,
        "cabin": {
            "availability": cabin_status,
            "condition_description": cabin_conditions
        },
        "trust": {
            "availability": trust_status,
            "condition_description": trust_conditions
        }
    }

    return result

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
    item = get_condition_by_name(db=db, name=search_term)
    if not item:
        await create_search_history(db, search_term=search_term)
        return JSONResponse(content=ItemNotFound(message=f"Item : {search_term} is not found").model_dump(), 
                            status_code=404, 
                            media_type="application/json")
    
    
    await create_search_history(db, search_term=search_term, prohibited_item_id=item.id)
    conditions = get_item_conditions(db=db, prohibited_item_id=item.id, is_domestic=is_domestic, is_international=is_international )

    cabin_conditions = [condition.condition for condition in conditions if condition.field_option.option == "cabin"]
    trust_conditions = [condition.condition for condition in conditions if condition.field_option.option == "trust"]
        
    cabin_allowed = [condition.allowed for condition in conditions if condition.field_option.option == "cabin"]
    trust_allowed = [condition.allowed for condition in conditions if condition.field_option.option == "trust"]

    cabin_status = '△' if True in cabin_allowed and False in cabin_allowed else ('O' if all(c == True for c in cabin_allowed) else 'X')
    trust_status = '△' if True in trust_allowed and False in trust_allowed else ('O' if all(c == True for c in trust_allowed) else 'X')
    
    item_dict = {
            "id": item.id,
            "category": item.subcategory.category.name,
            "subcategory": item.subcategory.name,
            "item_name": item.item_name,
            "image_path": item.image_path,
            "flight_option": conditions[0].flight_option.option,
            "cabin": {
                "availability": cabin_status,
                "condition_description": cabin_conditions
            },
            "trust": {
                "availability": trust_status,
                "condition_description": trust_conditions
            }
        }
    
    return SearchResponse(search_term=search_term, items=[item_dict])

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

@app.get("/search_history", 
         response_model=List[SearchHistoryResponse], 
         summary="검색 기록을 횟수 순으로 반환하는 API",
         description="ID가 있는 검색 기록 중 검색 횟수가 많은 순서대로 입력받은 수 만큼 반환합니다.",
         status_code=200)
async def get_search_history(
    limit: int = Query(10, description="출력할 검색어 수", ge=1),
    db: Session = Depends(get_db)
):
    search_histories = get_top_search_histories(db=db, limit=limit)
    return [SearchHistoryResponse(
        search_term=history.search_term,
        prohibited_item_id=history.prohibited_item_id
    ) for history in search_histories]

@app.post("/subcategories/")
async def create_subcategory(
    subcategory: SubcategoryCreate,
    db: Session = Depends(get_db)
):

    await insert_subcategory(db, subcategory=subcategory)

    return {"message": "성공적으로 생성되었습니다"}

@app.get("/categories/", response_model=List[Category])
async def read_categories(db: Session = Depends(get_db)):
    categories = get_categories(db)
    return categories

@app.get("/subcategories/", response_model=List[Subcategory])
async def read_subcategories(db: Session = Depends(get_db)):
    subcategories = get_subcategories(db)
    return subcategories

@app.get("/flight_options/", response_model=List[FlightOption])
async def read_flight_options(db: Session = Depends(get_db)):
    flight_options = get_flight_options(db)
    return flight_options

@app.get("/field_options/", response_model=List[FieldOption])
async def read_field_options(db: Session = Depends(get_db)):
    field_options = get_field_options(db)
    return field_options