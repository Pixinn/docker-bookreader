## Build the image

```bash
docker build . -t <IMAGE_NAME>
```
**IMAGE_NAME** : name of the docker image

## Run the image to generate the files

```bash
docker run --rm -v <OUTPUT_DIR>:/data <BOOK_DIR>:/book <IMAGE_NAME> python3 /build.py
```
**BOOK_DIR** : Directory the pages of the book. The path must be absolute  
**OUTPUT_DIR** : Directory containing the files to be served to read the book. The path must be absolute
