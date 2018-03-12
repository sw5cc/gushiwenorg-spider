# -*- coding: utf-8 -*-

import types
from w3lib.html import remove_entities
from urllib.parse import urlparse, urljoin


NULL = [None,'null']


list_first_item = lambda x:x[0] if x else None


def strip_nl(arg):
    strip_list = ['\n', '，']
    return [i for i in arg if i not in strip_list]


def good_to_int(arg):
    ret = []
    for i in arg:
        ret.append(int(i[len('\xa0'):]))
    return ret


def clean_link(link_text):
    """
        Remove leading and trailing whitespace and punctuation
    """

    return link_text.strip("\t\r\n '\"")


clean_url = lambda base_url,u: urljoin(base_url, remove_entities(clean_link(u)))
"""
    remove leading and trailing whitespace and punctuation and entities from the given text.
    then join the base_url and the link that extract
"""


prefix = 'http://so.gushiwen.org/authors/authorsw_'
posfix = '.aspx'


def get_author_page(url):
    v = url[len(prefix):-len(posfix)]
    a_pos = v.find('A')
    author = int(v[:a_pos])
    page = int(v[a_pos+1:])
    return author, page


def get_url(author, page):
    return prefix + str(author) + 'A' + str(page) + posfix


def next_page(url):
    author, page = get_author_page(url)
    page+=1
    return get_url(author, page)


def next_author(url):
    author, page = get_author_page(url)
    page = 1
    author+=1
    return get_url(author, page)
