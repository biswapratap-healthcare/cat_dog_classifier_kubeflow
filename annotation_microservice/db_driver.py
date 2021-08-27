import base64
import psycopg2
from datetime import datetime, timezone


# handle = "localhost"
handle = "34.87.16.166"
# database = "hops"
database = "training_data"


def drop_table(table_name):
    ret = 0
    status = "Success"
    conn = None
    sql = "DROP TABLE " + table_name + ";"
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
        status = str(error)
        ret = -1
    finally:
        if conn is not None:
            conn.close()
        return ret, status


def truncate_table(table_name):
    ret = 0
    status = "Success"
    conn = None
    sql = "TRUNCATE " + table_name + ";"
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
        status = str(error)
        ret = -1
    finally:
        if conn is not None:
            conn.close()
        return ret, status


def if_table_exists(table_name='train_data'):
    ret = False
    conn = None
    sql = "SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = '" + table_name + "');"""
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


def create_table(table_name='train_data'):
    ret = 0
    status = "Success"
    conn = None
    sql = "CREATE TABLE " + table_name + " (ID text PRIMARY KEY, Label text, Date date, Name text, Image bytea);"
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
        status = str(error)
        ret = -1
    finally:
        if conn is not None:
            conn.close()
        return ret, status


def get_study_from_to(from_date, to_date, table_name='train_data'):
    ret_dict = dict()
    ret_str = "Success"
    conn = None
    sql = "SELECT * FROM " + table_name + " WHERE Date BETWEEN '" + from_date + "' and '" + to_date + "'"
    try:
        conn = psycopg2.connect(host=handle,
                                database=database,
                                user="postgres",
                                password="admin")
        cur = conn.cursor()
        cur.execute(sql)
        records = cur.fetchall()
        idx = 0
        for record in records:
            one_rec = dict()
            one_rec['ID'] = str(record[0])
            one_rec['Label'] = str(record[1])
            one_rec['Date'] = str(record[2])
            one_rec['Name'] = str(record[3])
            # fp = open(one_rec['Name'], "wb")
            # fp.write(bytes(record[4]))
            # fp.close()
            data = base64.b64encode(bytes(record[4]))
            one_rec['Image'] = str(data)[1:]
            ret_dict[str(idx)] = one_rec
            idx += 1
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("DB Error: " + str(error))
        ret_str = str(error)
        ret_dict = dict()
    finally:
        if conn is not None:
            conn.close()
        return ret_dict, ret_str


def get_all_data(table_name='train_data'):
    ret_dict = dict()
    ret_str = "Success"
    conn = None
    sql = "SELECT * FROM " + table_name + ";"
    try:
        conn = psycopg2.connect(host=handle,
                                database=database,
                                user="postgres",
                                password="admin")
        cur = conn.cursor()
        cur.execute(sql)
        records = cur.fetchall()
        idx = 0
        for record in records:
            one_rec = dict()
            one_rec['ID'] = str(record[0])
            one_rec['Label'] = str(record[1])
            one_rec['Date'] = str(record[2])
            one_rec['Name'] = str(record[3])
            data = base64.b64encode(bytes(record[4]))
            one_rec['Image'] = str(data)[1:]
            ret_dict[str(idx)] = one_rec
            idx += 1
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print("DB Error: " + str(error))
        ret_str = str(error)
        ret_dict = dict()
    finally:
        if conn is not None:
            conn.close()
        return ret_dict, ret_str


def insert_data(_id, label, name, image):
    ret = 0
    status = "Success"
    conn = None
    try:
        created_date = datetime.now(timezone.utc)
        data_bytes = b''
        with open(image, "rb") as f:
            byte = f.read(1)
            while byte:
                data_bytes += byte
                byte = f.read(1)
        sql = """INSERT INTO train_data VALUES (%s,%s,%s,%s,%s) RETURNING ID;"""
        conn = psycopg2.connect(host=handle,
                                database=database,
                                user="postgres",
                                password="admin")
        cur = conn.cursor()
        cur.execute(sql, (_id,
                          label,
                          created_date,
                          name,
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
