import os

import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute(
    """

CREATE USER app_user WITH LOGIN PASSWORD 'dummy_password';
GRANT CREATE ON DATABASE app TO app_user;

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100),
    password VARCHAR(100),
    admin BOOLEAN,
    validated BOOLEAN,
    updated_at TIMESTAMP default now(),
    created_at DATE default now(),
    UNIQUE (username)
);
GRANT SELECT, INSERT, DELETE, UPDATE, REFERENCES on TABLE users to app_user;
GRANT USAGE on SEQUENCE users_id_seq TO app_user;

-- Create Admin user by default.
INSERT INTO users (username, password, admin, validated) VALUES ('admin', 'admin', true, false);
"""
)

conn.commit()
cur.close()
conn.close()
