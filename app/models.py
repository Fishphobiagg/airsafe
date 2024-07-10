from sqlalchemy import Column, Integer, String, Text, Boolean, BigInteger, TIMESTAMP, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import UserDefinedType
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import relationship

Base = declarative_base()

class TSVector(UserDefinedType):
    cache_ok = True  # 추가된 부분

    def get_col_spec(self):
        return 'TSVECTOR'

@compiles(TSVector, 'postgresql')
def compile_tsvector(element, compiler, **kw):
    return "TSVECTOR"

class Category(Base):
    __tablename__ = "category"
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String(20), index=True)
    image = Column(String(255), nullable=True)

    subcategories = relationship("Subcategory", back_populates="category")

class Subcategory(Base):
    __tablename__ = "subcategory"
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    category_id = Column(BigInteger, ForeignKey('category.id'))
    name = Column(String(50), index=True)
    search_vector = Column(TSVector, nullable=False)
    
    category = relationship("Category", back_populates="subcategories")
    prohibited_items = relationship("ProhibitedItem", back_populates="subcategory")

class ProhibitedItem(Base):
    __tablename__ = "prohibited_items"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    subcategory_id = Column(BigInteger, ForeignKey('subcategory.id'))
    item_name = Column(String, index=True)
    image_path = Column(String(255), nullable=True)
    search_vector = Column(TSVector, nullable=False)

    subcategory = relationship("Subcategory", back_populates="prohibited_items")
    search_histories = relationship("SearchHistory", back_populates="prohibited_item")
    conditions = relationship("Condition", back_populates="prohibited_item")

class Condition(Base):
    __tablename__ = "conditions"
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    prohibited_item_id = Column(BigInteger, ForeignKey('prohibited_items.id'))
    is_international = Column(Boolean, nullable=True)
    is_domestic = Column(Boolean, nullable=True)
    cabin = Column(String(1))  # 'O', '△', 'X'
    trust = Column(String(1))  # 'O', '△', 'X'
    condition_description = Column(Text)

    prohibited_item = relationship("ProhibitedItem", back_populates="conditions")

class SearchHistory(Base):
    __tablename__ = "search_history"
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    search_term = Column(String(255))
    prohibited_item_id = Column(BigInteger, ForeignKey('prohibited_items.id'), nullable=True)
    search_count = Column(Integer, default=1)
    
    prohibited_item = relationship("ProhibitedItem", back_populates="search_histories")

class Suggestion(Base):
    __tablename__ = "suggestions"
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    suggestion_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=func.now())