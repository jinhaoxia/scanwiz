#!/usr/bin/env python
# coding=utf-8
import sys
import os
import sqlite3
import _4_extract_headers_from_http_times
import pprint


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
        print label[0]
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

    for rll in rlls:
        cursor.execute("UPDATE tbl_reqrep SET request_idx=?, response_idx=? WHERE ROWID = ?",
                       (request_idx, response_idx, rll[0]))
        request_idx += rll[1]
        response_idx += rll[2]

    cursor.close()
    conn.commit()

request_headers = list()
response_headers = list()

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
    for rr in rrs:
        rowid, label, request_idx, request_len, response_idx, response_len = rr
        request = _4_extract_headers_from_http_times.get_request_headers(dir, pcap_id, label, request_idx, request_len)
        response = _4_extract_headers_from_http_times.get_response_headers(dir, pcap_id, label, response_idx,
                                                                           response_len)
        # pprint.pprint({
        #     'rowid': rowid,
        #     'request': request,
        #     'response': response
        # })
        global  request_headers, response_headers
        request_headers += request.keys()
        response_headers += response.keys()


if __name__ == '__main__':
    db_name = sys.argv[1]
    pcap_id = sys.argv[2]
    tcptrace_result_dir = sys.argv[3]

    http_times_file_path = os.path.join(tcptrace_result_dir, "%s_http.times" % pcap_id)

    file = open(http_times_file_path)
    conn = sqlite3.connect(db_name)
    feed_for_reqrep_of_all_conn(conn, pcap_id)
    show_headers_of_all_reqrep(conn, pcap_id, tcptrace_result_dir)

    print set(request_headers)
    print
    print set(response_headers)