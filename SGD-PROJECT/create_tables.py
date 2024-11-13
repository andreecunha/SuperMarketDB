import psycopg2
import base64
import os

def db_connection():
    decoded = base64.b64decode(os.environ.get('pass'))
    db = psycopg2.connect(
        user='trabalhoSGD',
        password= int(decoded),
        host='127.0.0.1',
        port='5432',
        database='TrabalhoSGD'
    )

    return db

	
conn = db_connection()
c = conn.cursor()

c.execute('''
CREATE TABLE store (
	id	 INTEGER,
	address VARCHAR(512) NOT NULL,
	phone	 BIGINT NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE employee (
	store_id	 INTEGER NOT NULL,
	person_nif BIGINT,
	PRIMARY KEY(person_nif)
);

CREATE TABLE purchase (
	id				 INTEGER,
	valor			 FLOAT(8) ,
	data			 DATE ,
	cashier_employee_person_nif BIGINT NOT NULL,
	store_id			 INTEGER,
	PRIMARY KEY(id)
);

CREATE TABLE customer (
	person_nif BIGINT,
	PRIMARY KEY(person_nif)
);

CREATE TABLE product (
	id	 INTEGER,
	type	 VARCHAR(512) NOT NULL,
	name	 VARCHAR(512) NOT NULL,
	price FLOAT(8) NOT NULL,
	description VARCHAR(512) NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE product_purchase (
	quantidade	 INTEGER,
	price		 FLOAT(8),
	discount_value FLOAT(8),
	product_id	 INTEGER,
	purchase_id	 INTEGER,
	PRIMARY KEY(product_id,purchase_id)
);

CREATE TABLE stock (
	stock	 INTEGER NOT NULL,
	product_id INTEGER,
	store_id	 INTEGER,
	PRIMARY KEY(product_id,store_id)
);

CREATE TABLE price_history (
	price_id	 SERIAL,
	price	 INTEGER NOT NULL,
	start_date DATE NOT NULL,
	end_date	 DATE,
	product_id INTEGER,
	PRIMARY KEY(price_id,product_id)
);

CREATE TABLE purchase_promotion (
	promotion_id INTEGER,
	PRIMARY KEY(promotion_id)
);

CREATE TABLE product_promotion (
	promotion_id INTEGER,
	PRIMARY KEY(promotion_id)
);

CREATE TABLE promotion (
	id	 INTEGER,
	start_date DATE NOT NULL,
	end_date	 DATE NOT NULL,
	discount	 FLOAT(8) NOT NULL,
	name	 VARCHAR(512) NOT NULL,
	store_id	 INTEGER NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE cashier (
	employee_person_nif BIGINT,
	PRIMARY KEY(employee_person_nif)
);

CREATE TABLE repositor (
	employee_person_nif BIGINT,
	PRIMARY KEY(employee_person_nif)
);

CREATE TABLE chefe (
	employee_person_nif BIGINT,
	PRIMARY KEY(employee_person_nif)
);

CREATE TABLE person (
	nif	 BIGINT,
	name	 VARCHAR(512) NOT NULL,
	phone	 BIGINT NOT NULL,
	address VARCHAR(512) NOT NULL,
	PRIMARY KEY(nif)
);

CREATE TABLE promotion_discount (
	valor				 FLOAT(8) NOT NULL,
	purchase_promotion_promotion_id	 INTEGER NOT NULL,
	purchase_id			 INTEGER,
	PRIMARY KEY(purchase_id)
);

CREATE TABLE product_promotion_product_purchase (
	product_promotion_promotion_id INTEGER NOT NULL,
	product_purchase_product_id	 INTEGER,
	product_purchase_purchase_id	 INTEGER,
	PRIMARY KEY(product_purchase_product_id,product_purchase_purchase_id),
	FOREIGN KEY (product_purchase_product_id, product_purchase_purchase_id) REFERENCES product_purchase(product_id, purchase_id)
);

CREATE TABLE purchase_promotion_purchase (
	purchase_promotion_promotion_id INTEGER NOT NULL,
	purchase_id			 INTEGER,
	PRIMARY KEY(purchase_id)
);

CREATE TABLE customer_purchase (
	customer_person_nif BIGINT NOT NULL,
	purchase_id	 INTEGER,
	PRIMARY KEY(purchase_id)
);

ALTER TABLE employee ADD CONSTRAINT employee_fk1 FOREIGN KEY (store_id) REFERENCES store(id);
ALTER TABLE employee ADD CONSTRAINT employee_fk2 FOREIGN KEY (person_nif) REFERENCES person(nif);
ALTER TABLE purchase ADD CONSTRAINT purchase_fk1 FOREIGN KEY (cashier_employee_person_nif) REFERENCES cashier(employee_person_nif);
ALTER TABLE purchase ADD CONSTRAINT purchase_fk2 FOREIGN KEY (store_id) REFERENCES store(id);
ALTER TABLE customer ADD CONSTRAINT customer_fk1 FOREIGN KEY (person_nif) REFERENCES person(nif);
ALTER TABLE product_purchase ADD CONSTRAINT product_purchase_fk1 FOREIGN KEY (product_id) REFERENCES product(id);
ALTER TABLE product_purchase ADD CONSTRAINT product_purchase_fk2 FOREIGN KEY (purchase_id) REFERENCES purchase(id);
ALTER TABLE stock ADD CONSTRAINT stock_fk1 FOREIGN KEY (product_id) REFERENCES product(id);
ALTER TABLE stock ADD CONSTRAINT stock_fk2 FOREIGN KEY (store_id) REFERENCES store(id);
ALTER TABLE price_history ADD CONSTRAINT price_history_fk1 FOREIGN KEY (product_id) REFERENCES product(id);
ALTER TABLE purchase_promotion ADD CONSTRAINT purchase_promotion_fk1 FOREIGN KEY (promotion_id) REFERENCES promotion(id);
ALTER TABLE product_promotion ADD CONSTRAINT product_promotion_fk1 FOREIGN KEY (promotion_id) REFERENCES promotion(id);
ALTER TABLE promotion ADD CONSTRAINT promotion_fk1 FOREIGN KEY (store_id) REFERENCES store(id);
ALTER TABLE cashier ADD CONSTRAINT cashier_fk1 FOREIGN KEY (employee_person_nif) REFERENCES employee(person_nif);
ALTER TABLE repositor ADD CONSTRAINT repositor_fk1 FOREIGN KEY (employee_person_nif) REFERENCES employee(person_nif);
ALTER TABLE chefe ADD CONSTRAINT chefe_fk1 FOREIGN KEY (employee_person_nif) REFERENCES employee(person_nif);
ALTER TABLE promotion_discount ADD CONSTRAINT promotion_discount_fk1 FOREIGN KEY (purchase_promotion_promotion_id) REFERENCES purchase_promotion(promotion_id);
ALTER TABLE promotion_discount ADD CONSTRAINT promotion_discount_fk2 FOREIGN KEY (purchase_id) REFERENCES purchase(id);
ALTER TABLE product_promotion_product_purchase ADD CONSTRAINT product_promotion_product_purchase_fk1 FOREIGN KEY (product_promotion_promotion_id) REFERENCES product_promotion(promotion_id);
ALTER TABLE purchase_promotion_purchase ADD CONSTRAINT purchase_promotion_purchase_fk1 FOREIGN KEY (purchase_promotion_promotion_id) REFERENCES purchase_promotion(promotion_id);
ALTER TABLE purchase_promotion_purchase ADD CONSTRAINT purchase_promotion_purchase_fk2 FOREIGN KEY (purchase_id) REFERENCES purchase(id);
ALTER TABLE customer_purchase ADD CONSTRAINT customer_purchase_fk1 FOREIGN KEY (customer_person_nif) REFERENCES customer(person_nif);
ALTER TABLE customer_purchase ADD CONSTRAINT customer_purchase_fk2 FOREIGN KEY (purchase_id) REFERENCES purchase(id);
''')

conn.commit()
conn.close()