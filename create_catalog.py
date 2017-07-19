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
    ret = o_xml.xpath('//./div[@class="selector-content"]')
    log.debug('Found {} titles in XML'.format(len(ret)))
    return ret


def normalize_data(node_list):
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


def print_list(items, delim='\t'):
    log.debug('Delimiter set to [{}]'.format(delim))
    writer = csv.DictWriter(sys.stdout, fieldnames=items[0].keys(), delimiter=delim)
    writer.writeheader()
    writer.writerows(items)


def _main(opts):
    if not opts.verbose:
        logging.disable(logging.DEBUG)
    else:
        log.debug('Verbose output enabled')

    log.info('Opening [{}] to looked for saved library HTML'.format(opts.input_file))
    with open(opts.input_file) as f:
        root = html.parse(f)
    node_list = make_list(root)
    title_info = normalize_data(node_list=node_list)
    print_list(title_info)


if __name__ == '__main__':
    opts = get_opts()
    _main(opts)