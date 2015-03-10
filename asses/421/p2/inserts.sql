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

INSERT INTO featured_books VALUES(1, current_timestamp - interval + '5 days');
INSERT INTO featured_books VALUES(6, current_timestamp - interval + '7 days');
INSERT INTO featured_books VALUES(3, current_timestamp - interval + '4 days');
