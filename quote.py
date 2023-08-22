#!/usr/bin/env python3

import time
import argparse
import os
import sys
import random
import re
import requests


def logger(level, message):
    print('[' + str(int(time.time())) + ']' +
          '[' + level + ']' + ' ' + message, file=sys.stderr)


def parse(book):
    header = []
    body = []
    footer = []
    mark_head = 1
    mark_body = 0
    mark_footer = 0

    if args.debug:
        logger('debug', 'parser is in head')

    for line in book:
        if 'START OF THE PROJECT' in line or 'START OF THIS PROJECT' in line:
            if args.debug:
                logger('debug', 'parser is in body')
            mark_head = 0
            mark_body = 1
            continue

        if 'END OF THE PROJECT' in line or 'END OF THIS PROJECT' in line:
            if args.debug:
                logger('debug', 'parser is in footer')
            mark_body = 0
            mark_footer = 1
            continue

        # remove leading and trailing whitespace
        line.strip()

        # correct double spacing
        line = re.sub(' +', ' ', line)

        if mark_head == 1:
            header.append(line)
        elif mark_body == 1:
            body.append(line)
        elif mark_footer == 1:
            footer.append(line)

    return header, body, footer


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-d',
        '--debug',
        help='print more information during the run',
        action='store_true')
    parser.add_argument(
        '-b',
        '--book',
        help='manually specify the book number',
        type=int)

    global args
    args = parser.parse_args()

    try:
        with open(os.path.dirname(__file__) + '/catalog.txt', encoding='utf-8') as catalog_fh:
            catalog = catalog_fh.read().splitlines()
    except Exception as e:
        s = str(e)
        logger('error', s)
        sys.exit(1)

    download_error_count = 0
    while True:
        book_number = None
        book_name = None

        if args.book:
            book_number = str(args.book)
            for line in catalog:
                if line == book_number + '.txt' or line == book_number + '-0.txt':
                    book_name = line
                    break

            if book_name is None:
                logger('error', 'book not found - ' + book_number)
                sys.exit(1)

        else:
            random.seed(a=time.time())
            book_name = catalog[random.randint(0, len(catalog) - 1)]
            matches = re.match('^(\\d+)', book_name)
            book_number = str(matches[0])

        page_link = 'https://gutenberg.org/ebooks/' + book_number
        book_link = 'https://aleph.pglaf.org'

        if len(book_number) == 1:
            book_link = book_link + '/0/' + book_number + '/' + book_name
        else:
            for i in range(len(book_number) - 1):
                book_link = book_link + '/' + book_number[i]

            book_link = book_link + '/' + book_number + '/' + book_name

        if args.debug:
            logger('debug', 'page link: ' + page_link)
            logger('debug', 'book link: ' + book_link)

        response = requests.get(book_link)

        if response.status_code != 200:
            download_error_count = download_error_count + 1
            logger(
                'error',
                'download response was ' +
                str(response.status_code) +
                ' - ' +
                book_number)

            if args.book:
                sys.exit(1)
            elif download_error_count == 20:
                logger('error', 'download limit (20) reached')
            else:
                continue

        book = response.text.splitlines()

        header, body, footer = parse(book)

        # quotes, error = process( header, body )

        break


if __name__ == '__main__':
    main()
