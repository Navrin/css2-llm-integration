CREATE TABLE sale (
    id SERIAL PRIMARY KEY,
    customer_id SERIAL REFERENCES customer(id)
);

CREATE TABLE sale_item (
    id SERIAL PRIMARY KEY,
    sale_id SERIAL REFERENCES sale(id),
    product_id SERIAL REFERENCES product(id),
    quantity INTEGER
--     CONSTRAINT sale_item_pk PRIMARY KEY (sale_id, product_id)
);

CREATE TABLE sale_item_modifier (
    sale_item_id SERIAL REFERENCES sale_item(id),
    modifier_id SERIAL REFERENCES modifier(id),
    CONSTRAINT sale_item_modifier_pk PRIMARY KEY (sale_item_id, modifier_id)
);