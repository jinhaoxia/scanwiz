#!/usr/bin/env python
# coding=utf-8

import http
import sys
import os
import json


#################################################
# 根据文件名,起始位置,长度,获取header                #
#################################################


def get_request(dir, pcap_id, label, req_idx, req_len):
    client, server = tuple(label.split('2'))

    # 打开客户端发送的数据,找到请求,处理完后关闭
    req_file = open(os.path.join(dir, ('%s_%s2%s_contents.dat' % (pcap_id, client, server))))
    req_file.seek(req_idx)
    req_str = req_file.read(req_len)
    req_file.close()

    # 解析请求,忽略请求体,只解析请求头部
    req = http.Request()
    req.unpack(req_str, False)

    return req


def get_response(dir, pcap_id, label, res_idx, res_len):
    client, server = tuple(label.split('2'))

    # 打开服务器发送的数据,找到响应,处理完后关闭
    res_file = open(os.path.join(dir, ('%s_%s2%s_contents.dat' % (pcap_id, server, client))))
    res_file.seek(res_idx)
    res_str = res_file.read(res_len)
    res_file.close()

    # 解析响应,忽略响应体,只解析响应头部
    res = http.Response()
    res.unpack(res_str, False)

    return res


if __name__ == '__main__':
    dir = sys.argv[1]
    pcap_id = sys.argv[2]
    label = sys.argv[3]
    req_idx = int(sys.argv[4])
    req_len = int(sys.argv[5])
    res_idx = int(sys.argv[6])
    res_len = int(sys.argv[7])

    # 返回返回处理结果
    result = {
        # 'request_raw': req_str,
        # 'response_raw': res_str,
        'request_headers': get_request_headers(dir, pcap_id, label, req_idx, req_len),
        'response_headers': get_response_headers(dir, pcap_id, label, res_idx, res_len),
    }

    print json.dumps(result)
