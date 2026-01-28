-- Database schema for household donation tracking

CREATE TABLE IF NOT EXISTS donors (
    id SERIAL PRIMARY KEY,
    last_name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    donor_id INT NOT NULL REFERENCES donors(id) ON DELETE CASCADE,
    month SMALLINT NOT NULL,
    year SMALLINT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recorded_by BIGINT NOT NULL,
    UNIQUE (donor_id, month, year)
);

CREATE TABLE IF NOT EXISTS admins (
    telegram_id BIGINT PRIMARY KEY,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
