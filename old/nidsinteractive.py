# coding=utf-8
import nids


def _interactive_callback_default(request, response):
    print "<<<REQUEST>>>"
    print request
    print "<<<RESPONSE>>>"
    print response


_interactive_callback = _interactive_callback_default


class _Connection(object):
    data_packet_seq = list()
    addr = None


_connections = dict()


def _tcp_callback(tcp):
    if tcp.nids_state == nids.NIDS_JUST_EST:
        tcp.client.collect = 1
        tcp.server.collect = 1
        connection = _Connection()
        connection.addr = tcp.addr
        _connections[tcp.addr] = connection
        return

    connection = _connections[tcp.addr]

    if tcp.nids_state == nids.NIDS_DATA:
        if tcp.client.count_new > 0:
            if len(connection.data_packet_seq) > 0 and connection.data_packet_seq[-1] < 0:
                del connection.data_packet_seq[-1]
            connection.data_packet_seq.append(-tcp.client.count_new)
        elif tcp.server.count_new > 0:
            if len(connection.data_packet_seq) > 0 and connection.data_packet_seq[-1] > 0:
                del connection.data_packet_seq[-1]
            connection.data_packet_seq.append(tcp.server.count_new)

        tcp.discard(0)
        return

    # 进入了结束状态
    last_request_idx = 0
    last_response_idx = 0
    for i in range(0, len(connection.data_packet_seq), 2):

        request = tcp.server.data[last_request_idx:connection.data_packet_seq[i]]
        last_request_idx = connection.data_packet_seq[i]

        response = None
        if i + 1 < len(connection.data_packet_seq):
            response = tcp.client.data[last_response_idx: -connection.data_packet_seq[i + 1]]
            last_response_idx = -connection.data_packet_seq[i + 1]
        _interactive_callback(request, response)
        pass


def register_tcp_interactive(interactive_callback = _interactive_callback_default):
    global __interactive_callback
    __interactive_callback = interactive_callback
    nids.register_tcp(_tcp_callback)
