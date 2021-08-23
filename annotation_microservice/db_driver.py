import psycopg2
from datetime import datetime, timezone


handle = "localhost"
# handle = "34.87.16.166"
database = "hops"
# database = "training_data"


def if_table_exists():
    ret = False
    conn = None
    sql = """SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'train_data');"""
    try:
        conn = psycopg2.connect(host=handle,
                                database=database,
                                user="postgres",
                                password="admin")
        cur = conn.cursor()
        cur.execute(sql)
        ret = cur.fetchone()[0]
    except (Exception, psycopg2.DatabaseError) as error:
        print("DB Error: " + str(error))
        ret = False
    finally:
        if conn is not None:
            conn.close()
        return ret


def create_table():
    ret = 0
    conn = None
    sql = """CREATE TABLE train_data (ID text PRIMARY KEY, Label text, Date date, Image bytea);"""
    try:
        conn = psycopg2.connect(host=handle,
                                database=database,
                                user="postgres",
                                password="admin")
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("DB Error: " + str(error))
        ret = -1
    finally:
        if conn is not None:
            conn.close()
        return ret


def insert_data(_id, label, image):
    ret = 0
    status = "Success"
    conn = None
    try:
        created_date = datetime.now(timezone.utc)
        data_bytes = b''
        with open(image, "rb") as f:
            while byte := f.read(1):
                data_bytes += byte
        sql = """INSERT INTO train_data VALUES (%s,%s,%s,%s) RETURNING ID;"""
        conn = psycopg2.connect(host=handle,
                                database=database,
                                user="postgres",
                                password="admin")
        cur = conn.cursor()
        cur.execute(sql, (_id,
                          label,
                          created_date,
                          data_bytes,))
        sid = cur.fetchone()[0]
        if sid:
            conn.commit()
            print("Committed --> " + str(sid))
        else:
            ret = -1
            status = "Failed to insert train data."
    except (Exception, psycopg2.DatabaseError) as error:
        print("DB Error: " + str(error))
        ret = -1
        status = str(error)
    finally:
        if conn is not None:
            conn.close()
        return ret, status
