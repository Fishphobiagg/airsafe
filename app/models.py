from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import UserDefinedType
from sqlalchemy.ext.compiler import compiles

Base = declarative_base()

class TSVector(UserDefinedType):
    def get_col_spec(self):
        return 'TSVECTOR'

@compiles(TSVector, 'postgresql')
def compile_tsvector(element, compiler, **kw):
    return "TSVECTOR"

class ProhibitedItem(Base):
    __tablename__ = "prohibited_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(String, index=True)
    subcategory = Column(String, index=True)
    item_name = Column(String, index=True)
    cabin = Column(Boolean, index=True)
    trust = Column(Boolean, index=True)
    description = Column(Text)
    search_vector = Column(TSVector, nullable=False)