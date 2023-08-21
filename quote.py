import time
import argparse
import os
import sys
import random
import re
import requests


def logger( level, message ):
    print( '[' + str(int( time.time() )) + ']' + '[' + level + ']' + ' ' + message, file = sys.stderr )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument( '-d', '--debug', help = 'print more information during the run', action = 'store_true' )
    parser.add_argument( '-b', '--book', help = 'manually specify the book number', type = int )

    args = parser.parse_args()

    try:
        with open( os.path.dirname(__file__) + '/catalog.txt' ) as catalog_fh:
            catalog = catalog_fh.read().splitlines()
    except Exception as e:
        s = str(e)
        logger( 'error', s )
        sys.exit(1)

    download_error_count = 0
    while True:
        book_number = None
        book_name = None

        if args.book:
            book_number = args.book
            for line in catalog:
                if line == str(book_number) + '.txt' or line == str(book_number) + '-0.txt':
                    book_name = line
                    break

            if book_name is None:
                logger( 'error', 'book not found - ' + str(book_number) )
                sys.exit(1)

        else:
            random.seed( a = time.time() )
            book_name = catalog[ random.randint( 0, len(catalog)-1 ) ]
            matches = re.match( '^(\d+)', book_name )
            book_number = matches[0]

        page_link = 'https://gutenberg.org/ebooks/' + book_number
        book_link = 'https://aleph.pglaf.org'

        if len(book_number) == 1:
            book_link = book_link + '/0/' + str(book_number) + '/' + book_name
        else:
            for i in range( len(book_number)-1 ):
                book_link = book_link + '/' + str(book_number[i])

            book_link = book_link + '/' + str(book_number) + '/' + book_name

        if args.debug:
            logger( 'debug', 'page link: ' + page_link )
            logger( 'debug', 'book link: ' + book_link )

        response = requests.get( book_link )

        if response.status_code != 200:
            download_error_count = download_error_count + 1
            logger( 'error', 'download response was ' + str(response.status_code) + ' - ' + str(book_number) )

            if args.book:
                sys.exit(1)
            elif download_error_count == 20:
                logger( 'error', 'download limit (20) reached' )
            else:
                continue

        book_text = response.text

        break


if __name__ == '__main__':
    main()
