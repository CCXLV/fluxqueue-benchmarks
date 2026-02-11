-- Script to populate 1 million users in the database using emails from a text file
-- Usage: psql -U <user> -d <database> -f scripts/populate_users.sql
-- Or:    psql postgresql://<user>:<password>@<host>:<port>/<database> -f scripts/populate_users.sql
--
-- Requirements:
--   - A plain text file with one email per line, e.g. scripts/emails.txt
--   - At least 1,000,000 lines (emails) in that file if you want 1M users
--
-- Example to generate some emails (bash):
--   seq 1 1000000 | sed 's/^/user_/' | sed 's/$/@example.com/' > scripts/emails.txt

-- Disable autocommit and set performance settings for faster inserts
BEGIN;
SET synchronous_commit = OFF;

-- Wipe existing data so we can deterministically repopulate
TRUNCATE TABLE commission_results, commission_rates, users RESTART IDENTITY;

-- Load emails from a text file into a temporary table.
-- NOTE: The path is relative to where you run psql from.
-- Adjust the path if your emails file lives elsewhere.
CREATE TEMP TABLE temp_emails (
    email text
);

\copy temp_emails(email) FROM 'scripts/emails.txt' WITH (FORMAT text);

-- Number the emails so we can pair them with generated ids.
WITH numbered_emails AS (
    SELECT
        email,
        row_number() OVER (ORDER BY email) AS rn
    FROM temp_emails
),
ids AS (
    SELECT generate_series(1, 1000000) AS id
)
INSERT INTO users (id, username, name, email, earnings)
SELECT
    i.id,
    'user_' || i.id AS username,
    'User ' || i.id AS name,
    ne.email,
    -- earnings: mix of thousands and millions
    CASE
        WHEN random() < 0.7
            THEN (1_000 + floor(random() * 99_000))::bigint     -- 1k..100k
        ELSE (1_000_000 + floor(random() * 9_000_000))::bigint -- 1M..10M
    END AS earnings
FROM ids AS i
JOIN numbered_emails AS ne
    ON ne.rn = i.id;

-- Populate commission_rates for each user with a reasonable random base_rate and rate_type.
--  - If rate_type = 'FLAT':       base_rate between 100 and 10_000
--  - If rate_type = 'PERCENTAGE': base_rate between 1 and 15
WITH user_rates AS (
    SELECT
        u.id AS user_id,
        CASE
            WHEN random() < 0.5 THEN 'FLAT'::ratetype ELSE 'PERCENTAGE'::ratetype
        END AS rate_type
    FROM users AS u
)
INSERT INTO commission_rates (user_id, base_rate, rate_type)
SELECT
    ur.user_id,
    CASE
        WHEN ur.rate_type = 'FLAT'::ratetype
            THEN (100 + floor(random() * 9_901))::int  -- flat:    100..10_000
        ELSE (1 + floor(random() * 15))::int           -- percent: 1..15
    END AS base_rate,
    ur.rate_type
FROM user_rates AS ur;

COMMIT;

-- Reset settings
RESET synchronous_commit;

-- Verify the count
SELECT COUNT(*) AS total_users FROM users;

-- Show a sample of inserted users
SELECT id, username, name, email FROM users ORDER BY id LIMIT 10;
