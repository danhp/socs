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

INSERT INTO books VALUES('1', 'Harry Potter', 'JK Rowling', 10, 7);
INSERT INTO books VALUES('2', 'Lord of The Rings', 'JRR Tolkien', 20, 12);
INSERT INTO books VALUES('3', 'The Emperors Handbook', 'Marcus Aurelius', 15, 4);
INSERT INTO books VALUES('4', 'Black Swan', 'Nassim Taleb', 44, 540);
INSERT INTO books VALUES('5', 'We Were Liars', 'E. Lockhart', 25, 0);
INSERT INTO books VALUES('6', 'The Hobbit', 'JRR Tolkien', 25, 0);
INSERT INTO books VALUES('7', 'Hellboy, The Seed of Destruction', 'Mike Mignola', 17, 0);

INSERT INTO customer VALUES(1, '1 McGill College', '11 McGill College', 'John A');
INSERT INTO customer VALUES(2, '2 McGill College', '22 McGill College', 'John B');
INSERT INTO customer VALUES(3, '3 McGill College', '3504 Durocher', 'Mike C');
INSERT INTO customer VALUES(4, '25 Peel', '42 Stanley', 'Ryan J');
INSERT INTO customer VALUES(5, '3489 University', '370 Milton', 'Jessica F');

INSERT INTO wants VALUES(1, '1', current_timestamp - interval '1 hours');
INSERT INTO wants VALUES(2, '1', current_timestamp - interval '2 hours');
INSERT INTO wants VALUES(3, '3', current_timestamp - interval '3 hours');
INSERT INTO wants VALUES(4, '5', current_timestamp - interval '1 hours');
INSERT INTO wants VALUES(5, '1', current_timestamp - interval '2 hours');
INSERT INTO wants VALUES(3, '7', current_timestamp - interval '3 hours');

INSERT INTO publisher VALUES(1, 'Penguin Books', '1112223333', 'A place in the USA');
INSERT INTO publisher VALUES(2, 'Dark Horse Comis', '4445556666', 'Some other place in the USA');
INSERT INTO publisher VALUES(3, 'Dutton Books', '7778889999', 'Anoter other place in the USA');
INSERT INTO publisher VALUES(4, 'McClelland and Stewart', '0001112222', 'A place in Canada');

INSERT INTO publishes VALUES(1, 6, 1999);
INSERT INTO publishes VALUES(1, 5, 2014);
INSERT INTO publishes VALUES(2, 7, 1994);
INSERT INTO publishes VALUES(1, 3, 1980);
INSERT INTO publishes VALUES(4, 4, 1998);

INSERT INTO discounts VALUES(10, 1, current_date + interval '30 days');
INSERT INTO discounts VALUES(15, 3, current_date + interval '30 days');
INSERT INTO discounts VALUES(11, 4, current_date + interval '30 days');
INSERT INTO discounts VALUES(25, 2, current_date + interval '30 days');

INSERT INTO orders VALUES(1, 2, current_date + interval '10 days', current_date + interval '15 days');
INSERT INTO orders VALUES(2, 1, current_date + interval '10 days', current_date + interval '15 days');
INSERT INTO orders VALUES(3, 1, current_date + interval '10 days', current_date + interval '15 days');
INSERT INTO orders VALUES(4, 2, current_date + interval '10 days', current_date + interval '15 days');
INSERT INTO orders VALUES(5, 2, current_date + interval '10 days', current_date + interval '15 days');

INSERT INTO ordered VALUES(1, 1, 6);
INSERT INTO ordered VALUES(1, 1, 5);
INSERT INTO ordered VALUES(2, 3, 2);
INSERT INTO ordered VALUES(3, 3, 3);
INSERT INTO ordered VALUES(4, 4, 2);
INSERT INTO ordered VALUES(4, 4, 7);
INSERT INTO ordered VALUES(5, 4, 7);
INSERT INTO ordered VALUES(5, 4, 2);

INSERT INTO recently_viewed VALUES(1, 1, current_timestamp - interval '3 hours');
INSERT INTO recently_viewed VALUES(1, 4, current_timestamp - interval '3 hours');
INSERT INTO recently_viewed VALUES(1, 7, current_timestamp - interval '3 hours');
INSERT INTO recently_viewed VALUES(3, 4, current_timestamp - interval '3 hours');
INSERT INTO recently_viewed VALUES(3, 5, current_timestamp - interval '3 hours');

INSERT INTO featured_books VALUES(1, current_timestamp + interval '5 days');
INSERT INTO featured_books VALUES(6, current_timestamp + interval '7 days');
INSERT INTO featured_books VALUES(3, current_timestamp + interval '4 days');

-- 1 Customers that bought books by Tolkien.
SELECT c.cname AS tolkien_buyers
    FROM customer as c
    INNER JOIN ordered as o ON c.cid = o.cid
    INNER JOIN (SELECT isbn FROM books WHERE author = 'JRR Tolkien') as tb ON tb.isbn = o.isbn
    GROUP BY c.cname;

-- 2 User that want books that are on sale.
SELECT c.cname as customer, b.title AS discounted_title, d.amount AS discount_amount
    FROM customer as c
    INNER JOIN wants as w ON c.cid = w.cid
    INNER JOIN discounts as d ON d.isbn = w.isbn
    INNER JOIN books as b ON w.isbn = b.isbn
    WHERE d.until > current_date
    ORDER BY b.title;

-- 3 Publishers contact info when books are our of stock
SELECT p.pname AS publisher, p.phone_number, p.address, count(*) AS books_to_order
    FROM publisher as p
    INNER JOIN publishes as pb ON p.pid = pb.pid
    INNER JOIN (SELECT isbn FROM books where qty_stock = 0) as no_stock ON pb.isbn = no_stock.isbn
    GROUP BY p.pname, p.phone_number, p.address;

-- 4 Customers names for those that have bought 2 or more books from Penguin.
SELECT c.cname AS penguin_loyal
    FROM customer AS c
    INNER JOIN ordered AS o ON c.cid = o.cid
    INNER JOIN (SELECT pb.isbn FROM publishes as pb INNER JOIN publisher as p ON pb.pid = p.pid WHERE p.pname = 'Penguin Books') as d_books ON o.isbn = d_books.isbn
    GROUP BY c.cname
    HAVING count(*) >= 2;

-- 5 Books that have 3 or more people who want them.
SELECT b.title AS popular_titles, b.price
    FROM books AS b
    INNER JOIN wants AS w ON b.isbn = w.isbn
    GROUP BY b.title, b.price
    HAVING count(*) >= 3;

DROP TABLE books, customer, orders, publisher, review, discounts, featured_books, recently_viewed, wants, ordered, publishes CASCADE;
