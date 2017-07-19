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
    for el in node_list:
        title = el.find('.//h2').text
        publisher = el.find('.//p').text

        title = scrub_unicode(title)
        title_type = assign_type(publisher)

        d = OrderedDict({'title': title, 'type': title_type})
        l.append(d)
    return l


TYPE_FN = 'publishers.json'
def assign_type(publisher, src_file=TYPE_FN):
    log.debug('Looking for type assignment for publisher: [{}]'.format(publisher))
    if not os.path.isfile(src_file):
        log.error('Could not locate [{}] to read publisher info'.format(src_file))
        return ''
    assignment = ''
    try:
        with open(src_file) as f:
            types = json.load(f)  # type: dict
        for title_type in types.values():
            publishers = title_type.get('publishers')
            if not isinstance(publishers, list):
                return ''
            if publisher.lower() in [p.lower() for p in publishers]:
                display = title_type.get('display_name')
                log.debug('Found type assignment for [{}] => [{}]'.format(publisher, display))
                assignment = display
                break
        if not assign_type:
            log.debug('Unassigned type for publisher: [{}]'.format(publisher))
    except IOError:
        log.error('Could not locate [{}] to read publisher info'.format(src_file))
    except ValueError:
        log.error('[{}] appears to be invalid JSON. See repo for expected format'.format(src_file))
        
    return assignment


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
