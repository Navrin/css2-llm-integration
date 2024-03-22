CREATE TABLE product (
    id SERIAL PRIMARY KEY UNIQUE,
    name varchar(50) NOT NULL,
    description varchar,
    price float NOT NULL
);


INSERT INTO product (id, name, description, price) VALUES (1, 'Arctic Freeze', 'Indulge in the refreshing taste of our Arctic Freeze Blueberry Shake. Made with plump, juicy blueberries and creamy vanilla ice cream, this frosty treat is sure to take your taste buds on a journey to the arctic. Perfect for hot summer days or as a sweet indulgence any time of year, our Arctic Freeze Blueberry Shake is a must-try for any blueberry lover. So go ahead, sip and savor the cool, fruity goodness of our Arctic Freeze Blueberry Shake today!', 9.99);
INSERT INTO modifier (id, name, price) VALUES (1, 'Dairy Free', 3.0);

CREATE TABLE product_modifier (
    product_id SERIAL REFERENCES product(id),
    modifier_id SERIAL REFERENCES modifier(id),
    CONSTRAINT product_modifier_pk PRIMARY KEY (product_id, modifier_id)
);
INSERT INTO product_modifier (product_id, modifier_id) VALUES (1, 1);

