#!/usr/bin/env python
# coding=utf-8


#################################################
# 把http.times文件导入到数据库                     #
#################################################


import re
import sqlite3

PATTERN_CONN = re.compile("^conn (\d+\.\d+\.\d+\.\d+):(\d+) (\d+\.\d+\.\d+\.\d+):(\d+) (.+) (\d+) (\d+) (\d+) (\d+)$")
PATTERN_REQREP = re.compile(
    "^reqrep (\d+\.\d+\.\d+\.\d+):(\d+) (\d+\.\d+\.\d+\.\d+):(\d+) (.+) (\d+\.\d+) (\d+\.\d+) (\d+\.\d+) (\d+) (\d+) (\d+) (.+) (.+) (.+) (.*)$")


def init_tables(conn):
    """
    初始化数据表,如果数据存在,就会把他删掉,再重新初始化
    :param conn:
    :return:
    """
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS tbl_conn;")
    cursor.execute("DROP TABLE IF EXISTS tbl_reqrep;")
    cursor.close()
    conn.commit()
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
                   "    response_len INTEGER,\n"
                   "    host TEXT,\n"
                   "    url TEXT,\n"
                   "    method TEXT,\n"
                   "    content_type TEXT,\n"
                   "    response_code INTEGER,\n"
                   "    version TEXT\n"
                   ");\n")
    cursor.close()
    conn.commit()


def insert_valid_conn(line, conn):
    """
    如果line是一个conn数据,就把他加到数据库里面
    :param line:
    :param conn:
    :return:
    """
    m = PATTERN_CONN.match(line)
    if not m:
        return

    client_addr, client_port = m.group(1), m.group(2)
    server_addr, server_port = m.group(3), m.group(4)
    label = m.group(5)
    request_bytes, request_count = m.group(6), m.group(7)
    response_bytes, response_count = m.group(8), m.group(9)

    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO '
        '    tbl_conn'
        '    ('
        '        label, '
        '        client_addr, client_port, '
        '        server_addr, server_port, '
        '        request_count, request_bytes, '
        '        response_count, response_bytes'
        '    )'
        'VALUES (?,?,?,?,?,?,?,?,?)',
        (
            label,
            client_addr, client_port,
            server_addr, server_port,
            request_count, request_bytes,
            response_count, response_bytes
        )
    )
    cursor.close()
    conn.commit()


def insert_valid_reqrep(line, conn):
    """
    如果line是一个reqrep数据,就把它加到数据库里面
    :param line:
    :param conn:
    :return:
    """
    m = PATTERN_REQREP.match(line)
    if not m:
        return

    # client_addr, client_port = m.group(1), m.group(2)
    # server_addr, server_port = m.group(3), m.group(4)
    label = m.group(5)
    ts1, ts2, ts3 = m.group(6), m.group(7), m.group(8)
    request_len, response_len = m.group(9), m.group(10)
    response_code = m.group(11)
    method, url, version = m.group(12), m.group(13), m.group(14)
    content_type = m.group(15)

    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO '
        '    tbl_reqrep'
        '    ('
        '        label,'
        '        ts1,ts2,ts3,'
        '        request_len,response_len,'
        '        response_code,'
        '        method,url,version,'
        '        content_type'
        '    ) '
        'VALUES (?,?,?,?,?,?,?,?,?,?,?)',
        (
            label,
            ts1, ts2, ts3,
            request_len, response_len,
            response_code,
            method, url, version,
            content_type
        )
    )
    cursor.close()
    conn.commit()


def httptimes2db(file, conn):
    """
    读取http.times文件的内容,按照顺序把数据加入到数据库中去
    :param file:  http.times文件
    :param conn:  数据库
    :return:
    """
    while True:
        line = file.readline()
        if not line:
            break

        insert_valid_conn(line, conn)
        insert_valid_reqrep(line, conn)

    pass


if __name__ == '__main__':
    file = open('/Users/jinhaoxia/Desktop/httptest/http.times')  # sys.stdin
    # db = sys.argv[1]
    # httptimes2db(file, db)
    conn = sqlite3.connect('test.db')
    init_tables(conn)
    httptimes2db(file, conn)
    conn.close()
