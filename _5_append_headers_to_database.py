#!/usr/bin/env python
# coding=utf-8
import sys
import os
import sqlite3
import pprint

from furl import furl

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

        x_request_method = request.method
        x_request_host = request.headers.get('host')
        x_request_uri = request.uri
        x_request_url = 'http://%s%s' % (x_request_host, x_request_uri)
        x_request_referer = request.headers.get('referer')
        x_request_cookie = request.headers.get('cookie')
        x_response_content_type = response.headers.get('content-type')
        x_response_status_code = response.status
        x_response_location = response.headers.get('location')
        x_response_cache_control = response.headers.get('cache-control')
        x_response_etag = response.headers.get('etag')
        x_response_set_cookie = response.headers.get('set-cookie')
        if x_response_set_cookie:
            x_response_set_cookie = repr(x_response_set_cookie)
        if type(x_response_cache_control) is list:
            x_response_cache_control = x_response_cache_control[0]
        cursor.execute(
            "UPDATE tbl_reqrep SET o_request_headers = ?, o_response_headers = ? WHERE rowid = ?",
            [
                repr(request.headers),
                repr(response.headers),
                rowid
            ]
        )
        cursor.execute(
            'UPDATE tbl_reqrep\n'
            'SET\n'
            '  x_request_method = ?,\n'
            '  x_request_host = ?,\n'
            '  x_request_uri = ?,\n'
            '  x_request_url = ?,\n'
            '  x_request_referer = ?,\n'
            '  x_request_cookie = ?,\n'
            '  x_response_content_type = ?,\n'
            '  x_response_status_code = ?,\n'
            '  x_response_location = ?,\n'
            '  x_response_cache_control = ?,\n'
            '  x_response_etag = ?,\n'
            '  x_response_set_cookie = ?\n'
            'WHERE\n'
            '  ROWID = ?\n',
            [
                x_request_method,
                x_request_host,
                x_request_uri,
                x_request_url,
                x_request_referer,
                x_request_cookie,
                x_response_content_type,
                x_response_status_code,
                x_response_location,
                x_response_cache_control,
                x_response_etag,
                x_response_set_cookie,
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
