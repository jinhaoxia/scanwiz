#!/usr/bin/env python
# coding=utf-8
import sys

import sqlite3
import logging

from StringIO import StringIO

from _6_url_oracle import UrlOracle

logging.root.level = logging.DEBUG


def main():
    db_name = sys.argv[1]
    seq_output = sys.argv[2]
    map_output = sys.argv[3]

    seq_output_file = open(seq_output, mode='w+')
    map_output_file = open(map_output, mode='w+')

    url_oracle = UrlOracle()

    conn = sqlite3.connect(db_name)

    cursor = conn.cursor()

    cursor.execute('SELECT DISTINCT pcap_id FROM tbl_reqrep WHERE pcap_id > 0')
    pcap_ids = cursor.fetchall()

    for pcap_id in pcap_ids:
        cursor.execute(""
                       "SELECT "
                       "    x_request_url "
                       "FROM "
                       "    tbl_reqrep "
                       "WHERE "
                       "    pcap_id = ? "
                       "    AND "
                       "    ( "
                       "        x_response_content_type LIKE '%html%' "
                       "        OR "
                       "        x_response_content_type LIKE '%json%' "
                       "        OR "
                       "        x_response_status_code = '302'"
                       "    ) "
                       "    AND "
                       "    x_request_url NOT LIKE '%adfront%' "
                       "ORDER BY "
                       "    ROWID ASC "
                       ,
                       pcap_id
                       )
        urls = cursor.fetchall()
        buffer = StringIO()
        logging.debug('pcap_id = %d' % pcap_id)

        for url, in urls:
            url_class_id = url_oracle.ask(url)
            logging.debug('%d %s' % (url_oracle.ask(url), url))
            buffer.write('%d -1 ' % url_class_id)
        buffer.write('-2')

        seq_output_file.write(buffer.getvalue())
        seq_output_file.write('\n')

        logging.debug('=== ' + buffer.getvalue())
        logging.debug('=====================')

    cursor.close()
    conn.close()

    map_output_file.write(repr(url_oracle.memory))


if __name__ == '__main__':
    main()
