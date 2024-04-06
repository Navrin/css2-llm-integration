CREATE TABLE product_review (
    id SERIAL PRIMARY KEY UNIQUE,
    product_id SERIAL REFERENCES product(id),
    customer_name varchar(100),
    review VARCHAR NOT NULL,
    rating int NOT NULL,
    CHECK (rating BETWEEN 1 AND 5)
)