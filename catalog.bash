#!/bin/bash

# catalog.bash
# download and process the catalog files from gutenberg.org's pglaf mirror

function error_and_exit {
    echo 'error' && exit 1
}

function warn {
    echo 'error'
}

MIRROR_URL='https://aleph.pglaf.org/cache/epub/feeds/'

echo -n 'downloading new archive - '
WGET=$(wget --prefer-family=IPv4 --quiet -O rdf-files.tar.bz2.new "$MIRROR_URL/rdf-files.tar.bz2")
if [ $? == 1 ]; then error_and_exit; else echo 'done'; fi

if [ -f rdf-files.tar.bz2 ]; then  # the catalog should always exist locally.  don't compare timestamps if it doesn't for some reason.
    echo -n 'checking timestamp on new archive - '
    NEW_TIMESTAMP=$(stat -c %y rdf-files.tar.bz2.new|awk -F':' '{print $1":"$2}')
    if [ $? == 1 ]; then error_and_exit; else echo 'done'; fi  # exit here if there was an issue connecting

    echo -n 'checking timestamp on stored archive - '
    OLD_TIMESTAMP=$(stat -c %y rdf-files.tar.bz2|awk -F':' '{print $1":"$2}')
    if [ $? == 1 ]; then warn; else echo 'done'; fi

    echo -n 'comparing timestamps - '
    NEW_EPOCH=$(date -d "$NEW_TIMESTAMP" +%s)
    OLD_EPOCH=$(date -d "$OLD_TIMESTAMP" +%s)

    if [ $NEW_EPOCH -le $OLD_EPOCH ]; then
        rm -f rdf-files.tar.bz2.new
        echo "up to date" && exit 0
    else
        echo "done"
    fi
fi

echo -n 'renaming new and old archives - '
mv rdf-files.tar.bz2.new rdf-files.tar.bz2
echo 'done'
echo -n 'unpacking the archive - '
BUNZIP2=$(bunzip2 --keep rdf-files.tar.bz2)
if [ $? == 1 ]; then error_and_exit; else echo 'done'; fi
echo -n "untar'ing - "
UNTAR=$(tar xf rdf-files.tar)
if [ $? == 1 ]; then error_and_exit; else echo 'done'; fi

echo -n 'removing tar - '
RM=$(rm -f rdf-files.tar)
if [ $? == 1 ]; then warn; else echo 'done'; fi

echo -n 'building the catalog - '
grep -r txt cache/epub/ | ack --filter cache/epub/ -o --match '\/\d+(?:-0)*\.txt"' | perl -ne 'my $line = $_; $line =~ s/^\///; $line =~ s/"$//; print $line' | sort | uniq > catalog.txt.new
echo 'done'

echo -n 'renaming new and removing the old catalog - '
mv catalog.txt.new catalog.txt
echo 'done'

echo -n 'removing the old cache - '
RM_CACHE=$(rm -rf cache)
if [ $? == 1 ]; then warn; else echo 'done'; fi

echo -n 'adding new catalog to git - '
GIT_ADD=$(git add catalog.txt)
if [ $? == 1 ]; then error_and_exit; else echo 'done'; fi

echo -n 'committing - '
GIT_COMMIT=$(git commit -m 'Update the catalog')
if [ $? == 1 ]; then error_and_exit; else echo 'done'; fi

echo 'pushing to remote'
GIT_PUSH=$(git push origin)
if [ $? == 1 ]; then error_and_exit; else echo 'done'; fi

echo 'all done' && exit 0

