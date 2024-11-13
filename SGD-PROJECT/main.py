import flask
from flask.wrappers import Request
import psycopg2
import logging
from flask import request, jsonify
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


app = flask.Flask(__name__)

StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
}

@app.route('/')
def landing_page():
    return """
        Projeto SGD
        \n
        Trabalho realizado por:
            André Cunha
            Francisco Gaspar
            Rodrigo Nogueira
        """ 

@app.route('/proj/product/<id>', methods=['PUT'])
def update_products(id):
    logger.info('PUT /proj/product/<id>')
    payload = flask.request.get_json()

    conn = db_connection()
    c = conn.cursor()

    logger.debug(f'PUT /proj/product/<id> - payload: {payload}')

    if 'price' not in payload or 'type' not in payload or 'name' not in payload or 'description' not in payload:
            response = {'status': StatusCodes['api_error'], 'results': 'missing data required for update'}
            return flask.jsonify(response)    
            
    statement = '''UPDATE product 
                SET price = %s, name = %s, description = %s, type = %s 
                WHERE id = %s;

                UPDATE price_history
                set end_date = current_date
                WHERE end_date is null AND product_id = %s;

                INSERT INTO price_history 
                (product_id, price, start_date)
                VALUES (%s, %s, current_date)'''

    values = (payload['price'], payload['name'], payload['description'], payload['type'],  id, id, id, payload['price'])

    try:
        res = c.execute(statement, values)
        response = {'status': StatusCodes['success'], 'results': f'Updated: {c.rowcount}'}

        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        response = {'status': StatusCodes['internal_error'], 'results': str(error)}

        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)



