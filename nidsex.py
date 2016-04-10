import nids
import dpkt

_http_callback = lambda request, response: None

request_filter = lambda request: True
response_filter = lambda response: True
request_max_length = 1 * 1024 * 1024
response_max_length = 2 * 1024 * 1024

_http_talks = dict()


class HttpTalk(object):
    request = None
    response = None

    def is_ready(self):
        return self.request is not None and self.response is not None


def _tcp_callback(tcp):
    ((src, sport), (dst, dport)) = tcp.addr
    if tcp.nids_state == nids.NIDS_JUST_EST:
        tcp.client.collect = 1
        tcp.server.collect = 1
        return

    if tcp.addr not in _http_talks:
        _http_talks[tcp.addr] = HttpTalk()

    http_talk = _http_talks[tcp.addr]

    if tcp.client.count_new > 0 and tcp.server.count - tcp.server.offset > 0:
        # TODO make Request object
        request_raw_data = tcp.server.data
        request = dpkt.http.Request(request_raw_data)
        request.raw_data = request_raw_data
        http_talk.request = request
        print request
        # TODO discard tcp.server.data
        tcp.discard(len(request_raw_data))
        pass
    elif tcp.server.count_new > 0 and tcp.client.count - tcp.client.offset > 0:
        # TODO make Response object
        response_raw_data = tcp.server.data
        response = dpkt.http.Response(response_raw_data)
        response.raw_data = response_raw_data
        http_talk.response = response
        print response
        # TODO discard tcp.client.data
        tcp.discard(len(response_raw_data))
        pass
        if http_talk.is_ready():
            _http_callback(http_talk.request, http_talk.response)
    else:
        tcp.discard(0)



def register_http(http_callback):
    _http_callback = http_callback
    nids.register_tcp(_tcp_callback)
