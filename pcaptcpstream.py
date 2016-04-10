import nids
import nidsex


def http_callback(request, response):
    print request
    print response


nids.param("filename", "/Users/jinhaoxia/Desktop/http.pcap")
nids.param("pcap_filter", "port 80")



nids.init()
nidsex.register_http(http_callback)
nids.run()
