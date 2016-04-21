import nids
# import nidsex
import nidsinteractive


def http_callback(request, response):
    print request
    print response


nids.param("filename", "/Users/jinhaoxia/Desktop/http2.pcap")
nids.param("pcap_filter", "port 80")



nids.init()
#nidsex.register_http(http_callback)
nidsinteractive.register_tcp_interactive()
nids.run()
