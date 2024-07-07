from sqlalchemy import Column, Integer, String, Text, Boolean, BigInteger, TIMESTAMP, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import UserDefinedType
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import relationship

Base = declarative_base()

class TSVector(UserDefinedType):
    def get_col_spec(self):
        return 'TSVECTOR'

@compiles(TSVector, 'postgresql')
def compile_tsvector(element, compiler, **kw):
    return "TSVECTOR"

class ProhibitedItem(Base):
    __tablename__ = "prohibited_items"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    category_id = Column(BigInteger, ForeignKey('category.id'))
    item_name = Column(String, index=True)
    cabin = Column(Boolean, index=True)
    trust = Column(Boolean, index=True)
    description = Column(Text)
    search_vector = Column(TSVector, nullable=False)

    category = relationship("Category", back_populates="prohibited_items")
    search_histories = relationship("SearchHistory", back_populates="prohibited_item")

class Category(Base):
    __tablename__ = "category"
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String(20), index=True)
    image = Column(String(255), nullable=True)

    prohibited_items = relationship("ProhibitedItem", back_populates="category")

class SearchHistory(Base):
    __tablename__ = "search_history"
    id = Column(BigInteger, primary_key=True, index=True)
    search_term = Column(String(255))
    prohibited_item_id = Column(BigInteger, ForeignKey('prohibited_items.id'), nullable=True)
    search_count = Column(Integer, default=1)
    
    prohibited_item = relationship("ProhibitedItem", back_populates="search_histories")

class Suggestion(Base):
    __tablename__ = "suggestions"
    id = Column(BigInteger, primary_key=True, index=True)
    suggestion_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=func.now())