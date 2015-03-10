CREATE TABLE books (
  isbn		char(13) NOT NULL PRIMARY KEY, -- ISBNs contain 13 digits but the constraint can not be expressed
  title		text NOT NULL,
  author	varchar(128) NOT NULL, -- author should contain name and surname but the constraint can not be expressed
  price		integer NOT NULL CHECK(price >= 0), --price in cents, price cannot be less than 0
  qty_stock	integer NOT NULL CHECK(qty_stock >= 0) -- number of units available for shipping cannot be less than 0
);

CREATE TABLE customer (
  cid			integer NOT NULL PRIMARY KEY,
  shipping_address	text NOT NULL, -- address should contain city, street, postal code but the constraint cannot be expressed
  billin_address	text NOT NULL, -- address should contain city, street, postal code but the constraint cannot be expressed
  cname			varchar(128) NOT NULL UNIQUE -- "cname" should contain first name and last name of customer but the constraint cannot be expressed
);

CREATE TABLE orders (
  oid		integer NOT NULL PRIMARY KEY,
  qty		smallint NOT NULL CHECK(qty> 0), -- number of units of a book the customer has ordered should be more than 0
  order_date	timestamptz NOT NULL,
  ship_date	timestamptz NOT NULL
);

CREATE TABLE publisher (
  pid		integer NOT NULL PRIMARY KEY,
  pname		varchar(128) NOT NULL,
  phone_number	char(10) NOT NULL, -- Phone number has 10 digits but the constraint cannot be expressed
  address	text NOT NULL -- address should contain city, street, postal code but the constraint cannot be expressed
);

CREATE TABLE review (
  isbn		char(13) NOT NULL,
  cid		integer NOT NULL,
  date		timestamptz NOT NULL,
  text		text NOT NULL,
  rating	smallint NOT NULL CHECK(rating>=0), -- rating cannot be less than 0
  PRIMARY KEY (isbn,cid),
  FOREIGN KEY (isbn) REFERENCES books(isbn),
  FOREIGN KEY (cid) REFERENCES customer(cid)
);

CREATE TABLE discounts (
  amount	smallint NOT NULL CHECK (amount >= 0), -- amount cannot be less than 0
  isbn		char(13) NOT NULL,
  until		timestamptz NOT NULL CHECK(until > current_timestamp), -- "until" time should be later than current time
  PRIMARY KEY (amount, isbn),
  FOREIGN KEY (isbn) REFERENCES books(isbn)
);

CREATE TABLE featured_books (
  isbn		char(13) NOT NULL PRIMARY KEY,
  until		timestamptz NOT NULL CHECK(until > current_timestamp), -- "until" time should be later than current time
  FOREIGN KEY (isbn) REFERENCES books(isbn)
);

CREATE TABLE recently_viewed (
  cid		integer NOT NULL,
  isbn		char(13) NOT NULL,
  date		timestamptz NOT NULL CHECK(date <= current_timestamp), -- "date" time should be earlier than current time
  PRIMARY KEY (cid,isbn),
  FOREIGN KEY (cid) REFERENCES customer(cid),
  FOREIGN KEY (isbn) REFERENCES books(isbn)
);

CREATE TABLE wants (
  cid		integer NOT NULL,
  isbn		char(13) NOT NULL,
  since		timestamptz NOT NULL CHECK(since <= current_timestamp), -- "since" time should be earlier than current time
  PRIMARY KEY (cid,isbn),
  FOREIGN KEY (cid) REFERENCES customer(cid),
  FOREIGN KEY (isbn) REFERENCES books(isbn)
);

CREATE TABLE ordered (
  oid		integer NOT NULL,
  cid		integer NOT NULL,
  isbn		char(13) NOT NULL,
  PRIMARY KEY (oid,cid,isbn),
  FOREIGN KEY (oid) REFERENCES orders(oid),
  FOREIGN KEY (cid) REFERENCES customer(cid),
  FOREIGN KEY (isbn) REFERENCES books(isbn)
);

CREATE TABLE publishes (
  pid		integer NOT NULL,
  isbn		char(13) NOT NULL,
  year		smallint NOT NULL,
  PRIMARY KEY (pid,isbn),
  FOREIGN KEY (pid) REFERENCES publisher(pid),
  FOREIGN KEY (isbn) REFERENCES books(isbn)
);
