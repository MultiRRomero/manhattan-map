
CREATE TABLE if not exists addresses (
  id INTEGER PRIMARY KEY, -- This will auto increment
  address TEXT NOT NULL,
  latitude INT DEFAULT NULL,
  longitude INT DEFAULT NULL
);

-- INSERT INTO addresses (address, latitude, longitude) VALUES ('a', 1, -1);
-- INSERT INTO addresses (address, latitude, longitude) VALUES ('b', 2, -2);

CREATE TABLE if not exists apartments (
  id INTEGER PRIMARY KEY,
  `source` VARCHAR(255) NOT NULL, -- renthop, craigslist, nybits
  title TEXT NOT NULL,
  price INT NOT NULL,
  url TEXT NOT NULL,
  address_id INT NOT NULL,
  has_fee BOOLEAN,
  blurb TEXT,
  posting_date VARCHAR(255),
  sqft INT
);

CREATE TABLE if not exists search_log (
  timestamp INT NOT NULL,
  apartment_id INT NOT NULL
);

CREATE TABLE if not exists annotations (
  timestamp INT NOT NULL,
  url TEXT NOT NULL,
  rating INT,
  comments TEXT,
  contacted TEXT
);