@app.route('/proj/report/promotions/', methods = ['GET'])
def promotions():
    logger.info('GET /proj/report/promotions/')

    conn = db_connection()
    c = conn.cursor()

    try:
        c.execute('''SELECT count(purchase_id), purchase_promotion_promotion_id, sum(valor) 
                    from promotion_discount
                    GROUP BY purchase_promotion_promotion_id''')

        rows = c.fetchall()

        logger.debug('GET /proj/report/promotions - parse')

        Results = []

        for row in rows:
            logger.debug(row)
            content = {'promotion_id': int(row[1]), 'promotion_purchases_count': row[0], 'total_discount_value': row[2]}
            Results.append(content)

        response = {'status': StatusCodes['success'], 'results': Results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /proj/report/promotions - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'results': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


@app.route('/proj/report/cashiers/', methods = ['GET'])
def cashier_sales():
    logger.info('GET /proj/report/cashiers/')

    conn = db_connection()
    c = conn.cursor()

    try:
        c.execute('''                 
                        SELECT
                            main.month,
                            sub.employee_person_nif as "cashier_nif",
                            main.maximo as "total vendas"
                        FROM
                        (SELECT 
                            month,
                            max(soma) as maximo
                        FROM
                            (SELECT 
                            date_part('month', purchase.data) as "month",
                            employee_person_nif,
                            sum(valor) as soma
                            FROM
                                cashier, purchase
                                WHERE cashier.employee_person_nif = purchase.cashier_employee_person_nif
                                AND purchase.data between current_date - interval '1 year' and current_date - 1
                                group by date_part('month', purchase.data), employee_person_nif
                                ORDER BY MONTH) x
                        GROUP BY MONTH) main,
                            (SELECT 
                            date_part('month', purchase.data) as "month",
                            employee_person_nif,
                            sum(valor) as soma
                            FROM
                                cashier, purchase
                                WHERE cashier.employee_person_nif = purchase.cashier_employee_person_nif
                                AND purchase.data between current_date - interval '1 year' and current_date - 1
                                group by date_part('month', purchase.data), employee_person_nif
                                ORDER BY MONTH) sub
                        WHERE main.maximo = sub.soma''')

        rows = c.fetchall()

        logger.debug('GET /proj/report/cashiers - parse')

        Results = []

        for row in rows:
            logger.debug(row)
            content = {'month': int(row[0]), 'cashier_id': row[1], 'total_value_purchases': row[2]}
            Results.append(content)

        response = {'status': StatusCodes['success'], 'results': Results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /proj/report/cashiers - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'results': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


@app.route('/proj/report/stores/', methods = ['GET'])
def store_sales():
    logger.info('GET /proj/report/stores/')

    conn = db_connection()
    c = conn.cursor()

    try:
        c.execute('''
                SELECT 
                    date_part('month', purchase.data) as "month",
                    store.id, 
                    sum(valor), 
                    count(purchase.id)

                FROM 
                    purchase, 
                    store
                WHERE 
                    purchase.store_id = store.id
                GROUP BY 
                    date_part('month', purchase.data), store.id
                ORDER BY 
                    date_part('month', purchase.data)
                    ''')

        rows = c.fetchall()

        logger.debug('GET /proj/report/stores - parse')

        Results = []

        for row in rows:
            logger.debug(row)
            content = {'month': int(row[0]), 'store_id': row[1], 'total_value_purchases': row[2], 'purchases_count': row[3]}
            Results.append(content)

        response = {'status': StatusCodes['success'], 'results': Results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /proj/report/stores - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'results': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


@app.route('/proj/report/store_last_month/<int:id>', methods = ['GET'])
def product_search(id: int):

    logger.info(f'GET /proj/report/store_last_month/{id}')
    logger.debug(f'store_id: {id}')

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""select date_part('day', data) as data, sum(valor), count(id) 
                    from purchase 
                    WHERE data >= date_trunc('month', current_date - interval '1' month) 
                    and data < date_trunc('month', current_date) 
                    and store_id = %s group by data
                    order by date_part('day', data)""", (id,))

        rows = cur.fetchall()

        logger.debug(f'GET /proj/report/store_last_month/{id} - parse')

        Results = []

        for row in rows:
            logger.debug(row)
            content = {'Date': int(row[0]), 'Total Value': row[1], 'Purchases Count': row[2]}
            Results.append(content)

        response = {'status': StatusCodes['success'], 'results': Results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /proj/report/store_last_month/{id} - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'results': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

@app.route('/proj/clients/', methods=['POST'])
def add_clients():
    logger.info('POST /proj/clients')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'POST /proj/clients - payload: {payload}')
    
    if 'id' not in payload or 'phone' not in payload or 'address' not in payload or 'name' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'missing critical data'}
        return flask.jsonify(response)

    
    statement1 = '''
                INSERT INTO person (nif, address, name, phone) VALUES (%s, %s, %s, %s);
                INSERT INTO customer(person_nif) VALUES(%s);
                '''
    
    values = (payload['id'], payload['address'], payload['name'], payload['phone'], payload['id'])
    
    try:
        cur.execute(statement1, values)
        

        conn.commit()
        response = {'status': StatusCodes['success'], 'results': f'{payload["id"]}'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /proj/clients - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'results': str(error)}

        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

@app.route('/proj/product/<int:id>', methods=['GET'])
def product_details(id):
    logger.info('GET /proj/product/<id>')

    logger.debug(f'id: {id}')

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""select description, purchase_id, price_history.price 
                    from product, product_purchase, price_history 
                    where product.id = price_history.product_id 
                    and product.id = product_purchase.product_id 
                    and product.id = %s""", (id,))

        rows = cur.fetchall()

        logger.debug('GET /proj/product/<id> - parse')

        purchase_ids = []
        prices = []

        for row in rows:
            logger.debug(row)
            if row[2] not in prices:
                prices.append(int(row[2]))
            if row[1] not in purchase_ids:
                purchase_ids.append(row[1])
        
        content = {"description": rows[0][0], "prices": prices, "purchases": purchase_ids}

        response = {'status': StatusCodes['success'], 'results': content}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /proj/product/<id> - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'results': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


@app.route('/proj/report/month_product/<data>', methods = ['GET'])
def product_results(data):
    date = data.split()
    year = data[0:4]
    month = data[-2:]

    logger.info('GET /report/month_product/<date>')

    conn = db_connection()
    c = conn.cursor()

    try:
        c.execute('''
                    SELECT product_id, count(product_id), SUM(product_purchase.price) as "valor total"
                        FROM product_purchase, purchase
                        WHERE product_purchase.purchase_id = purchase.id 
                        AND date_part('month', purchase.data) = %s
                        AND date_part('year', purchase.data) = %s
                        GROUP by product_id
                        ORDER BY COUNT(PRODUCT_ID) DESC
                        LIMIT 10;
                        ''', (month, year))

        rows = c.fetchall()

        logger.debug('GET /report/month_product/<date> - parse')

        Results = []

        for row in rows:
            logger.debug(row)
            content = {'product_id': row[0], 'total_value': row[2], 'purchases_count': row[1]}
            Results.append(content)

        response = {'status': StatusCodes['success'], 'results': Results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /report/month_product/<date> - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'results': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


@app.route('/proj/purchases/<data>', methods=['GET'])
def get_purchases(data):
    logger.info('GET /proj/purchases/<data>')

    logger.debug(f'data: {data}')

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""Select purchase.id, valor, data, product_purchase.product_id, product.name, product_purchase.quantidade,product.price, person.name, person.nif
                    FROM purchase, product_purchase, product,person, customer_purchase
                    WHERE purchase.id = product_purchase.purchase_id
                    AND product.id = product_purchase.product_id 
					AND customer_purchase.customer_person_nif = person.nif
					AND customer_purchase.purchase_id = purchase.id
                    AND data = %s""", (data,))

        rows = cur.fetchall()

        logger.debug('GET /proj/purchases/<data> - parse')   

        Results = []

        content = {"purchase_id": rows[0][0], "date_time": 0, "total": 0, "client_id": 0, "client_name": 0}
        
        for i in range(len(rows)):
            items = []
            for row in rows:
                if int(row[0]) == int(content["purchase_id"]):                   
                    logger.debug(row)          
                    if row[4] not in items:
                        items.append(row[4])
                        items.append(row[5])
                        items.append(row[6])
                
            content = {"purchase_id": rows[i][0], "date_time": rows[i][2], "total": rows[i][1], "client_id": rows[i][8], "client_name": rows[i][7],"items":items} 
                
            Results.append(content)
            
        response = {'status': StatusCodes['success'], 'results': Results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /proj/purchases/<data> - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'results': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

@app.route('/proj/product/<string:keyword>', methods=['GET'])
def product_search_keyword(keyword):
    logger.info('GET /proj/product/<keyword>')

    logger.debug(f'keyword: {keyword}')

    conn = db_connection()
    cur = conn.cursor()

    try:
        values = {'kw': keyword + '%', 'kw2': '%' + keyword + '%'}

        cur.execute(
            """SELECT id, type, name, price, description 
            from product 
            where name like %(kw)s 
            or type like %(kw)s 
            or description like %(kw2)s""", values)

        rows = cur.fetchall()

        logger.debug('GET /proj/product/{keyword} - parse')

        Results = []

        for row in rows:
            logger.debug(row)
            content = {'product_id': int(row[0]), 'type': row[1], 'name': row[2], 'price': row[3], 'description':row[4]}
            Results.append(content)
        response = {'status': StatusCodes['success'], 'results': Results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /proj/product/{keyword} - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'results': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

@app.route('/proj/purchase/', methods = ['POST'])
def add_purchase():
    logger.info('POST proj/purchase')
    payload = flask.request.get_json()

    conn = db_connection()
    c = conn.cursor()

    logger.debug(f'POST proj/purchase  - payload: {payload}')

    if 'cashier_id' not in payload or 'products' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'missing critical data for insertion'}
        return flask.jsonify(response)

    c.execute("SELECT max(id) FROM PURCHASE")
    purchase_id = c.fetchall()
    purchase_id = purchase_id[0][0]
    purchase_id += 1
    
    products = payload['products']
    products_insert = []
    purchase = (purchase_id, payload['cashier_id'])

    for product in products:
        products_insert.append((purchase_id, product))


    statement1 = '''
                    INSERT INTO purchase (id, cashier_employee_person_nif)
                    VALUES(%s, %s);
                '''

    statement2 = '''               
                    INSERT INTO product_purchase (purchase_id, product_id)
                    VALUES(%s, %s);
                '''
    
    statement3 = '''            
                    INSERT INTO customer_purchase (purchase_id, customer_person_nif)
                    VALUES (%s, %s)
                '''


    statement4 = '''
                    INSERT INTO promotion_discount (valor, purchase_promotion_promotion_id, purchase_id)
                    VALUES (%s, %s, %s);
                    INSERT INTO purchase_promotion_purchase (purchase_promotion_promotion_id, purchase_id)
                    VALUES (%s, %s);
                '''

    try:
        c.execute(statement1, purchase)
        c.executemany(statement2, products_insert)

        if 'client_id' in payload:
           c.execute(statement3, (purchase_id, payload['client_id']))

        if 'discount_value' in payload.keys():
            c.execute(statement4, (payload['discount_value'], payload['promotion_id'], purchase_id, payload['promotion_id'], purchase_id))

        conn.commit()

        response = {'status': StatusCodes['success'], 'results': f'{purchase_id}'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /proj/purchase  - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'results': str(error)}
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

if __name__ == '__main__':
    logging.basicConfig(filename='log_file.log')
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    host = '127.0.0.1'
    port = 8080
    app.run(host=host, debug=True, threaded=True, port=port)
    logger.info(f'API v1.0 online: http://{host}:{port}')
