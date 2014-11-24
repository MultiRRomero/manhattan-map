
CREATE TABLE addresses (
    id INTEGER PRIMARY KEY, -- This will auto increment
    address TEXT NOT NULL,
    latitude INT DEFAULT NULL,
    longitude INT DEFAULT NULL
);

-- INSERT INTO addresses (address, latitude, longitude) VALUES ('a', 1, -1);
-- INSERT INTO addresses (address, latitude, longitude) VALUES ('b', 2, -2);

