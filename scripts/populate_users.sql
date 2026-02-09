-- Script to populate 1 million users in the database
-- Usage: psql -U <user> -d <database> -f scripts/populate_users.sql
-- Or: psql postgresql://<user>:<password>@<host>:<port>/<database> -f scripts/populate_users.sql

-- Disable autocommit and set performance settings for faster inserts
BEGIN;
SET synchronous_commit = OFF;

-- Insert 1 million users using generate_series
-- Using MD5 hash of the id to ensure uniqueness while being deterministic
INSERT INTO users (id, username, name, email)
SELECT 
    generate_series(1, 1000000) AS id,
    'user_' || generate_series(1, 1000000) || '_' || substr(md5(generate_series(1, 1000000)::text), 1, 8) AS username,
    'User ' || generate_series(1, 1000000) AS name,
    'user_' || generate_series(1, 1000000) || '_' || substr(md5(generate_series(1, 1000000)::text), 9, 8) || '@example.com' AS email;

COMMIT;

-- Reset settings
RESET synchronous_commit;

-- Verify the count
SELECT COUNT(*) AS total_users FROM users;

-- Show a sample of inserted users
SELECT id, username, name, email FROM users ORDER BY id LIMIT 10;
