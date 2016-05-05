#!/usr/bin/env python
# coding=utf-8


#################################################
# 把http.times文件导入到数据库                     #
#################################################

import sys
import os
import re
import sqlite3

PATTERN_CONN = re.compile("^conn (\d+\.\d+\.\d+\.\d+):(\d+) (\d+\.\d+\.\d+\.\d+):(\d+) (.+) (\d+) (\d+) (\d+) (\d+)$")
PATTERN_REQREP = re.compile(
    "^reqrep (\d+\.\d+\.\d+\.\d+):(\d+) (\d+\.\d+\.\d+\.\d+):(\d+) (.+) (\d+\.\d+) (\d+\.\d+) (\d+\.\d+) (\d+) (\d+) (\d+) (.+) (.+) (.+) (.*)$")


def clear_old_data_of_this_pcap_id(pcap_id, conn):
    """
    清除掉老数据
    :param pcap_id:
    :param conn:
    :return:
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tbl_reqrep WHERE pcap_id = ?", (pcap_id,))
    cursor.execute("DELETE FROM tbl_conn WHERE pcap_id = ?", (pcap_id,))
    cursor.close()
    conn.commit()


def insert_valid_conn(pcap_id, line, conn):
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
        '        response_count, response_bytes, '
        '        pcap_id'
        '    )'
        'VALUES (?,?,?,?,?,?,?,?,?,?)',
        (
            label,
            client_addr, client_port,
            server_addr, server_port,
            request_count, request_bytes,
            response_count, response_bytes,
            pcap_id
        )
    )
    cursor.close()
    conn.commit()


def insert_valid_reqrep(pcap_id, line, conn):
    """
    如果line是一个reqrep数据,就把它加到数据库里面
    :param line:
    :param conn:
    :return:
    """
    m = PATTERN_REQREP.match(line)
    if not m:
        return

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
        '        pcap_id'
        '    ) '
        'VALUES (?,?,?,?,?,?,?)',
        (
            label,
            ts1, ts2, ts3,
            request_len, response_len,
            pcap_id
        )
    )
    cursor.close()
    conn.commit()


def httptimes2db(pcap_id, file, conn):
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

        insert_valid_conn(pcap_id, line, conn)
        insert_valid_reqrep(pcap_id, line, conn)

    pass


if __name__ == '__main__':
    db_name = sys.argv[1]
    pcap_id = int(sys.argv[2])
    tcptrace_result_dir = sys.argv[3]

    http_times_file = os.path.join(tcptrace_result_dir, '%s_http.times' % pcap_id)

    file = open(http_times_file)

    conn = sqlite3.connect(db_name)
    clear_old_data_of_this_pcap_id(pcap_id, conn)
    httptimes2db(pcap_id, file, conn)
    conn.close()
