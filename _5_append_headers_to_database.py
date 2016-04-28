#!/usr/bin/env python
# coding=utf-8
import sys
import os
import sqlite3
import pprint
from _4_extract_headers_from_http_times import get_request, get_response


#################################################
# 头部解析                                       #
#################################################


def feed_for_reqrep_of_all_conn(conn, pcap_id):
    """
    为所有reqrep记录填充文件位置(request_idx,response_idx)信息
    :param conn:
    :return:
    """
    cursor = conn.cursor()
    cursor.execute('SELECT label FROM tbl_conn WHERE pcap_id = ?', (pcap_id,))
    labels = cursor.fetchall()
    cursor.close()
    for label in labels:
        feed_for_reqrep_of_one_conn(conn, label[0], pcap_id)
    pass


def feed_for_reqrep_of_one_conn(conn, conn_label, pcap_id):
    """
    为特定conn的所有reqrep记录填充文件位置(request_idx,response_idx)信息
    :param conn:
    :param conn_label:
    :return:
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT ROWID, request_len, response_len FROM tbl_reqrep WHERE label = ? AND pcap_id = ? ORDER BY ts1 ASC",
        (conn_label, pcap_id))
    rlls = cursor.fetchall()
    cursor.close()

    request_idx = 0
    response_idx = 0

    cursor = conn.cursor()

    for rowid, request_len, response_len in rlls:
        cursor.execute(
            "UPDATE tbl_reqrep SET request_idx=?, response_idx=? WHERE ROWID = ?",
            (request_idx, response_idx, rowid)
        )
        request_idx += request_len
        response_idx += response_len

    cursor.close()
    conn.commit()


def show_headers_of_all_reqrep(conn, pcap_id, dir):
    """
    根据reqrep里面的request_idx,response_idx来读取请求和响应数据,并交给dpkt解析,打出头部
    :param conn:
    :param dir:
    :return:
    """
    cursor = conn.cursor()
    cursor.execute(
        'SELECT ROWID, label, request_idx, request_len, response_idx, response_len FROM tbl_reqrep WHERE pcap_id = ? ORDER BY ts1 ASC',
        (pcap_id,))
    rrs = cursor.fetchall()
    cursor.close()

    cursor = conn.cursor()

    for rowid, label, request_idx, request_len, response_idx, response_len in rrs:
        request = get_request(dir, pcap_id, label, request_idx, request_len)
        response = get_response(dir, pcap_id, label, response_idx, response_len)

        cursor.execute \
                (
                "UPDATE tbl_reqrep SET x_request_headers = ?, x_response_headers = ? WHERE rowid = ?",
                [
                    repr(request.headers),
                    repr(response.headers),
                    rowid
                ]
            )
        cursor.execute \
                (
                "UPDATE tbl_reqrep "
                "SET "
                "  x_url = ?,"
                "  x_content_type = ?,"
                "  x_status_code = ?"
                "WHERE "
                " ROWID = ?",
                [
                    "%s %s %s" % (request.method, request.headers.get('host'), request.uri),
                    response.headers.get('content-type'),
                    response.headers.get('location'),
                    rowid
                ]
            )
    cursor.close()
    conn.commit()


if __name__ == '__main__':
    db_name = sys.argv[1]
    pcap_id = int(sys.argv[2])
    tcptrace_result_dir = sys.argv[3]

    http_times_file_path = os.path.join(tcptrace_result_dir, "%s_http.times" % pcap_id)

    file = open(http_times_file_path)
    conn = sqlite3.connect(db_name)
    feed_for_reqrep_of_all_conn(conn, pcap_id)
    show_headers_of_all_reqrep(conn, pcap_id, tcptrace_result_dir)


