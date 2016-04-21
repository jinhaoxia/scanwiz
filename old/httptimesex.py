#!/usr/bin/env python
import sys
import re


def main():
    regex_conn = "^conn (?<clientAddr>\d+\.\d+\.\d+\.\d+):(?<clientPort>\d+) (?<serverAddr>\d+\.\d+\.\d+\.\d+):(?<serverPort>\d+) (?<label>.+) (?<bytesOfRequests>\d+) (?<numberOfRequests>\d+) (?<bytesOfResponses>\d+) (?<numberOfResponses>\d+)$"
    regex_reqrep = "^reqrep (?<clientAddr>\d+\.\d+\.\d+\.\d+):(?<clientPort>\d+) (?<serverAddr>\d+\.\d+\.\d+\.\d+):(?<serverPort>\d+) (?<label>.+) (?<ts1>\d+\.\d+) (?<ts2>\d+\.\d+) (?<ts3>\d+\.\d+) (?<requestLength>\d+) (?<responseLength>\d+) (?<responseCode>\d+) (?<method>.+) (?<url>.+) (?<version>.+) (?<contentType>.*)$"

    pattern_conn = re.compile(regex_conn)
    pattern_reqrep = re.compile(regex_reqrep)

    file = sys.stdin

    for line in file:
        if pattern_conn.match(line):
            print 'conn'
        elif pattern_reqrep.match(line):
            print 'reqrep'
        else:
            print 'other'

    pass


if __name__ == '__main__':
    main()
