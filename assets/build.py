#!/usr/bin/env python3

import argparse
from ast import arg
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

#SRC = "C:\\Users\\chris\\Temp\\bookreader\\in"
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
    shutil.copyfile("/bookreader/BookReaderDemo/demo-vendor-fullscreen.html", os.path.join(DST, "index.html"))


def JsonProperties(width, height, filepath):

    page = dict()
    page["width"] = int(width)
    page["height"] = int(height)
    page["uri"] = "pages/" + os.path.basename(filepath)

    return page

def GetStartStop(start: int, stop: int, page_count: int):

    if(start > page_count):
        print("Start page after the end of the document")
        sys.exit(-1)
    if(start > stop):
        print("Stop page must be >= Start page ")
        sys.exit(-1)

    return max(0, start), min(page_count, stop)



def GenerateFromEbbok(input_file: str, start_page: int, stop_page: int):
    # Code from https://www.thepythoncode.com/article/convert-pdf-files-to-images-in-python
    """Converts pdf to image and generates a file by page"""
 
    options = dict()
    data = []

    try:
        os.makedirs(os.path.join(DST, "pages"), exist_ok = True)
        # Open the document
        doc = fitz.open(input_file)
        start, stop = GetStartStop(start_page, stop_page, doc.page_count - 1)
        # Iterate throughout the pages
        for pgNr in range(start, stop + 1):

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


def GenerateFromImages(folder: str, start_page: int, stop_page: int):

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

        start, stop = GetStartStop(start_page, stop_page, len(images)-1)
        os.makedirs(os.path.join(DST, "pages"), exist_ok = True)
        for i in range(start, stop + 1):  
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



    ## Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--ebook', help='ebook file')
    parser.add_argument('--start', type=int, help='First page (counting from 0)')
    parser.add_argument('--stop', type=int, help='Last page (counting from 0)')
    args = parser.parse_args()
    ## Sanity
    start = 0
    stop  = sys.maxsize
    if(not args.start is None):
        start = args.start 
        if(start < 0):
            print("Start page must be >= 0")
    if(not args.stop is None):
        stop = args.stop 
        if(stop < 0):
            print("Stop page must be >= 0")

    # PDF
    if (not args.ebook is None):

        filepath = os.path.join(SRC, args.ebook)

        ## Sanity
        if not os.path.isfile(filepath) or not filepath.lower().endswith(('.pdf', '.xps', '.epub', '.cbz', '.fb2')):
            print("Cannot process {}: unsupported format.".format(filepath))
            sys.exit(-1)
    
        ## Convert PDF and generate pages
        options = GenerateFromEbbok(filepath, start, stop)
        
        ## Generate the javascript
        GenerateJavascript(options)


    # Folder of images
    if (args.ebook is None):
        if not os.path.isdir(SRC):
            print("No image in directory {}".format(SRC))
            print("You have to provide an image directory or an ebook file")
            sys.exit(-1)
        else:
            
            ## Generate the pages
            options = GenerateFromImages(SRC, start, stop)
            
            ## Generate the javascript
            GenerateJavascript(options)

    sys.exit(0)
