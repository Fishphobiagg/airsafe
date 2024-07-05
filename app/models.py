from sqlalchemy import Column, Integer, String, Text, Boolean, BigInteger, TIMESTAMP, ForeignKey
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
    category = Column(String, index=True)
    item_name = Column(String, index=True)
    cabin = Column(Boolean, index=True)
    trust = Column(Boolean, index=True)
    description = Column(Text)
    search_vector = Column(TSVector, nullable=False)
    search_histories = relationship("SearchHistory", back_populates="prohibited_item")

class Category(Base):
    __tablename__ = "category"
    id = Column(BigInteger, primary_key=True, index=True)
    category = Column(String(20), index=True)
    image = Column(String(255), nullable=True)

class SearchHistory(Base):
    __tablename__ = "search_history"
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    search_term = Column(String(255))
    search_date = Column(TIMESTAMP, default=None)
    prohibited_item_id = Column(BigInteger, ForeignKey('prohibited_items.id'), nullable=True)
    prohibited_item = relationship("ProhibitedItem", back_populates="search_histories")