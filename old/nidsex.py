import nids
import dpkt
import StringIO

i = 0


def _http_callback(talk, request, response):
    global i
    i += 1
    print talk, i, 'http://'+request.headers['host']+request.uri
    # print request
    # print response


request_filter = lambda request: True
response_filter = lambda response: True
request_max_length = 1 * 1024 * 1024
response_max_length = 2 * 1024 * 1024


class HttpTalk(object):
    request = None
    response = None

    addr = None

    def __init__(self, addr):
        self.addr = addr

    def __str__(self):
        return str(self.addr)

    request_buffer = StringIO.StringIO()
    response_buffer = StringIO.StringIO()

    def is_ready(self):
        return self.request is not None and self.response is not None

    def take_talk(self):
        if self.is_ready():
            req = self.request
            res = self.response
            self.request = None
            self.response = None
            self.request_buffer.truncate(0)
            self.request_buffer.truncate(0)
            return req, res
        else:
            return None, None

    def feed_client(self, tcp):
        data = tcp.client.data[:tcp.client.count_new]
        self.response_buffer.write(data)
        try:
            self.make_request()
        except:
            tcp.client.collect = 0
            tcp.server.collect = 0
            del http_talks[tcp.addr]
        pass

    def feed_server(self, tcp):
        data = tcp.server.data[:tcp.server.count_new]
        self.request_buffer.write(data)
        try:
            self.make_response()
        except:
            tcp.client.collect = 0
            tcp.server.collect = 0
            del http_talks[tcp.addr]
        pass

    def make_request(self):
        if self.request is None and len(self.request_buffer.getvalue()) > 0:
            self.request = dpkt.http.Request(self.request_buffer.getvalue())
            self.request.raw_data = self.request_buffer.getvalue()
            self.request_buffer.truncate(0)
        pass

    def make_response(self):
        if self.response is None and len(self.response_buffer.getvalue()) > 0:
            self.response = dpkt.http.Response(self.response_buffer.getvalue())
            self.response.raw_data = self.response_buffer.getvalue()
            self.response_buffer.truncate(0)
        pass

    def invoke_callback_if_ready(self):
        if self.is_ready():
            _http_callback(self, *self.take_talk())


http_talks = dict()


def _tcp_callback(tcp):
    ((src, sport), (dst, dport)) = tcp.addr
    if tcp.nids_state == nids.NIDS_JUST_EST:
        tcp.client.collect = 1
        tcp.server.collect = 1

        if tcp.addr not in http_talks:
            http_talks[tcp.addr] = HttpTalk(tcp.addr)

        return

    http_talk = http_talks[tcp.addr]

    if tcp.nids_state in [nids.NIDS_CLOSE, nids.NIDS_TIMED_OUT, nids.NIDS_RESET]:
        try:
            http_talk.make_request()
            http_talk.make_response()
            http_talk.invoke_callback_if_ready()
        except:
            pass
        del http_talks[tcp.addr]

        return

    if tcp.client.count_new > 0:
        http_talk.feed_client(tcp)
    elif tcp.server.count_new > 0:
        http_talk.feed_server(tcp)

    http_talk.invoke_callback_if_ready()


def register_http(http_callback):
    # _http_callback = http_callback
    nids.register_tcp(_tcp_callback)
