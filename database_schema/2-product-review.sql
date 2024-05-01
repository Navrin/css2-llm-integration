CREATE TABLE product_review (
    id INTEGER PRIMARY KEY UNIQUE GENERATED ALWAYS AS IDENTITY,
    product_id INTEGER REFERENCES product(id),
    name varchar(100),
    review VARCHAR NOT NULL,
    rating int NOT NULL,
    CHECK (rating BETWEEN 1 AND 5)
)