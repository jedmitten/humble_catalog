# -*- coding: utf-8 -*-
import argparse
import csv
import logging
import json
import sys
from collections import OrderedDict

from lxml import html

log = logging.getLogger('create_catalog')

if sys.version_info.major == 2:
    FileNotFoundError = IOError

TYPE_FN = 'publishers.json'
STEAM_KEY = 'steam key'


def scrub_unicode(text):
    '''
    Process special characters used on the HTML
    encoding from ASCII to UTF-8
    Accommodate Python 2.7 and 3.4+
    '''
    try:
        return str(text)
    except UnicodeEncodeError as uee:
        # python 2.5 and higher needs explicit encoding to utf-8
        return text.encode('utf-8')


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


def normalize_data(node_list, include_steam_keys=False):
    l = []
    publisher_info = get_publishers(file=TYPE_FN)
    for el in node_list:
        title = el.find('.//h2').text
        publisher = el.find('.//p').text

        title = scrub_unicode(title)
        if STEAM_KEY in title.lower() and not include_steam_keys:
            log.debug('Skipping steam key in library output')
            continue
        title_type = ''
        skip_pub_assign = False
        if not publisher:
            log.warning('No publisher was found for title: [{}]'.format(title))
            skip_pub_assign = True
        if not publisher_info:
            log.warning('No publisher information JSON was found')
            skip_pub_assign = True
        if skip_pub_assign:
            log.warning('Skipping assignment of publisher for title: [{}]'.format(title))
        else:
            title_type = assign_type(publisher, pub_info_dict=publisher_info)
        d = OrderedDict({'title': title, 'title_pub': publisher, 'type': title_type})
        l.append(d)
    return l


def assign_type(publisher, pub_info_dict):
    assignment = ''
    for category in pub_info_dict.values():
        publishers = category.get('publishers')
        if not isinstance(publishers, list):
            return ''
        try:
            l_pubs = [p.lower() for p in publishers]
        except:
            log.error('Cannot read publishers from category dict: {}'.format(category))
            continue
        if publisher.lower() in l_pubs:
            display = category.get('display_name')
            log.debug('Found type assignment for [{}] => [{}]'.format(publisher, display))
            assignment = display
            break
    if not assignment:
        log.debug('Unassigned type for publisher: [{}]'.format(publisher))
        suggest_type(publisher)

    return assignment


def suggest_type(publisher):
    TEXT = 'text'
    CAT = 'category'
    GAME = 'Game'
    BOOK = 'Book'
    SUGGESTIONS = [
        {TEXT: 'game', CAT: GAME},
        {TEXT: 'book', CAT: BOOK},
        {TEXT: 'publish', CAT: BOOK},
        {TEXT: 'press', CAT: BOOK},
        {TEXT: 'interactive', CAT: GAME},
        {TEXT: 'studio', CAT: GAME},
        {TEXT: 'software', CAT: GAME},
    ]
    if not publisher:
        return
    for SUG in SUGGESTIONS:
        if SUG[TEXT].lower() in publisher.lower():
            log.debug('Suggested category for publisher [{}]: [{}]'.format(publisher, SUG[CAT]))
        break


def get_opts():
    parser = argparse.ArgumentParser('Parse the saved HTML file from Humble Bundle Library')
    parser.add_argument('-i', '--input-file', required=True, help='The saved Humble Bundle Library file')
    parser.add_argument('--include-steam', action='store_true', required=False, default=False,
                        help='Include Steam Keys in output')
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
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, delimiter=delim, lineterminator='\n')
    writer.writeheader()
    writer.writerows(items)


def _main(opts):
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
    if not opts.verbose:
        logging.disable(logging.DEBUG)
    else:
        log.debug('Verbose output enabled')

    log.info('Opening [{}] to look for saved library HTML'.format(opts.input_file))
    with open(opts.input_file) as f:
        root = html.parse(f)
    node_list = make_list(root)
    if not node_list:
        log.error('There were no titles found in the file you pointed to')
        log.error('Either the script is out of date or something else is wrong with the HTML')
        sys.exit(1)
    log.debug('Normalizing data...')
    title_info = normalize_data(node_list=node_list, include_steam_keys=opts.include_steam)
    log.debug('Printing data...')
    print_list(title_info)
    log.info('All done. Bye!')


if __name__ == '__main__':
    opts = get_opts()
    _main(opts)