#!/usr/bin/env python
# coding=utf-8
import sys
import codecs
import logging

logging.root.level = logging.DEBUG

from furl import furl


class UrlRecover(object):
    id_2_url_class_map = {}

    def __init__(self, ori_map):
        for url, id in ori_map.items():
            if id not in self.id_2_url_class_map:
                ffurl = furl(url)
                for param in ffurl.args.keys():
                    ffurl.args[param] = ''
                self.id_2_url_class_map[id] = ffurl.url
                logging.debug('learn id: %d for url: %s' % (id, ffurl.url))
        logging.debug(repr(self.id_2_url_class_map))

    def ask(self, id):
        if id in self.id_2_url_class_map:
            return self.id_2_url_class_map[id]
        else:
            return '<UNKNOWN>'


def main():
    ori_map_file = open(sys.argv[1])

    spmf_ans_file = codecs.open(sys.argv[2])

    lines_need_skip = int(sys.argv[3]) # 8

    ori_map = eval(ori_map_file.read())

    url_recover = UrlRecover(ori_map)

    for i in range(lines_need_skip):
        spmf_ans_file.readline()

    while True:
        line = spmf_ans_file.readline()

        if not line:
            break

        numbers = map(int, line.split()[:-2])

        for number in numbers:
            if number == -1:
                pass
            else:
                print url_recover.ask(id=number)
        print

    pass


if __name__ == '__main__':
    main()
