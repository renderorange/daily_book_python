# daily_book_python

`daily_book_python` finds quotes in free ebooks at [project gutenberg](https://www.gutenberg.org).

## USAGE

```bash
$ ./quote.py --help
usage: quote.py [-h] [-d] [-b BOOK]

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           print more information during the run
  -b BOOK, --book BOOK  manually specify the book number
```

### Find a quote for a random book

```bash
$ ./quote.py
"Ah, well--a--day!--do what we can for him," said Trim, maintaining his point, "the poor soul will die."  https://gutenberg.org/ebooks/21775
```

### Find a quote from a specific book

```bash
$ ./quote.py --book 220
"I won't be there to see you go," I began with an effort. "The rest ... I only hope I have understood, too."  https://gutenberg.org/ebooks/220
```

### Error and debug output is sent to STDERR

To print more information during the run, `--debug` can be defined to send additional output to `STDERR`.

```bash
$ ./quote.py --book 220 --debug 2> stderr.o > stdout.o
$ cat stderr.o
[1692811696][debug] page link: https://gutenberg.org/ebooks/220
[1692811696][debug] book link: https://aleph.pglaf.org/2/2/220/220-0.txt
[1692811696][debug] parser is in head
[1692811696][debug] parser is in body
[1692811696][debug] parser is in footer
[1692811696][debug] title: The Secret Sharer
[1692811696][debug] author: Joseph Conrad
[1692811696][debug] paragraphs found: 356
[1692811696][debug] quote was found: "Hadn't the slightest idea. I am the mate of her--" He paused and corrected himself. "I should say I _was_." 
[1692811696][debug] quote was found: "Unless you manage to recover him before tomorrow," I assented, dispassionately.... "I mean, alive." 
[1692811696][debug] quote was found: "Bless my soul! Do you mean, sir, in the dark amongst the lot of all them islands and reefs and shoals?" 
[1692811696][debug] quote was found: "I won't be there to see you go," I began with an effort. "The rest ... I only hope I have understood, too." 
```

Non debug information and error output is also sent to `STDERR`.

```bash
$ ./quote.py 2> stderr.o > stdout.o
$ cat stderr.o
[1692811795][error] quote was not found - 26726
$ cat stdout.o 
"No," he said to me, "I cannot do that. I'll live like the old Bradlaugh, or I'll go under."  https://gutenberg.org/ebooks/30205
```

```bash
$ ./quote.py --book 52751 2> stderr.o
$ cat stderr.o
[1692811864][error] book not found - 52751
```

```bash
$ ./quote -m 46392 2> stderr.o
$ cat stderr.o
[1692811902][error] quote was not found - 46392
```

## COPYRIGHT AND LICENSE

`daily_book_python` is Copyright (c) 2023 Blaine Motsinger under the MIT license.

## AUTHOR

Blaine Motsinger `blaine@renderorange.com`
