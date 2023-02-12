DROP TABLE IF EXISTS user;
-- DROP TABLE IF EXISTS post;
-- DROP TABLE IF EXISTS product_inventory;
-- DROP TABLE IF EXISTS product_def;
-- DROP TABLE IF EXISTS material;
-- DROP TABLE IF EXISTS manufacture_record;
-- DROP TABLE IF EXISTS transport;
-- DROP TABLE IF EXISTS customer;
-- DROP TABLE IF EXISTS seller;
-- DROP TABLE IF EXISTS sell_record;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  role TEXT NOT NULL
);
--
-- CREATE TABLE post (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   author_id INTEGER NOT NULL,
--   created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
--   title TEXT NOT NULL,
--   body TEXT NOT NULL
-- );
--
-- CREATE TABLE product_inventory(
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     product_id INTEGER UNIQUE NOT NULL,
--     amount DOUBLE
-- );
--
-- CREATE TABLE product_def(
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     name TEXT UNIQUE NOT NULL,
--     unit TEXT NOT NULL,
--     specification TEXT,
--     price DOUBLE,
--     creator TEXT NOT NULL,
--     material_cost_conf TEXT
-- );
-- CREATE TABLE transport(
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     sell_record_id INTEGER NOT NULL,
--     amount DOUBLE NOT NULL,
--     address TEXT NOT NULL,
--     driver_name TEXT NOT NULL,
--     driver_cellphone TEXT
-- );
-- CREATE TABLE customer(
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     name TEXT NOT NULL,
--     cellphone TEXT,
--     city TEXT,
--     province TEXT,
--     address TEXT
-- );
--
-- CREATE TABLE seller(
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     name TEXT NOT NULL,
--     cellphone TEXT
-- );

-- CREATE TABLE sell_record(
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
--     product_id INTEGER NOT NULL ,
--     amount DOUBLE NOT NULL ,
--     seller_id INTEGER NOT NULL,
--     customer_id INTEGER NOT NULL,
--     status TEXT NOT NULL,
--     transported_amount DOUBLE default 0
-- );
--
-- CREATE TABLE material(
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     name TEXT UNIQUE NOT NULL,
--     count INTEGER NOT NULL DEFAULT 0
-- );

-- CREATE TABLE manufacture_record(
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     product_id INTEGER,
--     amount DOUBLE
-- );