import argparse
import csv
import logging
import json
import sys
from collections import OrderedDict
from lxml import html, etree
from pprint import pprint

log = logging.getLogger('create_catalog')


def scrub_unicode(text):
    log.debug('Scrubbing string: [{}]'.format(text))
    text = text.replace(u'â€™', u"'")
    text = text.replace(u'â\x80\x99', u"'")
    log.debug('Scrubbed to: [{}]'.format(text))

    return text


def make_list(o_xml):
    l = []
    for el in o_xml.xpath('//./div[@class="selector-content"]/div/h2'):
        text = el.text
        text = scrub_unicode(text)
        l.append(text)
    return l


def assign_type(xml_node):
    EBOOKS = ['oreilly',
              'no starch press',
              'cherie priest',
              'kamui cosplay',
              'wiley',
              ]


def get_opts():
    parser = argparse.ArgumentParser('Parse the saved HTML file from Humble Bundle Library')
    parser.add_argument('-i', '--input-file', required=True, help='The saved Humble Bundle Library file')
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    return parser.parse_args()


def _main(opts):
    with open(opts.input_file) as f:
        root = html.parse(f)
    items = make_list(root)
    for i in items:
        print(i)


if __name__ == '__main__':
    opts = get_opts()
    _main(opts)