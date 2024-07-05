-- Category 테이블 생성
CREATE TABLE category (
    id BIGINT PRIMARY KEY,
    category VARCHAR(20) NOT NULL,
    image VARCHAR(255)
);

-- ProhibitedItems 테이블 생성
CREATE TABLE prohibited_items (
    id BIGINT PRIMARY KEY,
    category VARCHAR(255),
    item_name VARCHAR(255),
    cabin BOOLEAN,
    trust BOOLEAN,
    description TEXT,
    search_vector TSVECTOR NOT NULL
);

-- SearchHistory 테이블 생성
CREATE TABLE search_history (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    search_term VARCHAR(255),
    search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    prohibited_item_id BIGINT REFERENCES prohibited_items(id)
);


CREATE EXTENSION IF NOT EXISTS pg_trgm;

ALTER TABLE prohibited_items ADD COLUMN search_vector tsvector;

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

CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
ON prohibited_items FOR EACH ROW EXECUTE FUNCTION update_search_vector();

CREATE INDEX idx_search_vector ON prohibited_items USING gin(search_vector);