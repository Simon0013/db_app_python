from psycopg2 import *
from redis import *
import json
import random
import flask

str_redis = StrictRedis(host="127.0.0.1", port=6379, decode_responses=True)

userId = input("Укажите имя пользователя PostgreSQL: ")
passId = input("Укажите пароль для пользователя " + userId + ": ")
dbName = input("Укажите имя базы данных PostgreSQL: ")

try:
    connection = connect(user=userId, password=passId, host="127.0.0.1", port="5432", database=dbName)
    cursor = connection.cursor()
    stroke1 = input("Укажите первую строку: ")
    stroke2 = input("Укажите вторую строку: ")
    letters1 = set()
    letters2 = set()
    for i in stroke1:
        letters1.add(i)
    for i in stroke2:
        letters2.add(i)
    ans = dict()
    if (len(stroke1) == len(stroke2)) and (letters1 == letters2):
        ans = {"anagramms": True}
        str_redis.incr('count')
    else:
        ans = {"anagramms": False}
    print(json.dumps(ans))
    print(json.dumps({"count": str_redis.get('count')}))

    if connection:
        arr = ["emeter", "zigbee", "lora", "gsm"]
        insert_query = "INSERT INTO devices (dev_id, dev_type) VALUES "
        for i in range(1, 11):
            insert_query += "('"
            mac_address = str()
            for j in range(6):
                mac_address += hex(random.randint(0, 255))[2:]
                if j != 5:
                    mac_address += "."
            insert_query += mac_address + "'"
            device = arr[random.randint(0, 3)]
            insert_query += ", '" + device + "'), "
        insert_query = insert_query[0:len(insert_query) - 2]
        cursor.execute(insert_query)
        connection.commit()
        app = flask.Flask(__name__)
        with app.app_context():
            res_obj = flask.make_response("201 HTTP status", 201)
            print("Insert: ", res_obj)

        insert_query = "INSERT INTO endpoints (device_id, comment) VALUES "
        arr = list(range(1, 11))
        for i in range(1, 6):
            n = random.randint(0, len(arr) - 1)
            insert_query += "(" + str(arr[n]) + ", 'no comment'), "
            arr.pop(n)
        insert_query = insert_query[0:len(insert_query) - 2]
        cursor.execute(insert_query)
        connection.commit()
        with app.app_context():
            res_obj = flask.make_response("201 HTTP status", 201)
            print("Insert: ", res_obj)

        create_query = "CREATE OR REPLACE VIEW devs AS SELECT devices.id, dev_id, dev_type FROM devices EXCEPT SELECT " +\
                       " devices.id, dev_id, dev_type FROM devices INNER JOIN endpoints ON devices.id = device_id"
        cursor.execute(create_query)
        connection.commit()
        select_query = "SELECT COUNT(id), dev_type FROM devs GROUP BY dev_type"
        cursor.execute(select_query)
        record = cursor.fetchall()
        print("Не привязанные к endpoints устройства (количество и тип устройства): \n", record)

        cursor.close()
        connection.close()
except (Exception, Error) as err:
    print("Ошибка: ", err)
