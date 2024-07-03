CREATE TABLE prohibited_items (
    id SERIAL PRIMARY KEY,
    category VARCHAR(255),
    subcategory VARCHAR(255),
    item_name VARCHAR(255),
    cabin BOOLEAN,
    trust BOOLEAN,
    description TEXT
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