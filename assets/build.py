#!/usr/bin/env python3

import argparse
from genericpath import isdir, isfile
import sys
import os
import shutil
import base64
import json
from PIL import Image
from PIL import UnidentifiedImageError
import fitz


SRC = "/book"
DST = "/data"

#SRC = "C:\\Users\\chris\\Temp\\bookreader\\in\\Byte.pdf"
#DST = "C:\\Users\\chris\\Temp\\bookreader\\out"


def GenerateJavascript(options: dict):

    ## Populates JSON with other fields
    options["bookUrl"] = "index.html"
    options["bookTitle"] = ""
    options["thumbnail"] =  options["data"][0][0]["uri"]
    options["imagesBaseURL"] = "pages"
    options["ui"] = "full"
    options["el"] = "#BookReader"
    
    ## Build javascript
    jsPart1 = '''
function instantiateBookReader(selector, extraOptions) {
    selector = selector || '#BookReader';
    extraOptions = extraOptions || {};
    var options = '''
    jsPart2 = ''';
    $.extend(options, extraOptions);
    var br = new BookReader(options);
    br.init();
}
    '''
    javascript = jsPart1 + json.dumps(options) + jsPart2

    ## Write js to file
    with open(os.path.join(DST, "BookReaderJSSimple.js"), 'w') as file:
        file.write(javascript)

    ## copy bookreader files
    shutil.copytree("/bookreader/BookReader", os.path.join(DST, "BookReader"), dirs_exist_ok=True)
    shutil.copytree("/bookreader/BookReaderDemo/assets", os.path.join(DST, "assets"), dirs_exist_ok=True)
    shutil.copyfile("BookReaderDemo/demo-vendor-fullscreen.html", os.path.join(DST, "index.html"))


def JsonProperties(width, height, filepath):

    page = dict()
    page["width"] = int(width)
    page["height"] = int(height)
    page["uri"] = "pages/" + os.path.basename(filepath)

    return page


def GenerateFromPdf(input_file: str):
    # Code from https://www.thepythoncode.com/article/convert-pdf-files-to-images-in-python
    """Converts pdf to image and generates a file by page"""
 
    options = dict()
    data = []

    try:
        os.makedirs(os.path.join(DST, "pages"), exist_ok = True)
        # Open the document
        doc = fitz.open(input_file)
        # Iterate throughout the pages
        for pgNr in range(doc.page_count):

            print("Processing page {}".format(pgNr), flush=True)

            # Compute a pixmap of the page
            page = doc[pgNr]
            pix = page.get_pixmap(dpi=200, alpha=False)

            # Compute output file
            basename = os.path.splitext(os.path.basename(input_file))[0] + str(pgNr)
            urlSafeEncodedBytes = base64.urlsafe_b64encode(basename.encode("utf-8"))
            urlSafeEncodedStr = str(urlSafeEncodedBytes, "utf-8")
            dstImage = os.path.join(DST, "pages", urlSafeEncodedStr)
            dstImage = os.path.splitext(dstImage)[0] + ".webp"

            # Save the pixmap using PIL
            pix.pil_save(dstImage, format="WEBP", quality=50)

            # JSON propoerties
            data.append(JsonProperties(pix.width, pix.height, dstImage))

        # Close the document
        doc.close()

    except Exception as e:
        print("Error: {}".format(e))

    options["data"] = [data]
    return options


def GenerateFromImages(folder: str):

    options = dict()
    data = []

    ## Directory containing images
    ### Copy the "page" files
    files = os.listdir(folder)
    images = []
    for file in files:
        if file.lower().endswith(('.tiff', '.tif', '.png', '.jpg', '.jpeg')): # todo better filtering
            images.append(file)
    if len(images) != 0:

        os.makedirs(os.path.join(DST, "pages"), exist_ok = True)
        for i in range(len(images)):  
            srcImage = os.path.join(folder, images[i])
            urlSafeEncodedBytes = base64.urlsafe_b64encode(images[i].encode("utf-8"))
            urlSafeEncodedStr = str(urlSafeEncodedBytes, "utf-8")
            dstImage = os.path.join(DST, "pages", urlSafeEncodedStr)
            dstImage = os.path.splitext(dstImage)[0] + ".webp"

            try:
                print("Processing {} => {}".format(images[i], dstImage), flush=True)
                ### Save the images
                img = Image.open(srcImage).convert("RGB")
                img.save(dstImage, format="WEBP", quality=50)
                images[i] = dstImage
                ### Build page description
                data.append(JsonProperties(img.width, img.height, dstImage))

            except Exception as e:
                print("Warning: {}".format(e))

    options["data"] = [data]
    return options


if __name__ == '__main__':

    # pdf or epub?
    if len(sys.argv) > 1: 
        ## Arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('--pdf', help='pdf file')
        parser.add_argument('--epub', help='epub file')
        args = parser.parse_args()
        ## Sanity
        if (not args.pdf is None) and  (not args.epub is None):
            print("You have to provide a pdf OR an epub")
            sys.exit(1)

        if (not args.pdf is None):
            filepath = os.path.join(SRC, args.pdf)
        if (not args.epub is None):
            filepath = os.path.join(SRC, args.epub)

        if not os.path.isfile(filepath) or not filepath.lower().endswith(('.pdf', '.epub')):
            print("Cannot process {}: unsupported format.".format(filepath))
            sys.exit(-1)
        
        ## Convert PDF and generate pages
        options = GenerateFromPdf(filepath)
        
        ## Generate the javascript
        GenerateJavascript(options)


    # folder of images?
    else:
        if not os.path.isdir(SRC):
            print("No image in directory {}".format(SRC))
            print("You have to provide an image directory or a pdf/epub file")
            sys.exit(-1)
        else:
            
            ## Generate the pages
            options = GenerateFromImages(SRC)
            
            ## Generate the javascript
            GenerateJavascript(options)

    sys.exit(0)
