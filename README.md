# Internet Archive's BookReader

This *Docker* image provides an easy way to instantiate a [Bookreader](https://archive.org/details/BookReader) from a collection of images or an ebook such as a PDF or an EPUB file.  
Its main purpose is to offer an online reader for scanned documents and magazine, but can serve all kind of electronic documents as well.  

All the files are generated in a user provided folder and can be served as-is, with no requirement on the server side.

## Examples

* Generated from a collection of images:  
  [An article comparing the Atari Falcon to the Amiga 4000 from a vintage French magazine](https://books.xtof.info/demos/tilt)
* Generated from a PDF:  
  [An article from Byte magazine about the Next Computer](https://books.xtof.info/demos/byte)
* Generated from an EPUB:  
  [An extract of "The Complete Works of William Shakespeare"](https://books.xtof.info/demos/shakespeare)


As with any Docker based project, you have to first generate the image (only once), then run it.
## Build the image

```bash
docker build . -t <IMAGE_NAME>
```
* **IMAGE_NAME** : name of the docker image

## Generate the bookreader

```bash
docker run --rm -v <OUTPUT_DIR>:/data -v <BOOK_DIR>:/book <IMAGE_NAME> python3 /build.py <OPTIONS>
```

* **BOOK_DIR** : Directory containing images of the pages of the book or an ebook file. The path must be absolute  
* **OUTPUT_DIR** : Directory containing the files to be served to read the book. The path must be absolute

Inline help of *build.py*:

```bash
usage: build.py [-h] [--ebook EBOOK] [--start START] [--stop STOP]

optional arguments:
  -h, --help     show this help message and exit
  --ebook EBOOK  ebook file in the **BOOK_DIR** directory
  --start START  First page (counting from 0)
  --stop STOP    Last page (counting from 0)
```
