import time
from urllib.request import urlopen
import re
import mysql.connector
import os
import datetime
from mysql.connector import Error
#Подключение к SQL серверу
def create_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password
        )
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection
#Подключение к SQL непосредственно к БД
def try_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection
#Создание БД
def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
    except Error as e:
        print(f"Ошибка подключения:'{e}'")
#Используется для многих вещей
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
    except Error as e:
        print(f"Ошибка подключения:'{e}'")
#Ссылка на страничку с ноутбуками
url1 = 'https://www.xcom-shop.ru/catalog/kompyutery_i_noytbyki/noytbyki/?utm_source=admitad&utm_medium=cpa&utm_campaign=1560786&utm_content=9238df3cb632c8b66e925de7050bd071&tagtag_uid=9238df3cb632c8b66e925de7050bd071'
page = urlopen(url1)
#Тут HTML код переводиться в текст и уже в тексте находятся нужные значения.
html_code = page.read().decode('utf-8')
#Список названий ноутбука
noutname = re.findall(r'" alt="(.*?)" title="', html_code, re.I)
#Список цен на ноутбуки
noutprice = re.findall(r'price="(.*?)"', html_code, re.I)
#Список ссылок на странички ноутбуков на сайте
nouturl = re.findall(r'<a class="catalog_item__image catalog_item__image--tiles" href="(.*?)"', html_code, re.I)
a = 0
for i in nouturl:
    nouturl[a] = 'https://www.xcom-shop.ru' + i
    a = a + 1
#Тут объясню: выше три списка. В них одинаковое количество эллементов и при появлении новых компьютеров он будет их добавлять.
#Первый эллемент первого списка соответствует первому эллементу второго и третьего списка.
#Ниже часть которая пытается подключиться к серверу, поиск и создания таблицы. Занесение Эллементов в таблицу
dir_path = os.getcwd()
#Выше путь к исполняемой директории
#                                              !!!ВАЖНО!!!
#Вам нужно положить файл кодировки UTF-8 в исполняемую директорию с названием: "123" (можете изменить в коде, это не сложно)
#В файле первая строка: название хоста, вторая строка: имя SQL пользователя, третья строка: пароль для подключения.
x = open('test.txt','r')
hostname = x.readline(1)
sqluser = x.readline(2)
sqlpassword = x.readline(3)
connection = try_connection(hostname, sqluser, sqlpassword, 'xcomeshop')
#Выше попытка подключения к серверу, если она будет неудачна - значение будет None.
if connection == None:
    connection = create_connection(hostname, sqluser, sqlpassword)
    #Если даже после этого подключиться не получиться то оно само собой завершиться
    if connection == None:
        exit()
    else:
        #ниже создание БД и цикл её заполнения
        create_database_query = "CREATE DATABASE xcomeshop"
        create_database(connection, create_database_query)
        connection = try_connection(hostname, sqluser, sqlpassword, 'xcomeshop')
        create_users_table = """
        CREATE TABLE IF NOT EXISTS noutbuki (
          id INT AUTO_INCREMENT, 
          name TEXT NOT NULL, 
          cost INT, 
          url TEXT NOT NULL, 
          tooday TEXT NOT NULL,
          PRIMARY KEY (id)
        ) ENGINE = InnoDB
        """
        execute_query(connection, create_users_table)
        a = 0
        while a != noutname.count():
            create_users = """
                    INSERT INTO
                      `noutbuki` (`name`, `cost`, `url`, `tooday`)
                    VALUES
                      ('""" + noutname[a] + """', """ + noutprice[a] + """, '""" + nouturl[a] + """"', '""" + str(datetime.datetime.now()) + """');
                    """
            execute_query(connection, create_users)
        time.sleep(3600)
#Если БД существует, то её данные обновляются
else:
        try:
            a = 0
            while a != noutname.count():
                update_nout_name = """
                            UPDATE
                                noutbuki
                            SET
                                name = " """ + noutname[a] + """ "
                            Where
                                id = """ + str(a) + """ 
                            """
                execute_query(connection, update_nout_name)
                update_nout_cost = """
                            UPDATE
                                noutbuki
                            SET
                                cost = """ + noutprice[a] + """ 
                            Where
                                id = """ + str(a) + """ 
                            """
                execute_query(connection, update_nout_cost)
                update_nout_url = """
                            UPDATE
                                noutbuki
                            SET
                                url = " """ + nouturl[a] + """ "
                            Where
                                id = """ + str(a) + """ 
                            """
                execute_query(connection, update_nout_url)
                update_nout_data = """
                            UPDATE
                                noutbuki
                            SET
                                tooday = " """ + str(datetime.datetime.now()) + """ "
                            Where
                                id = """ + str(a) + """ 
                            """
                execute_query(connection, update_nout_data)
            time.sleep(3600)
        except:
            create_users_table = """
                CREATE TABLE IF NOT EXISTS noutbuki (
                    id INT AUTO_INCREMENT, 
                    name TEXT NOT NULL, 
                    cost INT, 
                    url TEXT NOT NULL, 
                    PRIMARY KEY (id)
                ) ENGINE = InnoDB
                """
            execute_query(connection, create_users_table)
            time.sleep(3600)
#Ниже вечный цикл обновления всего раз в час
z = 0
while z == 0:
    try:
        a = 0
        while a != noutname.count():
            update_nout_name = """
                        UPDATE
                            noutbuki
                        SET
                            name = " """ + noutname[a] + """ "
                        Where
                            id = """ + str(a) + """ 
                        """
            execute_query(connection, update_nout_name)
            update_nout_cost = """
                        UPDATE
                            noutbuki
                        SET
                            cost = """ + noutprice[a] + """ 
                        Where
                            id = """ + str(a) + """ 
                        """
            execute_query(connection, update_nout_cost)
            update_nout_url = """
                        UPDATE
                            noutbuki
                        SET
                            url = " """ + nouturl[a] + """ "
                        Where
                            id = """ + str(a) + """ 
                        """
            execute_query(connection, update_nout_url)
            update_nout_data = """
                        UPDATE
                            noutbuki
                        SET
                            tooday = " """ + str(datetime.datetime.now()) + """ "
                        Where
                            id = """ + str(a) + """ 
                        """
            execute_query(connection, update_nout_data)
            time.sleep(3600)
    except:
        create_users_table = """
            CREATE TABLE IF NOT EXISTS noutbuki (
                id INT AUTO_INCREMENT, 
                name TEXT NOT NULL, 
                cost INT, 
                url TEXT NOT NULL, 
                PRIMARY KEY (id)
            ) ENGINE = InnoDB
            """
        execute_query(connection, create_users_table)
        time.sleep(3600)