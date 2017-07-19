import argparse
import csv
import logging
import json
import os
import sys
from collections import OrderedDict
from pprint import pprint

from lxml import html, etree

log = logging.getLogger('create_catalog')

if sys.version_info.major == 2:
    FileNotFoundError = IOError

TYPE_FN = 'publishers.json'


def scrub_unicode(text):
    text = text.replace(u'â€™', u"'")
    text = text.replace(u'â\x80\x99', u"'")

    return text


def make_list(o_xml):
    ret = o_xml.xpath('//./div[@class="selector-content"]')
    log.debug('Found {} titles in XML'.format(len(ret)))
    return ret


def get_publishers(file=TYPE_FN):
    types = dict()
    try:
        with open(file) as f:
            types = json.load(f)  # type: dict
    except (IOError, FileNotFoundError):
        log.error('Could not locate [{}] to read publisher info'.format(file))
    except ValueError:
        log.error('[{}] appears to be invalid JSON. See repo for expected format'.format(file))
    return types


def normalize_data(node_list):
    l = []
    publisher_info = get_publishers(file=TYPE_FN)
    for el in node_list:
        title = el.find('.//h2').text
        publisher = el.find('.//p').text

        title = scrub_unicode(title)
        title_type = assign_type(publisher, pub_info_dict=publisher_info)

        d = OrderedDict({'title': title, 'type': title_type})
        l.append(d)
    return l


def assign_type(publisher, pub_info_dict):
    assignment = ''
    for category in pub_info_dict.values():
        publishers = category.get('publishers')
        if not isinstance(publishers, list):
            return ''
        if publisher.lower() in [p.lower() for p in publishers]:
            display = category.get('display_name')
            log.debug('Found type assignment for [{}] => [{}]'.format(publisher, display))
            assignment = display
            break
    if not assignment:
        log.debug('Unassigned type for publisher: [{}]'.format(publisher))

    return assignment


def get_opts():
    parser = argparse.ArgumentParser('Parse the saved HTML file from Humble Bundle Library')
    parser.add_argument('-i', '--input-file', required=True, help='The saved Humble Bundle Library file')
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    return parser.parse_args()


def order_fieldnames(fieldnames):
    TITLE = 'title'
    if not isinstance(fieldnames, list):
        return fieldnames
    log.debug('Forcing {} to be first column'.format(TITLE))
    if TITLE != fieldnames[0] and TITLE in fieldnames:
        del fieldnames[fieldnames.index(TITLE)]
        fieldnames = [TITLE] + fieldnames
    return fieldnames


def print_list(items, delim='\t'):
    log.debug('Delimiter set to [{}]'.format(delim))
    fieldnames = order_fieldnames(list(items[0].keys()))
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, delimiter=delim)
    writer.writeheader()
    writer.writerows(items)


def _main(opts):
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
    if not opts.verbose:
        logging.disable(logging.DEBUG)
    else:
        log.debug('Verbose output enabled')

    log.info('Opening [{}] to looked for saved library HTML'.format(opts.input_file))
    with open(opts.input_file) as f:
        root = html.parse(f)
    node_list = make_list(root)
    log.debug('Normalizing data...')
    title_info = normalize_data(node_list=node_list)
    log.debug('Printing data...')
    print_list(title_info)
    log.info('All done. Bye!')


if __name__ == '__main__':
    opts = get_opts()
    _main(opts)
