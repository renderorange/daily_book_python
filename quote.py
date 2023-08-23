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

        # replace smart quotes
        line = re.sub('“', '"', line)
        line = re.sub('”', '"', line)
        line = re.sub('’', "'", line)

        if mark_head == 1:
            header.append(line)
        elif mark_body == 1:
            body.append(line)
        elif mark_footer == 1:
            footer.append(line)

    return header, body, footer


def process(header, body):
    title_regex = re.compile('^Title:\\s+(.+)')
    author_regex = re.compile('^Author:\\s+(.+)')
    title = None
    author = None

    for line in header:
        if 'The New McGuffey' in line:
            return None, 'book is The New McGuffey Reader'

        if 'Language:' in line and 'English' not in line:
            return None, "book isn't in English"

        if 'Title:' in line:
            match = title_regex.search(line)
            title = match.group(1)
            if args.debug:
                logger('debug', 'title: ' + title)

        if 'Author:' in line:
            match = author_regex.search(line)
            author = match.group(1)
            if args.debug:
                logger('debug', 'author: ' + author)

    if title is None:
        return None, 'title was not found'

    if author is None:
        return None, 'author was not found'

    build_variable = ''
    paragraphs = []

    for line in body:
        if len(line) > 0:
            build_variable = '{}{} '.format(build_variable, line)
        else:
            paragraphs.append(build_variable)
            build_variable = ''

    if args.debug:
        logger('debug', 'paragraphs found: ' + str(len(paragraphs)))

    quote_regex = re.compile('^["].+["]\\s*$')
    quotes = []

    for paragraph in paragraphs:
        match = quote_regex.search(paragraph)
        if match is not None:
            if len(paragraph) > 90 and len(paragraph) < 113:
                quotes.append(paragraph)
                if args.debug:
                    logger('debug', 'quote was found: ' + paragraph)

    if len(quotes) == 0:
        return None, 'quote was not found'

    return quotes, None


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
        with open(os.path.dirname(__file__) + '/catalog.txt') as catalog_fh:
            catalog = catalog_fh.read().splitlines()
    except Exception as e:
        s = str(e)
        logger('error', s)
        sys.exit(1)

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

    book_number_regex = re.compile('^(\\d+)')
    download_error_count = 0

    while True:
        if args.book is None:
            random.seed(a=time.time())
            book_name = catalog[random.randint(0, len(catalog) - 1)]
            match = book_number_regex.search(book_name)
            book_number = str(match.group(1))

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
        response.encoding = 'utf-8'

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
        quotes, error = process(header, body)

        if error is not None:
            logger('error', error + ' - ' + book_number)
            if args.book:
                sys.exit(1)
            else:
                continue

        quote = ''

        if len(quotes) > 1:
            random.seed(a=time.time())
            quote = quotes[random.randint(0, len(quotes) - 1)]
        else:
            quote = quotes[len(quotes) - 1]

        print('{} {}'.format(quote, page_link))

        break


if __name__ == '__main__':
    main()
