COPY customer FROM '/data/0-customer.csv' WITH (FORMAT csv, DELIMITER ',', HEADER MATCH, DEFAULT '<>');
COPY modifier FROM '/data/0-modifier.csv' WITH (FORMAT csv, DELIMITER ',', HEADER MATCH, DEFAULT '<>');
COPY product FROM '/data/0-product.csv' WITH (FORMAT csv, DELIMITER ',', HEADER MATCH, DEFAULT '<>');
COPY store FROM '/data/0-store.csv' WITH (FORMAT csv, DELIMITER ',', HEADER MATCH, DEFAULT '<>');
COPY product_modifier FROM '/data/1-product_modifier.csv' WITH (FORMAT csv, DELIMITER ',', HEADER MATCH, DEFAULT '<>');
COPY sale FROM '/data/1-sale.csv' WITH (FORMAT csv, DELIMITER ',', HEADER MATCH, DEFAULT '<>');
COPY sale_item FROM '/data/2-sale_item.csv' WITH (FORMAT csv, DELIMITER ',', HEADER MATCH, DEFAULT '<>');
COPY sale_item_modifier FROM '/data/3-sale_item_modifier.csv' WITH (FORMAT csv, DELIMITER ',', HEADER MATCH, DEFAULT '<>');
COPY product_review FROM '/data/4-product_review.csv' WITH (FORMAT csv, DELIMITER ',', HEADER MATCH, DEFAULT '<>');