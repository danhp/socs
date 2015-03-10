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
