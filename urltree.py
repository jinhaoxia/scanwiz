# coding=utf-8
from furl import furl


#################################################
# URL前缀树相关                                   #
#################################################


def make_url_vector(url):
    """
    生成url向量
    :param url: 要弄得url
    :return: (协议,域名,端口,[目录文件列表],[参数名列表],[参数值列表])
    """
    oo = furl(url)
    url_vector = (oo.scheme, oo.host, oo.port, oo.path.segments, oo.args.keys(), oo.args.values())
    # return (oo.scheme, oo.host, oo.port, oo.path.segments, oo.args, oo.fragment.path.segments, oo.fragment.args)
    return url_vector


if __name__ == '__main__':
    url1 = 'http://www.zjiet.edu.cn/content/detail.php?sid=33&cid=600&id=3851#haha'
    url2 = 'http://www.zjiet.edu.cn/'
    url3 = 'http://www.zjiet.edu.cn'

    print make_url_vector(url1)

    print make_url_vector(url2)

    print make_url_vector(url3)
