#!/usr/bin/env python
# coding=utf-8
import sqlite3
import httptimes2headers
import pprint


def feed_for_reqrep_of_all_conn(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT label FROM tbl_conn')
    labels = cursor.fetchall()
    cursor.close()
    for label in labels:
        print label[0]
        feed_for_reqrep_of_one_conn(conn, label[0])
    pass


def feed_for_reqrep_of_one_conn(conn, conn_label):
    cursor = conn.cursor()
    cursor.execute("SELECT reqrep_id, request_len, response_len FROM tbl_reqrep WHERE label = ? ORDER BY reqrep_id ASC",
                   (conn_label,))
    ills = cursor.fetchall()
    cursor.close()

    request_idx = 0
    response_idx = 0

    cursor = conn.cursor()

    for ill in ills:
        cursor.execute("UPDATE tbl_reqrep SET request_idx=?, response_idx=? WHERE reqrep_id=?",
                       (request_idx, response_idx, ill[0]))
        request_idx += ill[1]
        response_idx += ill[2]

    cursor.close()
    conn.commit()


def show_headers_of_one_reqrep(conn, reqrep_id):
    pass


def show_headers_of_all_reqrep(conn, dir):
    cursor = conn.cursor()
    cursor.execute(
        'SELECT reqrep_id, label, request_idx, request_len, response_idx, response_len FROM tbl_reqrep ORDER BY ts1 ASC')
    rrs = cursor.fetchall()
    cursor.close()
    for rr in rrs:
        reqrep_id, label, request_idx, request_len, response_idx, response_len = rr
        request = httptimes2headers.get_request_headers(dir, label, request_idx, request_len)
        response = httptimes2headers.get_response_headers(dir, label, response_idx, response_len)
        pprint.pprint({
            'reqrep_id': reqrep_id,
            'request': request,
            'response': response
        })


if __name__ == '__main__':
    file = open('/Users/jinhaoxia/Desktop/httptest/http.times')  # sys.stdin
    conn = sqlite3.connect('test.db')
    # feed_for_reqrep_of_all_conn(conn)
    show_headers_of_all_reqrep(conn, '/Users/jinhaoxia/Desktop/httptest/')
