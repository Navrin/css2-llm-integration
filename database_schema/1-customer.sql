CREATE TABLE customer
(
    id SERIAL PRIMARY KEY,
    first_name VARCHAR,
    last_name VARCHAR,
    email VARCHAR,
    phone VARCHAR,

    CONSTRAINT has_account CHECK (email IS NOT NULL or phone IS NOT NULL)
)