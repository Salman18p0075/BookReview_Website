DROP TABLE IF EXISTS "users";
DROP SEQUENCE IF EXISTS users_id_seq;
CREATE SEQUENCE users_id_seq START WITH 1 INCREMENT BY 1 MINVALUE 1  CACHE 1;


CREATE TABLE users(
    id int DEFAULT nextval('users_id_seq') NOT NULL,
    username VARCHAR(100) NOT NULL,
    passwords varchar(100) NOT NULL,
    CONSTRAINT "user_name" PRIMARY KEY("username")
);


DROP TABLE IF EXISTS books;
DROP SEQUENCE IF EXISTS books_id_seq;
CREATE SEQUENCE books_id_seq  START WITH 1 INCREMENT BY 1 MINVALUE 1 CACHE 1;

CREATE TABLE books(
    id int DEFAULT nextval('books_id_seq') NOT NULL,
    isbn  varchar(200) PRIMARY KEY,
    title varchar(100) NOT NULL,
    author varchar(100) NOT NULL,
    year int NOT NULL
     

);

DROP TABLE IF EXISTS reviews;
DROP SEQUENCE IF EXISTS reviews_id_seq;
CREATE SEQUENCE reviews_id_seq  START WITH 1 INCREMENT BY 1 MINVALUE 1 CACHE 1;

CREATE TABLE reviews(
    id int DEFAULT nextval('reviews_id_seq') PRIMARY KEY,
    username varchar(100) NOT NULL,
    book_id varchar(200) NOT NULL,
    comment text NOT NULL,
    rating int NOT NULL,
    date timestamp DEFAULT now() NOT NULL,
    CONSTRAINT "user_id_fk" FOREIGN KEY("username") REFERENCES users("username") ON DELETE CASCADE,
    CONSTRAINT "book_id_fk" FOREIGN KEY("book_id") REFERENCES books("isbn") on DELETE CASCADE
);

