import sys
import sqlite3


def drop_tables_if_exist(conn):
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS tbl_conn;")
    cursor.execute("DROP TABLE IF EXISTS tbl_reqrep;")
    cursor.close()
    conn.commit()


def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute("\n"
                   "CREATE TABLE tbl_conn\n"
                   "(\n"
                   "    label TEXT PRIMARY KEY,\n"
                   "    client_addr TEXT,\n"
                   "    client_port INTEGER,\n"
                   "    server_addr TEXT,\n"
                   "    server_port INTEGER,\n"
                   "    request_count INTEGER,\n"
                   "    request_bytes INTEGER,\n"
                   "    response_count INTEGER,\n"
                   "    response_bytes INTEGER\n"
                   ");\n")
    cursor.execute("\n"
                   "CREATE TABLE tbl_reqrep\n"
                   "(\n"
                   "    reqrep_id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
                   "    label TEXT,\n"
                   "    ts1 INTEGER,\n"
                   "    ts2 INTEGER,\n"
                   "    ts3 INTEGER,\n"
                   "    request_idx INTEGER,\n"
                   "    request_len INTEGER,\n"
                   "    response_idx INTEGER,\n"
                   "    response_len INTEGER\n"
                   ");\n")
    cursor.close()
    conn.commit()


if __name__ == '__main__':
    db_name = sys.argv[1]

    conn = sqlite3.connect(db_name)

    drop_tables_if_exist(conn)
    create_tables(conn)
