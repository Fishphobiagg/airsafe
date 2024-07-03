from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

SQLALCHEMY_DATABASE_URL = settings.database_url

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 트리거를 사용하여 search_vector 업데이트 설정

def create_trigger(conn):
    # Check if the trigger already exists
    trigger_exists_query = """
        SELECT EXISTS (
            SELECT 1 
            FROM pg_trigger 
            WHERE tgname = 'tsvectorupdate'
        );
    """
    trigger_exists = conn.execute(text(trigger_exists_query)).scalar()

    if not trigger_exists:
        conn.execute(text("""
            CREATE OR REPLACE FUNCTION update_search_vector() RETURNS trigger AS $$
            BEGIN
                NEW.search_vector :=
                    to_tsvector('pg_catalog.english', coalesce(NEW.category, '') || ' ' ||
                                coalesce(NEW.subcategory, '') || ' ' ||
                                coalesce(NEW.item_name, '') || ' ' ||
                                coalesce(NEW.description, ''));
                RETURN NEW;
            END
            $$ LANGUAGE plpgsql;
        """))

        conn.execute(text("""
            CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
            ON prohibited_items FOR EACH ROW EXECUTE PROCEDURE update_search_vector();
        """))

        
def init_db():
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        create_trigger(conn)