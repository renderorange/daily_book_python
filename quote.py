import time
import argparse
import os
import sys


def logger( level, message ):
    print( '[' + str(int( time.time() )) + ']' + '[' + level + ']' + ' ' + message, file = sys.stderr )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument( '-d', '--debug', help = 'print more information during the run', action = 'store_true' )
    parser.add_argument( '-b', '--book', help = 'manually specify the book number', type = int )

    args = parser.parse_args()

    try:
        with open( os.path.dirname(__file__) + '/catalog.txt' ) as catalog_fh:
            catalog = catalog_fh.read()
    except Exception as e:
        s = str(e)
        logger( 'error', s )
        sys.exit(1)


if __name__ == '__main__':
    main()
