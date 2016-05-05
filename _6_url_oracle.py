#!/usr/bin/env python
# coding=utf-8

import logging
from furl import furl

from collections import namedtuple

UrlParts = namedtuple('UrlParts', ('url', 'website', 'paths', 'params', 'values'))


def get_url_parts(url):
    website = '%s://%s/' % (url.scheme, url.host)
    paths = url.path.segments
    items = sorted(url.args.items())
    params = tuple(map(lambda x: x[0], items))
    values = tuple(map(lambda x: x[1], items))

    url_parts = UrlParts(url.url, website, paths, params, values)
    logging.debug(url_parts)

    return url_parts


class UrlOracle(object):
    tree = {}
    memory = {}
    counter = 0

    def get_mapping(self):
        return self.memory.items()

    def ask(self, url):
        if type(url) is str or type(url) is unicode:
            url = furl(url)

        if url.url in self.memory:
            return self.memory[url.url]

        url_parts = get_url_parts(url)

        logging.info(url)
        logging.info(url_parts)

        if url_parts.website not in self.tree:
            self.tree[url_parts.website] = {}

        folder_tree = self.tree[url_parts.website]

        for path in url_parts.paths:
            if path not in folder_tree:
                folder_tree[path] = {}
            folder_tree = folder_tree[path]

        if url_parts.params not in folder_tree:
            folder_tree[url_parts.params] = self.counter
            self.memory[url.url] = self.counter
            self.counter += 1

        logging.info(folder_tree[url_parts.params])
        return folder_tree[url_parts.params]


def main():
    logging.root.level = logging.INFO
    f = open('url-list.txt')

    url_oracle = UrlOracle()

    while True:
        line = f.readline()
        if not line:
            break
        if not line.strip():
            continue
        url = furl(line.strip())

        url_oracle.ask(url)

    pass


if __name__ == '__main__':
    main()
