import math
import pandas as pd
import psycopg2
import ast
from psycopg2.extensions import register_adapter, AsIs
import numpy as np
import base64
import os


def addapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)


def addapt_numpy_float64(numpy_float64):
   return AsIs(numpy_float64)


register_adapter(np.float64, addapt_numpy_float64)   # numpy.float64 to python float
register_adapter(np.int64, addapt_numpy_int64)       # numpy.int64 to python int

df = pd.read_excel(r'C:\Users\RodrigoNogueira\Desktop\SGD-PROJECT\sgd_2021_data_v1.xlsx')
df = df.where(pd.notnull(df), None)                  # nan to None


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

people = []
stores = []
cashier2 = []
customers = []
employees = []
promo_id = 1
ids = []
promotions = []
purchase_promotions = []
purchase_promotions2 = []
pur_promotions = []
pur_promotions2 = []
promos = {}
product_promos = {}
purchases = []
stores2 = {}
store_id = 0
products = []
products2 = []
purchase_purchase_promotion = []
product_promotion2 = []
products_purchase = []
product_promotion_purchase = []
stock = []
customer_purchase = []
price_history = []
prod_promos = []

people_c = df['customer nif'].unique()
cashiers = df['cashier nif'].unique()
store = df['store address'].unique()

for address in store:
    df1 = df[df['store address'] == address].iloc[0]
    df2 = df[df['store address'] == address].iloc[-1]
    store_id += 1
    stores2[df1['store address']] = store_id
    stores.append((store_id, df1['store address'], df1['store phone']))
    stock_store = ast.literal_eval(df2['store stock'])
    for product in stock_store.keys():
        stock.append((store_id, product, stock_store[product]))

for line in df.iterrows():
    line = line[1]
    purchases.append((line['record'], line['purchase value'], line['purchase date'], line['cashier nif'], stores2[line['store address']]))
    prod = ast.literal_eval(line['products'])
    products += prod
    for produto in prod:
        if len(produto.keys()) > 6:
            if produto['promotion_name'] not in product_promos.keys():
                product_promos[produto['promotion_name']] = promo_id
                promotions.append((promo_id, produto['promotion_date_start'], produto['promotion_date_end'], produto['promotion_discount'], produto['promotion_name'], stores2[line['store address']]))
                product_promotion2.append((promo_id,))
                promo_id += 1
            products_purchase.append((line['record'], produto['id'], produto['quantity'], produto['value'], produto['promotion_discount_value']))
        else:
            products_purchase.append((line['record'], produto['id'], produto['quantity'], produto['value'], 0))
    if line[14]:
        promo = ast.literal_eval(line[14])
        pur_promotions.append(promo['name'])
        purchase_promotions.append(line['record'])
        if promo['name'] not in promos.keys():
            promos[promo['name']] = promo_id
            promo_id += 1
            ids.append(line['record'])
    if not math.isnan(line['customer nif']):
        customer_purchase.append((line['record'], line['customer nif']))

pur_promotions = set(pur_promotions)
pur_promotions = list(pur_promotions)

for promotion in pur_promotions:
    pur_promotions2.append((promos[promotion],))


products = pd.DataFrame(products)
products = products.where(pd.notnull(products), None)
products_unique = products['id'].unique()

for record in ids:
    df1 = df[df['record'] == record].iloc[0]
    promotion = ast.literal_eval(df1['purchase promotion'])
    promotion_id = promos[promotion['name']]
    promotions.append((promotion_id, promotion['date_start'], promotion['date_end'], promotion['discount'], promotion['name'], stores2[df1['store address']]))

for record in purchase_promotions:
    df1 = df[df['record'] == record].iloc[0]
    promotion = ast.literal_eval(df1['purchase promotion'])
    promoid = promos[promotion['name']]
    purchase_purchase_promotion.append((promoid, record))
    purchase_promotions2.append((promoid, record, promotion['discount_value']))

for line in df.iterrows():
    line = line[1]
    prod = ast.literal_eval(line['products'])
    for prodt in prod:
        if len(prodt) > 6:
            promoid = product_promos[prodt['promotion_name']]
            if promoid == 75:
                print(line['record'], prodt, prod)
            product_promotion_purchase.append((line['record'], prodt['id'], promoid))

for cashier in cashiers:
    cashier2.append((cashier,))

for customer in people_c:
    if not math.isnan(customer):
        customers.append((customer,))

for nif in people_c:
    if not math.isnan(nif):
        df1 = df[df['customer nif'] == int(nif)].iloc[0]
        people.append((df1['customer nif'], df1['customer name'], df1['customer phone'], df1['customer address']))

for nif in cashiers:
    df1 = df[df['cashier nif'] == int(nif)].iloc[0]
    people.append((df1['cashier nif'], df1['cashier name'], df1['cashier phone'], df1['cashier address']))
    employees.append((df1['cashier nif'], stores2[df1['store address']]))

for product in products_unique:
    df1 = products[products['id'] == product].iloc[0]
    description = f'{df1["name"]} description'
    products2.append((product, df1['type'], df1['name'], description, df1['price']))
    price_history.append((product, df1['price'], "8/1/2021  12:00:00 AM"))

c.executemany("""INSERT INTO store (id, address, phone) 
                VALUES (%s, %s, %s)""", stores)

c.executemany("""INSERT INTO person (nif, name, phone, address) 
                VALUES (%s,%s,%s,%s)""", people)

c.executemany("""INSERT INTO employee (person_nif, store_id) 
                VALUES (%s, %s)""", employees)

c.executemany("""INSERT INTO cashier (employee_person_nif) 
                VALUES (%s)""", cashier2)

c.executemany("""INSERT INTO customer (person_nif) 
                VALUES (%s)""", customers)

c.executemany("""INSERT INTO purchase (id, valor, data, cashier_employee_person_nif, store_id) 
                VALUES (%s, %s, %s, %s, %s)""", purchases)

c.executemany("""INSERT INTO promotion (id, start_date, end_date, discount, name, store_id) 
                VALUES (%s, %s, %s, %s, %s, %s)""", promotions)

c.executemany("""INSERT INTO purchase_promotion (promotion_id)
                VALUES (%s)""", pur_promotions2)

c.executemany("""INSERT INTO purchase_promotion_purchase (purchase_promotion_promotion_id, purchase_id)
                VALUES (%s, %s)""", purchase_purchase_promotion)

c.executemany("""INSERT INTO promotion_discount (purchase_promotion_promotion_id, purchase_id, valor)
                VALUES (%s, %s, %s)""", purchase_promotions2)

c.executemany("""INSERT INTO product (id, type, name, description, price) 
                VALUES (%s, %s, %s, %s, %s)""", products2)

c.executemany("""INSERT INTO product_promotion (promotion_id) 
                VALUES (%s)""", product_promotion2)

c.executemany("""INSERT INTO product_purchase (purchase_id, product_id, quantidade, price, discount_value) 
                VALUES (%s, %s, %s, %s, %s)""", products_purchase)

c.executemany("""INSERT INTO product_promotion_product_purchase (product_purchase_purchase_id, product_purchase_product_id, product_promotion_promotion_id)
                VALUES (%s, %s, %s)""", product_promotion_purchase)

c.executemany("""INSERT INTO stock (store_id, product_id, stock)
                VALUES (%s, %s, %s)""", stock)

c.executemany("""INSERT INTO customer_purchase (purchase_id, customer_person_nif)
                VALUES (%s, %s)""", customer_purchase)

c.executemany("""INSERT INTO price_history (product_id, price, start_date)
                VALUES (%s, %s, %s)""", price_history)

conn.commit()
conn.close()
